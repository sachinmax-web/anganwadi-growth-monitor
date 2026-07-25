-- =============================================================
-- Anganwadi Child Nutrition & Growth Monitoring
-- Task 4: Schema with full constraints (SQLite)
-- Note: SQLite does not allow non-deterministic functions like
--       DATE('now') in CHECK constraints, so date-in-future
--       validation is enforced in application code (main.py).
-- =============================================================

PRAGMA foreign_keys = ON;

-- ── Centre ────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS anganwadi_centre (
    centre_id  INTEGER PRIMARY KEY AUTOINCREMENT,
    name       TEXT NOT NULL,
    village    TEXT NOT NULL,
    district   TEXT NOT NULL,
    state      TEXT NOT NULL DEFAULT 'Tamil Nadu',
    created_at TEXT NOT NULL DEFAULT (DATE('now'))
);

-- ── Worker ────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS worker (
    worker_id  INTEGER PRIMARY KEY AUTOINCREMENT,
    centre_id  INTEGER NOT NULL REFERENCES anganwadi_centre(centre_id),
    full_name  TEXT    NOT NULL,
    phone      TEXT,
    active     INTEGER NOT NULL DEFAULT 1 CHECK (active IN (0,1)),
    joined_on  TEXT    NOT NULL
);

-- ── Child ─────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS child (
    child_id           INTEGER PRIMARY KEY AUTOINCREMENT,
    centre_id          INTEGER NOT NULL REFERENCES anganwadi_centre(centre_id),
    full_name          TEXT NOT NULL,
    date_of_birth      TEXT NOT NULL,
    sex                TEXT NOT NULL CHECK (sex IN ('M','F')),

    father_name        TEXT,
    mother_name        TEXT,
    parent_contact     TEXT,
    address            TEXT,
    vaccination_status TEXT,

    guardian           TEXT NOT NULL,
    enrolled_on        TEXT NOT NULL
);
-- ── Growth Measurement (history — never overwritten) ──────────
CREATE TABLE IF NOT EXISTS growth_measurement (
    measurement_id INTEGER PRIMARY KEY AUTOINCREMENT,
    child_id       INTEGER NOT NULL REFERENCES child(child_id),
    worker_id      INTEGER NOT NULL REFERENCES worker(worker_id),
    measured_on    TEXT    NOT NULL,
    weight_kg      REAL    NOT NULL CHECK (weight_kg > 0 AND weight_kg < 100),
    height_cm      REAL             CHECK (height_cm IS NULL OR (height_cm > 0 AND height_cm < 200)),
    muac_cm        REAL             CHECK (muac_cm IS NULL OR (muac_cm > 0 AND muac_cm < 50)),
    notes          TEXT,
    UNIQUE (child_id, measured_on)   -- same child cannot be measured twice on the same day
);

-- ── Nutrition Status (derived, stored for audit) ──────────────
CREATE TABLE IF NOT EXISTS nutrition_status (
    status_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    measurement_id INTEGER NOT NULL UNIQUE REFERENCES growth_measurement(measurement_id),
    status         TEXT    NOT NULL CHECK (status IN ('Normal','MAM','SAM')),
    waz_score      REAL,
    determined_by  TEXT    NOT NULL DEFAULT 'system' CHECK (determined_by IN ('system','worker')),
    determined_at  TEXT    NOT NULL DEFAULT (DATETIME('now'))
);

-- ── Referral ──────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS referral (
    referral_id INTEGER PRIMARY KEY AUTOINCREMENT,
    child_id    INTEGER NOT NULL REFERENCES child(child_id),
    raised_by   INTEGER NOT NULL REFERENCES worker(worker_id),
    raised_on   TEXT    NOT NULL,
    reason      TEXT    NOT NULL,
    resolved_on TEXT,
    outcome     TEXT,
    CHECK (resolved_on IS NULL OR resolved_on >= raised_on)
);
