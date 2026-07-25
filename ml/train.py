"""
Task 2 — Prediction Model
Target: Will this child need a referral within the next 2 visits?
Features used at prediction time (no future data leakage):
  - age_months
  - sex (encoded)
  - last 3 weight measurements (current, prev-1, prev-2)
  - muac_cm (latest)
  - weight trend (slope over last 3 visits)
  - consecutive_no_gain count
  - current waz_score
"""

import os
import sqlite3
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import joblib

DB_PATH = os.environ.get("DB_PATH", os.path.join(os.path.dirname(__file__), "..", "anganwadi.db"))
MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.pkl")

CONFIDENCE_THRESHOLD = 0.40   # below this → no forced prediction (relaxed for small dataset)


def load_features(db_path: str) -> pd.DataFrame:
    con = sqlite3.connect(db_path)

    # Pull all measurements with status and child info
    df = pd.read_sql_query("""
        SELECT
            c.child_id,
            c.sex,
            CAST((JULIANDAY(gm.measured_on) - JULIANDAY(c.date_of_birth)) / 30.44 AS INTEGER) AS age_months,
            gm.measurement_id,
            gm.measured_on,
            gm.weight_kg,
            gm.muac_cm,
            ns.waz_score,
            ns.status,
            CASE WHEN EXISTS (
                SELECT 1 FROM referral r
                WHERE r.child_id = c.child_id
                  AND r.raised_on > gm.measured_on
                  AND JULIANDAY(r.raised_on) - JULIANDAY(gm.measured_on) <= 90
            ) THEN 1 ELSE 0 END AS referred_within_3m
        FROM child c
        JOIN growth_measurement gm ON gm.child_id = c.child_id
        JOIN nutrition_status   ns ON ns.measurement_id = gm.measurement_id
        ORDER BY c.child_id, gm.measured_on
    """, con)
    con.close()
    return df


def build_feature_rows(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for child_id, grp in df.groupby("child_id"):
        grp = grp.sort_values("measured_on").reset_index(drop=True)
        sex_enc = 1 if grp["sex"].iloc[0] == "M" else 0

        for i in range(2, len(grp)):   # need at least 3 rows
            curr  = grp.iloc[i]
            prev1 = grp.iloc[i - 1]
            prev2 = grp.iloc[i - 2]

            weights = [prev2["weight_kg"], prev1["weight_kg"], curr["weight_kg"]]
            slope = np.polyfit([0, 1, 2], weights, 1)[0]   # weight trend

            no_gain = sum(1 for j in range(1, i + 1)
                          if grp.iloc[j]["weight_kg"] <= grp.iloc[j - 1]["weight_kg"])

            rows.append({
                "child_id":          child_id,
                "age_months":        curr["age_months"],
                "sex":               sex_enc,
                "weight_curr":       curr["weight_kg"],
                "weight_prev1":      prev1["weight_kg"],
                "weight_prev2":      prev2["weight_kg"],
                "muac_cm":           curr["muac_cm"] if curr["muac_cm"] else 13.0,
                "waz_score":         curr["waz_score"] if curr["waz_score"] else -1.0,
                "weight_slope":      slope,
                "consecutive_no_gain": no_gain,
                "label":             curr["referred_within_3m"],
            })
    return pd.DataFrame(rows)


FEATURE_COLS = [
    "age_months", "sex", "weight_curr", "weight_prev1", "weight_prev2",
    "muac_cm", "waz_score", "weight_slope", "consecutive_no_gain"
]


def augment_with_synthetics(data: pd.DataFrame, n_positive: int = 30, n_negative: int = 30) -> pd.DataFrame:
    """
    Augment tiny seed dataset with clearly labelled synthetic rows so the
    classifier has enough signal to learn.  All feature values are within
    realistic clinical ranges.
    """
    rng = np.random.default_rng(42)

    pos_rows = []
    for _ in range(n_positive):
        w = rng.uniform(4.0, 6.5)
        pos_rows.append({
            "child_id": -1, "age_months": int(rng.integers(12, 36)),
            "sex": int(rng.integers(0, 2)),
            "weight_curr":  round(w - rng.uniform(0.1, 0.4), 2),
            "weight_prev1": round(w, 2),
            "weight_prev2": round(w + rng.uniform(0.0, 0.3), 2),
            "muac_cm":      round(rng.uniform(9.5, 11.4), 1),
            "waz_score":    round(rng.uniform(-4.5, -3.0), 2),
            "weight_slope": round(rng.uniform(-0.35, -0.05), 3),
            "consecutive_no_gain": int(rng.integers(3, 6)),
            "label": 1,
        })

    neg_rows = []
    for _ in range(n_negative):
        w = rng.uniform(7.0, 12.0)
        neg_rows.append({
            "child_id": -1, "age_months": int(rng.integers(12, 60)),
            "sex": int(rng.integers(0, 2)),
            "weight_curr":  round(w + rng.uniform(0.1, 0.5), 2),
            "weight_prev1": round(w, 2),
            "weight_prev2": round(w - rng.uniform(0.0, 0.2), 2),
            "muac_cm":      round(rng.uniform(13.0, 16.0), 1),
            "waz_score":    round(rng.uniform(-1.5, 0.5), 2),
            "weight_slope": round(rng.uniform(0.05, 0.40), 3),
            "consecutive_no_gain": int(rng.integers(0, 2)),
            "label": 0,
        })

    synth = pd.DataFrame(pos_rows + neg_rows)
    combined = pd.concat([data, synth], ignore_index=True)
    print(f"[train] After augmentation: {len(combined)} rows  (seed: {len(data)}, synthetic: {len(synth)})")
    return combined


def train(db_path: str = DB_PATH):
    print(f"[train] Loading data from {db_path}")
    raw = load_features(db_path)
    data = build_feature_rows(raw)

    if data.empty:
        raise RuntimeError("No feature rows built — check the database has enough measurements.")

    data = augment_with_synthetics(data)

    X = data[FEATURE_COLS].values
    y = data["label"].values

    print(f"[train] Final dataset: {len(data)} rows  |  positive (referred): {int(y.sum())}")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y if y.sum() >= 2 else None
    )

    clf = RandomForestClassifier(n_estimators=100, max_depth=6, random_state=42, class_weight="balanced")
    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_test)
    print("\n[train] Classification Report:")
    print(classification_report(y_test, y_pred, target_names=["No Referral", "Needs Referral"], zero_division=0))
    print("[train] Confusion Matrix:")
    print(confusion_matrix(y_test, y_pred))

    joblib.dump(clf, MODEL_PATH)
    print(f"\n[train] Model saved → {MODEL_PATH}")
    return clf


def predict_single(features: dict, model_path: str = MODEL_PATH):
    """
    Predict for one child at inference time.
    features: dict with keys matching FEATURE_COLS
    Returns (prediction, confidence) or (None, confidence) if below threshold.
    """
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model not found at {model_path}. Run train() first.")

    clf = joblib.load(model_path)
    row = np.array([[features[col] for col in FEATURE_COLS]])
    proba = clf.predict_proba(row)[0]
    confidence = float(proba[1])   # probability of "needs referral"

    if confidence < CONFIDENCE_THRESHOLD:
        print(f"[predict] Low confidence ({confidence:.2f}) — no forced prediction.")
        return None, confidence

    prediction = int(clf.predict(row)[0])
    return prediction, confidence


if __name__ == "__main__":
    train()
