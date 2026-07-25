"""
app.py — Flask web application for Anganwadi Growth Monitoring

Run:
python app.py

Open:
http://127.0.0.1:5000
"""

import os
import sys
import sqlite3

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session
)

from datetime import date


# ============================================================
# CONFIGURATION
# ============================================================

BASE = os.path.dirname(__file__)

DB_PATH = os.environ.get(
    "DB_PATH",
    os.path.join(BASE, "anganwadi.db")
)

sys.path.insert(
    0,
    os.path.join(BASE, "ml")
)


# ============================================================
# FLASK APP
# ============================================================

app = Flask(__name__)

# Secret key for session
app.secret_key = "anganwadi-dev-key"

# Session will NOT be remembered after browser is closed
app.config["SESSION_PERMANENT"] = False
# ============================================================
# DATABASE HELPER
# ============================================================

def get_db():


    con = sqlite3.connect(DB_PATH)

    con.execute(
        "PRAGMA foreign_keys = ON"
    )

    con.row_factory = sqlite3.Row

    return con

   # ============================================================
# LOGIN PROTECTION
# ============================================================

@app.before_request
def require_login():

    # Routes that do not require login
    public_routes = [
        "login",
        "static"
    ]

    # Current endpoint
    endpoint = request.endpoint

    # Allow public routes
    if endpoint in public_routes:
        return

    # If endpoint is not available
    if endpoint is None:
        return

    # Check whether user is logged in
    if not session.get("logged_in"):

        return redirect(
            url_for("login")
        )
# ============================================================
# LOGIN
# ============================================================

@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    # If already logged in,
    # don't show login page again
    if session.get("logged_in"):

        return redirect(
            url_for("index")
        )


    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )


        # ====================================================
        # DEMO LOGIN
        # ====================================================

        if (
            username == "admin"
            and password == "admin123"
        ):

            # Clear old session data
            session.clear()


            # Create new login session
            session["logged_in"] = True

            session["username"] = username


            flash(
                "Login successful. Welcome Admin!",
                "success"
            )


            return redirect(
                url_for("index")
            )


        else:

            flash(
                "Invalid username or password.",
                "danger"
            )


    return render_template(
        "login.html"
    )


# ============================================================
# LOGOUT
# ============================================================

@app.route("/logout")
def logout():

    session.clear()

    flash(
        "You have been logged out successfully.",
        "success"
    )

    return redirect(
        url_for("login")
    )


# ============================================================
# DASHBOARD
# ============================================================

@app.route("/")
def index():

    # Login protection
    if not session.get("logged_in"):

        return redirect(
            url_for("login")
        )

    con = get_db()


    # Total children
    total_children = con.execute(
        """
        SELECT COUNT(*)
        FROM child
        """
    ).fetchone()[0]


    # Total centres
    total_centres = con.execute(
        """
        SELECT COUNT(*)
        FROM anganwadi_centre
        """
    ).fetchone()[0]


    # Open referrals
    open_referrals = con.execute(
        """
        SELECT COUNT(*)
        FROM referral
        WHERE resolved_on IS NULL
        """
    ).fetchone()[0]


    # Nutrition status
    status_counts = con.execute(
        """
        SELECT
            ns.status,
            COUNT(*) AS cnt

        FROM child c

        JOIN growth_measurement gm
            ON gm.child_id = c.child_id

        JOIN nutrition_status ns
            ON ns.measurement_id = gm.measurement_id

        WHERE gm.measured_on = (

            SELECT MAX(m.measured_on)

            FROM growth_measurement m

            WHERE m.child_id = c.child_id

        )

        GROUP BY ns.status
        """
    ).fetchall()


    status_map = {
        r["status"]: r["cnt"]
        for r in status_counts
    }


    # Weight loss count
    weight_loss = con.execute(
        """
        SELECT COUNT(*)
        FROM (

            SELECT c.child_id

            FROM child c

            JOIN growth_measurement curr
                ON curr.child_id = c.child_id

            JOIN growth_measurement prev
                ON prev.child_id = c.child_id

            WHERE curr.measured_on = (

                SELECT MAX(m.measured_on)

                FROM growth_measurement m

                WHERE m.child_id = c.child_id

            )

            AND prev.measured_on = (

                SELECT MAX(m.measured_on)

                FROM growth_measurement m

                WHERE m.child_id = c.child_id

                AND m.measured_on < curr.measured_on

            )

            AND curr.weight_kg < prev.weight_kg

        )
        """
    ).fetchone()[0]


    con.close()


    return render_template(
        "index.html",

        total_children=total_children,

        total_centres=total_centres,

        open_referrals=open_referrals,

        sam_count=status_map.get(
            "SAM",
            0
        ),

        mam_count=status_map.get(
            "MAM",
            0
        ),

        normal_count=status_map.get(
            "Normal",
            0
        ),

        weight_loss=weight_loss
    )
# ============================================================
# ADD CHILD
# ============================================================

@app.route(
    "/add-child",
    methods=["GET", "POST"]
)
def add_child():

    con = get_db()

    if request.method == "POST":

        # ====================================================
        # GET FORM DATA
        # ====================================================

        child_name = request.form.get(
            "child_name",
            ""
        ).strip()

        date_of_birth = request.form.get(
            "date_of_birth",
            ""
        ).strip()

        gender = request.form.get(
            "gender",
            ""
        ).strip()

        father_name = request.form.get(
            "father_name",
            ""
        ).strip()

        mother_name = request.form.get(
            "mother_name",
            ""
        ).strip()

        parent_contact = request.form.get(
            "parent_contact",
            ""
        ).strip()

        address = request.form.get(
            "address",
            ""
        ).strip()

        vaccination_status = request.form.get(
            "vaccination_status",
            ""
        ).strip()

        centre_id = request.form.get(
            "centre_id",
            ""
        ).strip()


        # ====================================================
        # VALIDATION
        # ====================================================

        if (
            not child_name
            or not date_of_birth
            or not gender
            or not centre_id
        ):

            flash(
                "Child name, date of birth, gender and centre are required.",
                "danger"
            )

        elif date_of_birth > date.today().isoformat():

            flash(
                "Date of birth cannot be in the future.",
                "danger"
            )

        elif not father_name and not mother_name:

            flash(
                "Please enter at least Father's Name or Mother's Name.",
                "danger"
            )

        else:

            try:

                # ====================================================
                # GUARDIAN NAME
                # ====================================================

                if father_name and mother_name:

                    guardian = (
                        father_name
                        + " / "
                        + mother_name
                    )

                elif father_name:

                    guardian = father_name

                else:

                    guardian = mother_name


                # ====================================================
                # ENROLLED DATE
                # ====================================================

                enrolled_on = date.today().isoformat()


                # ====================================================
                # INSERT CHILD
                # ====================================================

                con.execute(
                    """
                    INSERT INTO child
                    (
                        full_name,
                        guardian,
                        father_name,
                        mother_name,
                        parent_contact,
                        address,
                        vaccination_status,
                        sex,
                        date_of_birth,
                        enrolled_on,
                        centre_id
                    )

                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,

                    (
                        child_name,
                        guardian,
                        father_name,
                        mother_name,
                        parent_contact,
                        address,
                        vaccination_status,
                        gender,
                        date_of_birth,
                        enrolled_on,
                        int(centre_id)
                    )
                )


                # ====================================================
                # SAVE DATABASE
                # ====================================================

                con.commit()

                con.close()


                # ====================================================
                # SUCCESS MESSAGE
                # ====================================================

                flash(
                    "Child added successfully!",
                    "success"
                )


                return redirect(
                    url_for("children")
                )


            except sqlite3.IntegrityError as e:

                con.rollback()

                flash(
                    f"Database error: {e}",
                    "danger"
                )


            except Exception as e:

                con.rollback()

                flash(
                    f"Error adding child: {e}",
                    "danger"
                )


    # ============================================================
    # GET ALL ANGANWADI CENTRES
    # ============================================================

    centres = con.execute(
        """
        SELECT

            centre_id,

            name,

            village,

            district

        FROM anganwadi_centre

        ORDER BY name

        """
    ).fetchall()


    con.close()


    # ============================================================
    # SHOW ADD CHILD PAGE
    # ============================================================

    return render_template(
        "add_child.html",

        centres=centres,

        today=date.today().isoformat()
    )

# ============================================================
# ALL CHILDREN
# ============================================================

@app.route("/children")
def children():

    con = get_db()

    rows = con.execute(
        """
        SELECT

            c.child_id,

            c.full_name,

            c.guardian,

            c.sex,

            c.date_of_birth,

            c.enrolled_on,

            CAST(
                (
                    JULIANDAY('now')
                    -
                    JULIANDAY(c.date_of_birth)
                ) / 30.44
                AS INTEGER
            ) AS age_months,

            ac.name AS centre,

            gm.measured_on,

            gm.weight_kg,

            gm.height_cm,

            gm.muac_cm,

            ns.status,

            ns.waz_score

        FROM child c

        JOIN anganwadi_centre ac

            ON ac.centre_id = c.centre_id

        LEFT JOIN growth_measurement gm

            ON gm.child_id = c.child_id

            AND gm.measured_on = (

                SELECT MAX(m.measured_on)

                FROM growth_measurement m

                WHERE m.child_id = c.child_id

            )

        LEFT JOIN nutrition_status ns

            ON ns.measurement_id =
               gm.measurement_id

        ORDER BY
            c.child_id DESC

        """
    ).fetchall()

    con.close()

    return render_template(
        "children.html",
        children=rows
    )
# ============================================================
# CHILD DETAIL
# ============================================================

@app.route(
    "/child/<int:child_id>"
)
def child_detail(child_id):

    con = get_db()


    child = con.execute(
        """
        SELECT

            c.*,

            ac.name AS centre,

            CAST(
                (
                    JULIANDAY('now')
                    -
                    JULIANDAY(c.date_of_birth)
                ) / 30.44
                AS INTEGER
            ) AS age_months


        FROM child c


        JOIN anganwadi_centre ac

            ON ac.centre_id =
               c.centre_id


        WHERE c.child_id = ?

        """,
        (child_id,)
    ).fetchone()


    if not child:

        flash(
            "Child not found.",
            "danger"
        )

        con.close()

        return redirect(
            url_for("children")
        )


    # Measurement history
    history = con.execute(
        """
        SELECT

            gm.measured_on,

            gm.weight_kg,

            gm.height_cm,

            gm.muac_cm,

            ns.status,

            ns.waz_score,

            ROUND(

                gm.weight_kg

                -

                LAG(gm.weight_kg)
                OVER (
                    ORDER BY gm.measured_on
                ),

                2

            ) AS gain_kg


        FROM growth_measurement gm


        LEFT JOIN nutrition_status ns

            ON ns.measurement_id =
               gm.measurement_id


        WHERE gm.child_id = ?


        ORDER BY gm.measured_on

        """,
        (child_id,)
    ).fetchall()


    # Referrals
    referrals = con.execute(
        """
        SELECT

            r.*,

            w.full_name AS worker_name


        FROM referral r


        JOIN worker w

            ON w.worker_id =
               r.raised_by


        WHERE r.child_id = ?


        ORDER BY r.raised_on DESC

        """,
        (child_id,)
    ).fetchall()


    con.close()


    return render_template(
        "child_detail.html",

        child=child,

        history=history,

        referrals=referrals
    )


# ============================================================
# ALERTS
# ============================================================

@app.route("/alerts")
def alerts():

    con = get_db()


    # Weight loss
    weight_loss = con.execute(
        """
        SELECT

            c.child_id,

            c.full_name,

            c.sex,

            curr.measured_on
                AS latest_visit,

            curr.weight_kg
                AS latest_weight,

            prev.measured_on
                AS prev_visit,

            prev.weight_kg
                AS prev_weight,

            ROUND(
                curr.weight_kg
                -
                prev.weight_kg,
                2
            ) AS change_kg,

            ns.status


        FROM child c


        JOIN growth_measurement curr

            ON curr.child_id =
               c.child_id


        JOIN growth_measurement prev

            ON prev.child_id =
               c.child_id


        LEFT JOIN nutrition_status ns

            ON ns.measurement_id =
               curr.measurement_id


        WHERE curr.measured_on = (

            SELECT MAX(m.measured_on)

            FROM growth_measurement m

            WHERE m.child_id =
                  c.child_id

        )


        AND prev.measured_on = (

            SELECT MAX(m.measured_on)

            FROM growth_measurement m

            WHERE m.child_id =
                  c.child_id

            AND m.measured_on <
                curr.measured_on

        )


        AND curr.weight_kg <
            prev.weight_kg


        ORDER BY change_kg

        """
    ).fetchall()


    # No weight gain
    no_gain = con.execute(
        """
        SELECT

            c.child_id,

            c.full_name,

            ROUND(
                MAX(gm.weight_kg)
                -
                MIN(gm.weight_kg),
                2
            ) AS total_gain,

            COUNT(*) AS visits


        FROM child c


        JOIN (

            SELECT

                child_id,

                weight_kg,

                ROW_NUMBER()
                OVER (

                    PARTITION BY child_id

                    ORDER BY measured_on DESC

                ) rn


            FROM growth_measurement

        ) gm


        ON gm.child_id =
           c.child_id


        AND gm.rn <= 3


        GROUP BY c.child_id


        HAVING total_gain <= 0


        ORDER BY total_gain

        """
    ).fetchall()


    # SAM children
    sam_children = con.execute(
        """
        SELECT

            c.child_id,

            c.full_name,

            gm.measured_on,

            gm.weight_kg,

            gm.muac_cm,

            ns.waz_score


        FROM child c


        JOIN growth_measurement gm

            ON gm.child_id =
               c.child_id


        JOIN nutrition_status ns

            ON ns.measurement_id =
               gm.measurement_id


        WHERE ns.status = 'SAM'


        AND gm.measured_on = (

            SELECT MAX(m.measured_on)

            FROM growth_measurement m

            WHERE m.child_id =
                  c.child_id

        )


        ORDER BY ns.waz_score

        """
    ).fetchall()


    con.close()


    return render_template(
        "alerts.html",

        weight_loss=weight_loss,

        no_gain=no_gain,

        sam_children=sam_children
    )


# ============================================================
# REFERRALS
# ============================================================

@app.route("/referrals")
def referrals():

    con = get_db()


    # Open referrals
    open_refs = con.execute(
        """
        SELECT

            r.referral_id,

            c.full_name,

            c.child_id,

            w.full_name AS worker,

            r.raised_on,

            r.reason


        FROM referral r


        JOIN child c

            ON c.child_id =
               r.child_id


        JOIN worker w

            ON w.worker_id =
               r.raised_by


        WHERE r.resolved_on IS NULL


        ORDER BY r.raised_on

        """
    ).fetchall()


    # Closed referrals
    closed_refs = con.execute(
        """
        SELECT

            r.referral_id,

            c.full_name,

            w.full_name AS worker,

            r.raised_on,

            r.resolved_on,

            r.outcome


        FROM referral r


        JOIN child c

            ON c.child_id =
               r.child_id


        JOIN worker w

            ON w.worker_id =
               r.raised_by


        WHERE r.resolved_on IS NOT NULL


        ORDER BY r.resolved_on DESC

        """
    ).fetchall()


    con.close()


    return render_template(
        "referrals.html",

        open_refs=open_refs,

        closed_refs=closed_refs
    )


# ============================================================
# ADD REFERRAL
# ============================================================

@app.route(
    "/referrals/add",
    methods=["GET", "POST"]
)
def add_referral():

    con = get_db()


    if request.method == "POST":

        child_id = request.form[
            "child_id"
        ]

        worker_id = request.form[
            "worker_id"
        ]

        reason = request.form[
            "reason"
        ].strip()

        raised_on = request.form[
            "raised_on"
        ]


        if raised_on > date.today().isoformat():

            flash(
                "Referral date cannot be in the future.",
                "danger"
            )


        elif not reason:

            flash(
                "Reason is required.",
                "danger"
            )


        else:

            con.execute(
                """
                INSERT INTO referral
                (
                    child_id,
                    raised_by,
                    raised_on,
                    reason
                )

                VALUES (?, ?, ?, ?)
                """,

                (
                    child_id,
                    worker_id,
                    raised_on,
                    reason
                )
            )


            con.commit()

            con.close()


            flash(
                "Referral created successfully.",
                "success"
            )


            return redirect(
                url_for("referrals")
            )


    children = con.execute(
        """
        SELECT

            child_id,

            full_name


        FROM child


        ORDER BY full_name

        """
    ).fetchall()


    workers = con.execute(
        """
        SELECT

            worker_id,

            full_name


        FROM worker


        WHERE active = 1


        ORDER BY full_name

        """
    ).fetchall()


    con.close()


    return render_template(
        "add_referral.html",

        children=children,

        workers=workers,

        today=date.today().isoformat()
    )


# ============================================================
# ML PREDICTION
# ============================================================

@app.route(
    "/predict",
    methods=["GET", "POST"]
)
def predict():

    result = None

    error = None

    form = {}


    if request.method == "POST":

        try:

            form = request.form.to_dict()


            features = {

                "age_months":
                    float(
                        form["age_months"]
                    ),

                "sex":
                    1
                    if form["sex"] == "M"
                    else 0,

                "weight_curr":
                    float(
                        form["weight_curr"]
                    ),

                "weight_prev1":
                    float(
                        form["weight_prev1"]
                    ),

                "weight_prev2":
                    float(
                        form["weight_prev2"]
                    ),

                "muac_cm":
                    float(
                        form["muac_cm"]
                    ),

                "waz_score":
                    float(
                        form["waz_score"]
                    ),

                "weight_slope":
                    float(
                        form["weight_curr"]
                    )
                    -
                    float(
                        form["weight_prev1"]
                    ),

                "consecutive_no_gain":
                    int(
                        form[
                            "consecutive_no_gain"
                        ]
                    )
            }


            model_path = os.path.join(
                BASE,
                "ml",
                "model.pkl"
            )


            if not os.path.exists(
                model_path
            ):

                error = (
                    "Model not found. "
                    "Please run init_db.py first."
                )


            else:

                from train import predict_single


                pred, conf = predict_single(
                    features,
                    model_path
                )


                result = {

                    "prediction":
                        pred,

                    "confidence":
                        round(
                            conf * 100,
                            1
                        ),

                    "label":
                        "NEEDS REFERRAL"
                        if pred == 1

                        else
                        (
                            "No referral needed"
                            if pred == 0
                            else None
                        ),

                    "color":
                        "danger"
                        if pred == 1

                        else
                        (
                            "success"
                            if pred == 0

                            else "warning"
                        )
                }


        except Exception as e:

            error = (
                f"Prediction error: {e}"
            )


    return render_template(
        "predict.html",

        result=result,

        error=error,

        form=form
    )


# ============================================================
# ADD MEASUREMENT
# ============================================================

@app.route(
    "/add-measurement",
    methods=["GET", "POST"]
)
def add_measurement():

    con = get_db()

    if request.method == "POST":

        try:

            # ====================================================
            # GET FORM DATA
            # ====================================================

            child_id = int(
                request.form.get(
                    "child_id",
                    0
                )
            )

            worker_id = int(
                request.form.get(
                    "worker_id",
                    0
                )
            )

            measured_on = request.form.get(
                "measured_on",
                ""
            ).strip()

            weight_kg = float(
                request.form.get(
                    "weight_kg",
                    0
                )
            )

            height_cm = (
                request.form.get(
                    "height_cm",
                    ""
                ).strip()
                or None
            )

            muac_cm = (
                request.form.get(
                    "muac_cm",
                    ""
                ).strip()
                or None
            )

            notes = (
                request.form.get(
                    "notes",
                    ""
                ).strip()
                or None
            )


            # ====================================================
            # VALIDATION
            # ====================================================

            if not child_id:

                flash(
                    "Please select a child.",
                    "danger"
                )

            elif not worker_id:

                flash(
                    "Please select the worker.",
                    "danger"
                )

            elif not measured_on:

                flash(
                    "Measurement date is required.",
                    "danger"
                )

            elif measured_on > date.today().isoformat():

                flash(
                    "Measurement date cannot be in the future.",
                    "danger"
                )

            elif weight_kg <= 0:

                flash(
                    "Weight must be greater than 0.",
                    "danger"
                )

            elif weight_kg > 99:

                flash(
                    "Please enter a valid weight.",
                    "danger"
                )

            else:

                # ====================================================
                # CONVERT OPTIONAL VALUES
                # ====================================================

                if height_cm:

                    height_cm = float(
                        height_cm
                    )

                    if (
                        height_cm <= 0
                        or height_cm > 199
                    ):

                        flash(
                            "Please enter a valid height.",
                            "danger"
                        )

                        con.close()

                        return redirect(
                            request.url
                        )


                if muac_cm:

                    muac_cm = float(
                        muac_cm
                    )

                    if (
                        muac_cm <= 0
                        or muac_cm > 49
                    ):

                        flash(
                            "Please enter a valid MUAC value.",
                            "danger"
                        )

                        con.close()

                        return redirect(
                            request.url
                        )


                # ====================================================
                # CHECK DUPLICATE MEASUREMENT
                # ====================================================

                existing = con.execute(
                    """
                    SELECT measurement_id

                    FROM growth_measurement

                    WHERE child_id = ?

                    AND measured_on = ?

                    """,
                    (
                        child_id,
                        measured_on
                    )
                ).fetchone()


                if existing:

                    flash(
                        "A measurement already exists for this child on this date.",
                        "warning"
                    )

                else:

                    # ====================================================
                    # INSERT GROWTH MEASUREMENT
                    # ====================================================

                    cur = con.execute(
                        """
                        INSERT INTO growth_measurement
                        (
                            child_id,
                            worker_id,
                            measured_on,
                            weight_kg,
                            height_cm,
                            muac_cm,
                            notes
                        )

                        VALUES (?, ?, ?, ?, ?, ?, ?)
                        """,

                        (
                            child_id,
                            worker_id,
                            measured_on,
                            weight_kg,
                            height_cm,
                            muac_cm,
                            notes
                        )
                    )


                    measurement_id = cur.lastrowid


                    # ====================================================
                    # CALCULATE NUTRITION STATUS
                    # ====================================================

                    if muac_cm is None:

                        status = "Normal"

                        waz_score = None


                    elif muac_cm < 11.5:

                        status = "SAM"

                        waz_score = None


                    elif muac_cm < 12.5:

                        status = "MAM"

                        waz_score = None


                    else:

                        status = "Normal"

                        waz_score = None


                    # ====================================================
                    # INSERT NUTRITION STATUS
                    # ====================================================

                    con.execute(
                        """
                        INSERT INTO nutrition_status
                        (
                            measurement_id,
                            status,
                            waz_score,
                            determined_by
                        )

                        VALUES (?, ?, ?, ?)
                        """,

                        (
                            measurement_id,
                            status,
                            waz_score,
                            "system"
                        )
                    )


                    # ====================================================
                    # COMMIT DATABASE
                    # ====================================================

                    con.commit()

                    con.close()


                    # ====================================================
                    # SUCCESS MESSAGE
                    # ====================================================

                    flash(
                        f"Measurement recorded successfully! Nutrition Status: {status}",
                        "success"
                    )


                    return redirect(
                        url_for(
                            "child_detail",
                            child_id=child_id
                        )
                    )


        except sqlite3.IntegrityError as e:

            con.rollback()

            flash(
                f"Database error: {e}",
                "danger"
            )


        except ValueError:

            con.rollback()

            flash(
                "Please enter valid numeric values.",
                "danger"
            )


        except Exception as e:

            con.rollback()

            flash(
                f"Error recording measurement: {e}",
                "danger"
            )


    # ============================================================
    # GET ALL CHILDREN
    # ============================================================

    children = con.execute(
        """
        SELECT

            child_id,

            full_name

        FROM child

        ORDER BY full_name

        """
    ).fetchall()


    # ============================================================
    # GET ALL ACTIVE WORKERS
    # ============================================================

    workers = con.execute(
        """
        SELECT

            worker_id,

            full_name

        FROM worker

        WHERE active = 1

        ORDER BY full_name

        """
    ).fetchall()


    con.close()


    # ============================================================
    # SHOW MEASUREMENT PAGE
    # ============================================================

    return render_template(
        "add_measurement.html",

        children=children,

        workers=workers,

        today=date.today().isoformat()
    )
# ============================================================
# ADD CENTRE
# ============================================================

@app.route(
    "/centres/add",
    methods=["GET", "POST"]
)
def add_centre():

    con = get_db()


    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()


        village = request.form.get(
            "village",
            ""
        ).strip()


        district = request.form.get(
            "district",
            ""
        ).strip()


        if (
            not name
            or not village
            or not district
        ):

            flash(
                "All fields are required.",
                "danger"
            )


        else:

            try:

                con.execute(
                    """
                    INSERT INTO
                    anganwadi_centre

                    (
                        name,
                        village,
                        district
                    )

                    VALUES (?, ?, ?)
                    """,

                    (
                        name,
                        village,
                        district
                    )
                )


                con.commit()

                con.close()


                flash(
                    "Anganwadi Centre added successfully!",
                    "success"
                )


                return redirect(
                    url_for("centres")
                )


            except sqlite3.IntegrityError as e:

                flash(
                    f"Database error: {e}",
                    "danger"
                )


    con.close()


    return render_template(
        "add_centre.html"
    )


# ============================================================
# CENTRE SUMMARY
# ============================================================

@app.route("/centres")
def centres():

    con = get_db()


    rows = con.execute(
        """
        SELECT

            ac.centre_id,

            ac.name,

            ac.village,

            ac.district,


            COUNT(
                DISTINCT c.child_id
            ) AS total_children,


            COALESCE(

                SUM(

                    CASE

                        WHEN ns.status = 'SAM'

                        THEN 1

                        ELSE 0

                    END

                ),

                0

            ) AS sam,


            COALESCE(

                SUM(

                    CASE

                        WHEN ns.status = 'MAM'

                        THEN 1

                        ELSE 0

                    END

                ),

                0

            ) AS mam,


            COALESCE(

                SUM(

                    CASE

                        WHEN ns.status = 'Normal'

                        THEN 1

                        ELSE 0

                    END

                ),

                0

            ) AS normal


        FROM anganwadi_centre ac


        LEFT JOIN child c

            ON c.centre_id =
               ac.centre_id


        LEFT JOIN growth_measurement gm

            ON gm.child_id =
               c.child_id

            AND gm.measured_on = (

                SELECT MAX(m.measured_on)

                FROM growth_measurement m

                WHERE m.child_id =
                      c.child_id

            )


        LEFT JOIN nutrition_status ns

            ON ns.measurement_id =
               gm.measurement_id


        GROUP BY

            ac.centre_id,

            ac.name,

            ac.village,

            ac.district


        ORDER BY ac.name

        """
    ).fetchall()


    con.close()


    return render_template(
        "centres.html",

        centres=rows
    )


# ============================================================
# VIEW CHILDREN IN A CENTRE
# ============================================================

@app.route(
    "/centre/<int:centre_id>/children"
)
def centre_children(centre_id):

    con = get_db()


    # Get Centre
    centre = con.execute(
        """
        SELECT

            centre_id,

            name,

            village,

            district


        FROM anganwadi_centre


        WHERE centre_id = ?

        """,
        (centre_id,)
    ).fetchone()


    if not centre:

        flash(
            "Centre not found.",
            "danger"
        )

        con.close()


        return redirect(
            url_for("centres")
        )


    # Get Children
    children = con.execute(
        """
        SELECT

            c.child_id,

            c.full_name,

            c.sex,


            CAST(

                (

                    JULIANDAY('now')

                    -

                    JULIANDAY(
                        c.date_of_birth
                    )

                ) / 30.44

                AS INTEGER

            ) AS age_months,


            gm.measured_on,

            gm.weight_kg,

            gm.muac_cm,


            ns.status,

            ns.waz_score


        FROM child c


        LEFT JOIN growth_measurement gm

            ON gm.child_id =
               c.child_id


            AND gm.measured_on = (

                SELECT MAX(m.measured_on)

                FROM growth_measurement m

                WHERE m.child_id =
                      c.child_id

            )


        LEFT JOIN nutrition_status ns

            ON ns.measurement_id =
               gm.measurement_id


        WHERE c.centre_id = ?


        ORDER BY c.full_name

        """,
        (centre_id,)
    ).fetchall()


    con.close()


    return render_template(
        "centre_children.html",

        centre=centre,

        children=children
    )


# ============================================================
# RUN APPLICATION
# ============================================================

if __name__ == "__main__":

    if not os.path.exists(
        DB_PATH
    ):

        print(
            "Database not found."
        )

        print(
            "Running init_db.py first..."
        )


        import init_db


        init_db.init()


    app.run(
        debug=True,
        host="0.0.0.0",
        port=5000
    )