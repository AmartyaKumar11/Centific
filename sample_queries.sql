-- ============================================================
-- SAMPLE QUERIES — Simulate API Calls via PostgreSQL
-- ============================================================

-- ============================================================
-- 1. KYC API CALL — Fetch identity details for a borrower
-- ============================================================
SELECT
    k.pan_number,
    k.applicant_name,
    k.aadhaar_number,
    k.date_of_birth,
    k.email,
    k.phone_number,
    k.address,
    k.employer_name,
    k.employer_type,
    k.employment_tenure_years,
    k.data_consistency_flag
FROM kyc_api_table k
WHERE k.pan_number = 'CRJKW0660X';


-- ============================================================
-- 2. CIBIL API CALL — Fetch credit bureau score for a borrower
-- ============================================================
SELECT
    c.pan_number,
    c.cibil_score,
    c.default_flag,
    c.written_off_flag,
    c.credit_enquiries_6m,
    c.negative_items_count,
    c.oldest_account_years,
    c.accounts_good_standing,
    c.derogatory_marks,
    CASE
        WHEN c.cibil_score >= 750 THEN 'EXCELLENT'
        WHEN c.cibil_score >= 700 THEN 'GOOD'
        WHEN c.cibil_score >= 620 THEN 'FAIR'
        ELSE 'POOR'
    END AS cibil_band
FROM cibil_api_table c
WHERE c.pan_number = 'CRJKW0660X';


-- ============================================================
-- 3. BANK API CALL — Fetch banking behaviour for a borrower
-- ============================================================
SELECT
    b.pan_number,
    b.bank_balance,
    b.bounce_count,
    b.statement_months,
    b.spending_ratio,
    b.negative_month_count,
    b.existing_emi_total,
    CASE
        WHEN b.bounce_count = 0 AND b.spending_ratio < 0.5 THEN 'HEALTHY'
        WHEN b.bounce_count <= 2 AND b.spending_ratio < 0.7 THEN 'MODERATE'
        ELSE 'STRESSED'
    END AS banking_health
FROM bank_api_table b
WHERE b.pan_number = 'CRJKW0660X';


-- ============================================================
-- 4. INCOME API CALL — Fetch income verification for a borrower
-- ============================================================
SELECT
    i.pan_number,
    i.gross_salary,
    i.total_deductions,
    i.declared_income,
    i.verified_income,
    i.income_mismatch_flag,
    i.income_stability,
    (i.declared_income - i.verified_income) AS income_delta
FROM income_api_table i
WHERE i.pan_number = 'CRJKW0660X';


-- ============================================================
-- 5. DOCUMENT ANALYSIS API CALL — Fetch OCR and consistency
-- ============================================================
SELECT
    d.pan_number,
    d.ocr_confidence_score,
    d.document_consistency_flag,
    d.data_consistency_flag,
    CASE
        WHEN d.ocr_confidence_score >= 90 THEN 'HIGH'
        WHEN d.ocr_confidence_score >= 75 THEN 'MEDIUM'
        ELSE 'LOW'
    END AS ocr_band
FROM document_analysis_table d
WHERE d.pan_number = 'CRJKW0660X';


-- ============================================================
-- 6. DECISION ENGINE OUTPUT — Fetch final decision for an app
-- ============================================================
SELECT
    de.application_id,
    de.pan_number,
    de.decision,
    de.risk_category,
    de.decision_reason_codes,
    de.confidence_score,
    de.hil_required_flag,
    de.interest_rate,
    de.proposed_emi,
    ROUND(de.dti_ratio * 100, 2) AS dti_percent
FROM decision_engine_output de
WHERE de.application_id = 'APP-2026-00001';


-- ============================================================
-- 7. APPLICATION TIMELINE — Full agent reasoning trace
-- ============================================================
SELECT
    t.step_order,
    t.step_name,
    t.step_status,
    t.triggered_by,
    t.output_data,
    t.created_at
FROM application_timeline t
WHERE t.application_id = 'APP-2026-00001'
ORDER BY t.step_order ASC;


-- ============================================================
-- 8. FULL APPLICATION VIEW — Join all tables for one borrower
-- ============================================================
SELECT
    a.application_id,
    a.applicant_name,
    a.pan_number,
    a.requested_loan_amount,
    a.requested_tenure_months,
    a.decision,
    a.risk_category,
    a.confidence_score,
    a.hil_required_flag,
    -- KYC
    k.employer_name,
    k.employer_type,
    k.employment_tenure_years,
    -- CIBIL
    c.cibil_score,
    c.default_flag,
    c.credit_enquiries_6m,
    -- BANK
    b.bank_balance,
    b.bounce_count,
    b.spending_ratio,
    -- INCOME
    i.declared_income,
    i.verified_income,
    i.income_mismatch_flag,
    i.income_stability,
    -- DOCUMENTS
    d.ocr_confidence_score,
    d.document_consistency_flag,
    -- DECISION
    de.interest_rate,
    de.proposed_emi,
    ROUND(de.dti_ratio * 100, 2) AS dti_percent
FROM applications a
JOIN kyc_api_table          k  ON k.application_id  = a.application_id
JOIN cibil_api_table        c  ON c.application_id  = a.application_id
JOIN bank_api_table         b  ON b.application_id  = a.application_id
JOIN income_api_table       i  ON i.application_id  = a.application_id
JOIN document_analysis_table d ON d.application_id  = a.application_id
JOIN decision_engine_output de ON de.application_id = a.application_id
WHERE a.application_id = 'APP-2026-00001';


-- ============================================================
-- 9. HIL QUEUE — All applications requiring human review
-- ============================================================
SELECT
    a.application_id,
    a.applicant_name,
    a.requested_loan_amount,
    a.risk_category,
    a.confidence_score,
    de.dti_ratio,
    c.cibil_score,
    de.decision_reason_codes,
    a.application_date
FROM applications a
JOIN decision_engine_output de ON de.application_id = a.application_id
JOIN cibil_api_table        c  ON c.application_id  = a.application_id
WHERE a.hil_required_flag = TRUE
ORDER BY a.risk_category DESC, a.confidence_score ASC;


-- ============================================================
-- 10. REJECTION ANALYSIS — Top rejection reason breakdown
-- ============================================================
SELECT
    reason_code,
    COUNT(*) AS count
FROM (
    SELECT
        UNNEST(STRING_TO_ARRAY(decision_reason_codes, '|')) AS reason_code
    FROM decision_engine_output
    WHERE decision = 'REJECTED'
) sub
GROUP BY reason_code
ORDER BY count DESC;


-- ============================================================
-- 11. TIMELINE STEPS WITH FLAGS — Show escalated/flagged steps
-- ============================================================
SELECT
    t.application_id,
    a.applicant_name,
    t.step_name,
    t.step_status,
    t.triggered_by,
    t.output_data->>'escalation_reason' AS escalation_reason,
    t.output_data->>'confidence_score'  AS confidence_at_step
FROM application_timeline t
JOIN applications a ON a.application_id = t.application_id
WHERE t.step_status IN ('ESCALATED', 'FLAGGED', 'FAIL')
ORDER BY t.application_id, t.step_order;
