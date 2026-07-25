-- =============================================================
-- Task 5 Queries — actionable reports for anganwadi worker
-- Run against: anganwadi.db
-- =============================================================
PRAGMA foreign_keys = ON;

-- ── Q1: Children who LOST weight in the most recent visit ─────
SELECT
    c.child_id,
    c.full_name,
    c.sex,
    curr.measured_on        AS latest_visit,
    curr.weight_kg          AS latest_weight,
    prev.measured_on        AS previous_visit,
    prev.weight_kg          AS previous_weight,
    ROUND(curr.weight_kg - prev.weight_kg, 2) AS weight_change_kg
FROM child c
JOIN growth_measurement curr
    ON curr.child_id = c.child_id
JOIN growth_measurement prev
    ON prev.child_id = c.child_id
WHERE curr.measured_on = (
        SELECT MAX(m2.measured_on) FROM growth_measurement m2
        WHERE m2.child_id = c.child_id)
  AND prev.measured_on = (
        SELECT MAX(m3.measured_on) FROM growth_measurement m3
        WHERE m3.child_id = c.child_id
          AND m3.measured_on < curr.measured_on)
  AND curr.weight_kg < prev.weight_kg
ORDER BY weight_change_kg ASC;

-- ── Q2: Children with NO weight gain across last 3 visits ─────
SELECT
    c.child_id,
    c.full_name,
    COUNT(gm.measurement_id) AS visits_checked,
    MIN(gm.weight_kg)        AS min_weight,
    MAX(gm.weight_kg)        AS max_weight,
    ROUND(MAX(gm.weight_kg) - MIN(gm.weight_kg), 2) AS total_gain_kg
FROM child c
JOIN (
    SELECT child_id, measurement_id, weight_kg, measured_on,
           ROW_NUMBER() OVER (PARTITION BY child_id ORDER BY measured_on DESC) AS rn
    FROM growth_measurement
) gm ON gm.child_id = c.child_id AND gm.rn <= 3
GROUP BY c.child_id, c.full_name
HAVING total_gain_kg <= 0
ORDER BY total_gain_kg ASC;

-- ── Q3: Current nutrition status of every child ───────────────
SELECT
    c.child_id,
    c.full_name,
    c.sex,
    CAST((JULIANDAY(DATE('now')) - JULIANDAY(c.date_of_birth)) / 30.44 AS INTEGER) AS age_months,
    gm.measured_on,
    gm.weight_kg,
    gm.muac_cm,
    ns.status,
    ns.waz_score
FROM child c
JOIN growth_measurement gm ON gm.child_id = c.child_id
JOIN nutrition_status ns   ON ns.measurement_id = gm.measurement_id
WHERE gm.measured_on = (
    SELECT MAX(m.measured_on) FROM growth_measurement m WHERE m.child_id = c.child_id)
ORDER BY ns.status DESC, ns.waz_score ASC;

-- ── Q4: Full growth history for a specific child (child_id=2) ─
SELECT
    gm.measured_on,
    gm.weight_kg,
    gm.height_cm,
    gm.muac_cm,
    ns.status,
    ns.waz_score,
    ROUND(gm.weight_kg -
        LAG(gm.weight_kg) OVER (PARTITION BY gm.child_id ORDER BY gm.measured_on), 2)
        AS month_gain_kg
FROM growth_measurement gm
JOIN nutrition_status ns ON ns.measurement_id = gm.measurement_id
WHERE gm.child_id = 2
ORDER BY gm.measured_on;

-- ── Q5: Open referrals (not yet resolved) ─────────────────────
SELECT
    r.referral_id,
    c.full_name   AS child_name,
    w.full_name   AS raised_by_worker,
    r.raised_on,
    r.reason
FROM referral r
JOIN child  c ON c.child_id  = r.child_id
JOIN worker w ON w.worker_id = r.raised_by
WHERE r.resolved_on IS NULL
ORDER BY r.raised_on;

-- ── Q6: Centre-level summary (SAM/MAM counts) ─────────────────
SELECT
    ac.name         AS centre,
    ns.status,
    COUNT(*)        AS children_count
FROM child c
JOIN anganwadi_centre ac ON ac.centre_id = c.centre_id
JOIN growth_measurement gm ON gm.child_id = c.child_id
JOIN nutrition_status   ns ON ns.measurement_id = gm.measurement_id
WHERE gm.measured_on = (
    SELECT MAX(m.measured_on) FROM growth_measurement m WHERE m.child_id = c.child_id)
GROUP BY ac.name, ns.status
ORDER BY ac.name, ns.status;
