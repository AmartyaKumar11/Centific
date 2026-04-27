-- ============================================================
-- LOAN PREQUALIFICATION AGENT — PostgreSQL DML (data.sql)
-- Sample data: 14 applications, all 8 tables populated
-- Source: loan_underwriting_perfected.csv (14 rows)
-- Generated to match schema.sql exactly
-- ============================================================

BEGIN;


-- ============================================================
-- TABLE 1: applications
-- ============================================================
INSERT INTO maria.applications
    (application_id, pan_number, applicant_name, requested_loan_amount,
     requested_tenure_months, application_date, decision, risk_category,
     confidence_score, hil_required_flag, decision_reason_codes)
VALUES
    ('APP-2026-00001', 'CRJKW0660X', 'MEHTA VARUN', 596410, 60, '2026-03-26T00:00:00+05:30'::TIMESTAMPTZ, 'APPROVED', 'LOW', 100, FALSE, 'LOW_RISK'),
    ('APP-2026-00002', 'ZVZYW1424B', 'RAO SNEHA', 354974, 12, '2026-03-25T00:00:00+05:30'::TIMESTAMPTZ, 'REJECTED', 'HIGH', 75, FALSE, 'DEFAULT_FLAG|LOW_CIBIL|HIGH_DTI'),
    ('APP-2026-00003', 'BPNWE9015V', 'PILLAI SAVITA', 219751, 24, '2026-04-06T00:00:00+05:30'::TIMESTAMPTZ, 'REJECTED', 'HIGH', 65, TRUE, 'HIGH_DTI|HIGH_ENQUIRIES|INCOME_MISMATCH'),
    ('APP-2026-00004', 'BLZZB2298H', 'TIWARI AJAY', 291723, 24, '2026-03-27T00:00:00+05:30'::TIMESTAMPTZ, 'REVIEW', 'MEDIUM', 100, TRUE, 'BORDERLINE_DTI'),
    ('APP-2026-00005', 'COHPS2624B', 'KAPOOR KAVYA', 250520, 24, '2026-04-02T00:00:00+05:30'::TIMESTAMPTZ, 'REJECTED', 'HIGH', 100, FALSE, 'DEFAULT_FLAG|LOW_CIBIL|BORDERLINE_DTI'),
    ('APP-2026-00006', 'OLBJY9036V', 'MALHOTRA LAKSHMI', 283796, 24, '2026-04-14T00:00:00+05:30'::TIMESTAMPTZ, 'REJECTED', 'HIGH', 75, TRUE, 'DEFAULT_FLAG|LOW_CIBIL|HIGH_ENQUIRIES|INCOME_MISMATCH'),
    ('APP-2026-00007', 'SJBMF9388H', 'NAIDU KIRAN', 637633, 12, '2026-04-18T00:00:00+05:30'::TIMESTAMPTZ, 'APPROVED', 'LOW', 85, FALSE, 'LOW_RISK'),
    ('APP-2026-00008', 'PZAPI7491S', 'NAIR DEEPAK', 469899, 60, '2026-04-04T00:00:00+05:30'::TIMESTAMPTZ, 'REJECTED', 'HIGH', 90, FALSE, 'DEFAULT_FLAG|LOW_CIBIL|HIGH_DTI'),
    ('APP-2026-00009', 'DXNRI6516M', 'SAXENA VIVEK', 272831, 48, '2026-04-09T00:00:00+05:30'::TIMESTAMPTZ, 'REJECTED', 'HIGH', 65, TRUE, 'LOW_CIBIL|HIGH_DTI|HIGH_ENQUIRIES|INCOME_MISMATCH'),
    ('APP-2026-00010', 'RQCYG3810P', 'DAS NIKHIL', 335208, 12, '2026-04-12T00:00:00+05:30'::TIMESTAMPTZ, 'REJECTED', 'HIGH', 75, FALSE, 'HIGH_DTI'),
    ('APP-2026-00011', 'USMOX1145R', 'NAIR AMIT', 1309676, 48, '2026-03-27T00:00:00+05:30'::TIMESTAMPTZ, 'APPROVED', 'LOW', 100, FALSE, 'LOW_RISK'),
    ('APP-2026-00012', 'GQTNQ2022K', 'KRISHNAN DEEPAK', 295622, 48, '2026-03-26T00:00:00+05:30'::TIMESTAMPTZ, 'REVIEW', 'MEDIUM', 75, TRUE, 'INCOME_MISMATCH'),
    ('APP-2026-00013', 'JAJTW9475T', 'MALHOTRA AJAY', 246302, 48, '2026-04-04T00:00:00+05:30'::TIMESTAMPTZ, 'APPROVED', 'LOW', 100, FALSE, 'LOW_RISK'),
    ('APP-2026-00014', 'AQDMB3237M', 'HEGDE PRAKASH', 272068, 12, '2026-04-10T00:00:00+05:30'::TIMESTAMPTZ, 'REJECTED', 'HIGH', 90, FALSE, 'HIGH_DTI')
ON CONFLICT (application_id) DO NOTHING;

-- ============================================================
-- TABLE 2: kyc_api_table
-- ============================================================
INSERT INTO maria.kyc_api_table
    (application_id, pan_number, applicant_name, aadhaar_number, date_of_birth,
     phone_number, email, address, employer_name, employer_type,
     employment_tenure_years, data_consistency_flag)
VALUES
    ('APP-2026-00001', 'CRJKW0660X', 'MEHTA VARUN', 367469214295, '1991-06-11'::DATE, 916667779376, 'mehta.varun@email.com', 'Mumbai, Gujarat', 'Reliance Industries', 'PRIVATE', 12.6, TRUE),
    ('APP-2026-00002', 'ZVZYW1424B', 'RAO SNEHA', 251282538206, '1981-03-07'::DATE, 916924765563, 'rao.sneha@email.com', 'Jaipur, Karnataka', 'HDFC Bank', 'PRIVATE', 3.7, TRUE),
    ('APP-2026-00003', 'BPNWE9015V', 'PILLAI SAVITA', 214832269481, '1974-11-24'::DATE, 919279182318, 'pillai.savita@email.com', 'Pune, Karnataka', 'BHEL', 'GOVERNMENT', 1.3, FALSE),
    ('APP-2026-00004', 'BLZZB2298H', 'TIWARI AJAY', 914655221101, '1988-11-07'::DATE, 917445662585, 'tiwari.ajay@email.com', 'Jaipur, Tamil Nadu', 'Larsen & Toubro', 'PRIVATE', 3.0, TRUE),
    ('APP-2026-00005', 'COHPS2624B', 'KAPOOR KAVYA', 700832336208, '1965-01-08'::DATE, 916438989805, 'kapoor.kavya@email.com', 'Lucknow, West Bengal', 'Wipro Technologies', 'PRIVATE', 5.4, TRUE),
    ('APP-2026-00006', 'OLBJY9036V', 'MALHOTRA LAKSHMI', 748913461122, '1962-05-03'::DATE, 916398340369, 'malhotra.lakshmi@email.com', 'Lucknow, Telangana', 'HCL Technologies', 'PRIVATE', 3.5, FALSE),
    ('APP-2026-00007', 'SJBMF9388H', 'NAIDU KIRAN', 136171878809, '2001-01-14'::DATE, 917631775357, 'naidu.kiran@email.com', 'Bangalore, Maharashtra', 'Infosys Ltd', 'PRIVATE', 10.9, TRUE),
    ('APP-2026-00008', 'PZAPI7491S', 'NAIR DEEPAK', 198912225902, '1967-04-17'::DATE, 916415393687, 'nair.deepak@email.com', 'Hyderabad, Tamil Nadu', 'ICICI Bank', 'PRIVATE', 1.4, TRUE),
    ('APP-2026-00009', 'DXNRI6516M', 'SAXENA VIVEK', 354342113419, '1965-03-08'::DATE, 917541804686, 'saxena.vivek@email.com', 'Bangalore, Telangana', 'Government of Karnataka', 'GOVERNMENT', 3.1, FALSE),
    ('APP-2026-00010', 'RQCYG3810P', 'DAS NIKHIL', 763595448017, '1994-03-03'::DATE, 919639960595, 'das.nikhil@email.com', 'Bangalore, Maharashtra', 'Cipla Ltd', 'PRIVATE', 6.9, TRUE),
    ('APP-2026-00011', 'USMOX1145R', 'NAIR AMIT', 714294294451, '1970-01-05'::DATE, 917477278577, 'nair.amit@email.com', 'Chennai, Gujarat', 'Cipla Ltd', 'PRIVATE', 6.8, TRUE),
    ('APP-2026-00012', 'GQTNQ2022K', 'KRISHNAN DEEPAK', 886833016361, '1982-05-16'::DATE, 918592983555, 'krishnan.deepak@email.com', 'Kolkata, Delhi', 'NTPC Ltd', 'GOVERNMENT', 9.5, FALSE),
    ('APP-2026-00013', 'JAJTW9475T', 'MALHOTRA AJAY', 871590378377, '1986-01-25'::DATE, 917136108454, 'malhotra.ajay@email.com', 'Kolkata, West Bengal', 'NTPC Ltd', 'GOVERNMENT', 5.6, TRUE),
    ('APP-2026-00014', 'AQDMB3237M', 'HEGDE PRAKASH', 561902006518, '1988-11-12'::DATE, 919466589567, 'hegde.prakash@email.com', 'Hyderabad, Tamil Nadu', 'Axis Bank', 'PRIVATE', 6.3, TRUE)
ON CONFLICT (application_id) DO NOTHING;

-- ============================================================
-- TABLE 3: cibil_api_table
-- ============================================================
INSERT INTO maria.cibil_api_table
    (application_id, pan_number, cibil_score, default_flag, written_off_flag,
     credit_enquiries_6m, negative_items_count, oldest_account_years,
     inquiries_12m, accounts_good_standing, derogatory_marks)
VALUES
    ('APP-2026-00001', 'CRJKW0660X', 745, FALSE, FALSE, 0, NULL, NULL, NULL, NULL, NULL),
    ('APP-2026-00002', 'ZVZYW1424B', 635, TRUE, FALSE, 0, NULL, NULL, NULL, NULL, NULL),
    ('APP-2026-00003', 'BPNWE9015V', 763, FALSE, FALSE, 6, 2.0, 1.5, 6.0, 3.0, 2.0),
    ('APP-2026-00004', 'BLZZB2298H', 687, FALSE, FALSE, 0, NULL, NULL, NULL, NULL, NULL),
    ('APP-2026-00005', 'COHPS2624B', 629, TRUE, FALSE, 0, NULL, NULL, NULL, NULL, NULL),
    ('APP-2026-00006', 'OLBJY9036V', 628, TRUE, FALSE, 4, 1.0, 5.9, 4.0, 3.0, 1.0),
    ('APP-2026-00007', 'SJBMF9388H', 749, FALSE, FALSE, 0, NULL, NULL, NULL, NULL, NULL),
    ('APP-2026-00008', 'PZAPI7491S', 590, TRUE, FALSE, 0, NULL, NULL, NULL, NULL, NULL),
    ('APP-2026-00009', 'DXNRI6516M', 606, FALSE, FALSE, 7, 3.0, 1.0, 7.0, 1.0, 1.0),
    ('APP-2026-00010', 'RQCYG3810P', 728, FALSE, FALSE, 0, NULL, NULL, NULL, NULL, NULL),
    ('APP-2026-00011', 'USMOX1145R', 835, FALSE, FALSE, 0, NULL, NULL, NULL, NULL, NULL),
    ('APP-2026-00012', 'GQTNQ2022K', 789, FALSE, FALSE, 2, 0.0, 8.9, 2.0, 4.0, 0.0),
    ('APP-2026-00013', 'JAJTW9475T', 871, FALSE, FALSE, 0, NULL, NULL, NULL, NULL, NULL),
    ('APP-2026-00014', 'AQDMB3237M', 683, FALSE, FALSE, 0, NULL, NULL, NULL, NULL, NULL)
ON CONFLICT (application_id) DO NOTHING;

-- ============================================================
-- TABLE 4: bank_api_table
-- ============================================================
INSERT INTO maria.bank_api_table
    (application_id, pan_number, bank_balance, bounce_count, statement_months,
     spending_ratio, negative_month_count, existing_emi_total)
VALUES
    ('APP-2026-00001', 'CRJKW0660X', 427599, 0, 6, 0.42, 0, 12307),
    ('APP-2026-00002', 'ZVZYW1424B', 389402, 1, 12, 0.64, 0, 22451),
    ('APP-2026-00003', 'BPNWE9015V', 18244, 2, 12, 0.79, 0, 10855),
    ('APP-2026-00004', 'BLZZB2298H', 299847, 1, 6, 0.8, 0, 34145),
    ('APP-2026-00005', 'COHPS2624B', 145324, 0, 9, 0.6, 0, 27308),
    ('APP-2026-00006', 'OLBJY9036V', 429181, 2, 6, 0.79, 1, 21749),
    ('APP-2026-00007', 'SJBMF9388H', 1087594, 0, 9, 0.67, 0, 16945),
    ('APP-2026-00008', 'PZAPI7491S', 141298, 1, 6, 0.86, 0, 30332),
    ('APP-2026-00009', 'DXNRI6516M', 33722, 2, 9, 0.8, 1, 11596),
    ('APP-2026-00010', 'RQCYG3810P', 131150, 0, 9, 0.6, 0, 16203),
    ('APP-2026-00011', 'USMOX1145R', 1790710, 0, 12, 0.45, 0, 34947),
    ('APP-2026-00012', 'GQTNQ2022K', 552568, 0, 6, 0.53, 0, 9545),
    ('APP-2026-00013', 'JAJTW9475T', 936094, 0, 6, 0.69, 0, 20673),
    ('APP-2026-00014', 'AQDMB3237M', 418243, 0, 6, 0.81, 0, 25440)
ON CONFLICT (application_id) DO NOTHING;

-- ============================================================
-- TABLE 5: income_api_table
-- ============================================================
INSERT INTO maria.income_api_table
    (application_id, pan_number, gross_salary, total_deductions,
     declared_income, verified_income, income_mismatch_flag, income_stability)
VALUES
    ('APP-2026-00001', 'CRJKW0660X', 108644, 22257, 102638, 102638, FALSE, 'CONSISTENT_6M'),
    ('APP-2026-00002', 'ZVZYW1424B', 101173, 20894, 103391, 103391, FALSE, 'CONSISTENT_6M'),
    ('APP-2026-00003', 'BPNWE9015V', 37856, 10378, 37631, 28024, TRUE, 'ONE_ANOMALY'),
    ('APP-2026-00004', 'BLZZB2298H', 107433, 28295, 108664, 108664, FALSE, 'CONSISTENT_3M'),
    ('APP-2026-00005', 'COHPS2624B', 86265, 15908, 83104, 83104, FALSE, 'CONSISTENT_6M'),
    ('APP-2026-00006', 'OLBJY9036V', 123385, 33118, 120032, 89720, TRUE, 'CONSISTENT_3M'),
    ('APP-2026-00007', 'SJBMF9388H', 184455, 39256, 190425, 190425, FALSE, 'CONSISTENT_3M'),
    ('APP-2026-00008', 'PZAPI7491S', 76450, 17094, 75501, 75501, FALSE, 'TWO_PLUS_ANOMALIES'),
    ('APP-2026-00009', 'DXNRI6516M', 41405, 10001, 39712, 33329, TRUE, 'ONE_ANOMALY'),
    ('APP-2026-00010', 'RQCYG3810P', 59545, 13429, 61640, 61640, FALSE, 'CONSISTENT_3M'),
    ('APP-2026-00011', 'USMOX1145R', 277984, 74817, 277885, 277885, FALSE, 'CONSISTENT_6M'),
    ('APP-2026-00012', 'GQTNQ2022K', 116273, 22682, 112760, 85105, TRUE, 'CONSISTENT_6M'),
    ('APP-2026-00013', 'JAJTW9475T', 137520, 28507, 135200, 135200, FALSE, 'CONSISTENT_6M'),
    ('APP-2026-00014', 'AQDMB3237M', 105255, 21601, 97955, 97955, FALSE, 'CONSISTENT_6M')
ON CONFLICT (application_id) DO NOTHING;

-- ============================================================
-- TABLE 6: document_analysis_table
-- ============================================================
INSERT INTO maria.document_analysis_table
    (application_id, pan_number, ocr_confidence_score,
     document_consistency_flag, data_consistency_flag)
VALUES
    ('APP-2026-00001', 'CRJKW0660X', 88, TRUE, TRUE),
    ('APP-2026-00002', 'ZVZYW1424B', 70, FALSE, TRUE),
    ('APP-2026-00003', 'BPNWE9015V', 98, TRUE, FALSE),
    ('APP-2026-00004', 'BLZZB2298H', 97, TRUE, TRUE),
    ('APP-2026-00005', 'COHPS2624B', 97, TRUE, TRUE),
    ('APP-2026-00006', 'OLBJY9036V', 85, TRUE, FALSE),
    ('APP-2026-00007', 'SJBMF9388H', 67, FALSE, TRUE),
    ('APP-2026-00008', 'PZAPI7491S', 98, TRUE, TRUE),
    ('APP-2026-00009', 'DXNRI6516M', 85, TRUE, FALSE),
    ('APP-2026-00010', 'RQCYG3810P', 70, FALSE, TRUE),
    ('APP-2026-00011', 'USMOX1145R', 91, TRUE, TRUE),
    ('APP-2026-00012', 'GQTNQ2022K', 89, TRUE, FALSE),
    ('APP-2026-00013', 'JAJTW9475T', 86, TRUE, TRUE),
    ('APP-2026-00014', 'AQDMB3237M', 88, TRUE, TRUE)
ON CONFLICT (application_id) DO NOTHING;

-- ============================================================
-- TABLE 7: decision_engine_output
-- ============================================================
INSERT INTO maria.decision_engine_output
    (application_id, pan_number, decision, risk_category, decision_reason_codes,
     confidence_score, hil_required_flag, interest_rate, proposed_emi, dti_ratio)
VALUES
    ('APP-2026-00001', 'CRJKW0660X', 'APPROVED', 'LOW', 'LOW_RISK', 100, FALSE, 8.5, 12236, 0.23912196262592803),
    ('APP-2026-00002', 'ZVZYW1424B', 'REJECTED', 'HIGH', 'DEFAULT_FLAG|LOW_CIBIL|HIGH_DTI', 75, FALSE, 13.5, 31788, 0.5246007873025699),
    ('APP-2026-00003', 'BPNWE9015V', 'REJECTED', 'HIGH', 'HIGH_DTI|HIGH_ENQUIRIES|INCOME_MISMATCH', 65, TRUE, 6.5, 9789, 0.7366542963174422),
    ('APP-2026-00004', 'BLZZB2298H', 'REVIEW', 'MEDIUM', 'BORDERLINE_DTI', 100, TRUE, 10.5, 13528, 0.4387193550761982),
    ('APP-2026-00005', 'COHPS2624B', 'REJECTED', 'HIGH', 'DEFAULT_FLAG|LOW_CIBIL|BORDERLINE_DTI', 100, FALSE, 13.5, 11969, 0.4726246630727763),
    ('APP-2026-00006', 'OLBJY9036V', 'REJECTED', 'HIGH', 'DEFAULT_FLAG|LOW_CIBIL|HIGH_ENQUIRIES|INCOME_MISMATCH', 75, TRUE, 13.5, 13558, 0.39352429781542575),
    ('APP-2026-00007', 'SJBMF9388H', 'APPROVED', 'LOW', 'LOW_RISK', 85, FALSE, 8.5, 55614, 0.3810371537350663),
    ('APP-2026-00008', 'PZAPI7491S', 'REJECTED', 'HIGH', 'DEFAULT_FLAG|LOW_CIBIL|HIGH_DTI', 90, FALSE, 13.5, 10812, 0.5449464245506682),
    ('APP-2026-00009', 'DXNRI6516M', 'REJECTED', 'HIGH', 'LOW_CIBIL|HIGH_DTI|HIGH_ENQUIRIES|INCOME_MISMATCH', 65, TRUE, 13.5, 7387, 0.5695640433256324),
    ('APP-2026-00010', 'RQCYG3810P', 'REJECTED', 'HIGH', 'HIGH_DTI', 75, FALSE, 8.5, 29236, 0.7371674237508111),
    ('APP-2026-00011', 'USMOX1145R', 'APPROVED', 'LOW', 'LOW_RISK', 100, FALSE, 6.5, 31058, 0.2375263148424708),
    ('APP-2026-00012', 'GQTNQ2022K', 'REVIEW', 'MEDIUM', 'INCOME_MISMATCH', 75, TRUE, 6.5, 7010, 0.1945244110216791),
    ('APP-2026-00013', 'JAJTW9475T', 'APPROVED', 'LOW', 'LOW_RISK', 100, FALSE, 6.5, 5841, 0.1961094674556213),
    ('APP-2026-00014', 'AQDMB3237M', 'REJECTED', 'HIGH', 'HIGH_DTI', 90, FALSE, 10.5, 23982, 0.5045377979684549)
ON CONFLICT (application_id) DO NOTHING;

-- ============================================================
-- TABLE 8: application_timeline
-- 119 step rows across 14 applications (8–9 steps each)
-- ============================================================
INSERT INTO maria.application_timeline
    (application_id, step_order, step_name, step_status, triggered_by, output_data)
VALUES
    ('APP-2026-00001', 1, 'KYC_VALIDATION', 'PASS', 'application_intake', '{"pan_number": "CRJKW0660X", "aadhaar_check": "match", "dob_verified": "1991-06-11", "identity_match": true, "dedupe_window_30d": "pass"}'::JSONB),
    ('APP-2026-00001', 2, 'DOCUMENT_ANALYSIS', 'PASS', 'kyc_validation_complete', '{"ocr_confidence_score": 88, "document_consistency": true, "data_consistency": true, "ocr_result": "high_confidence"}'::JSONB),
    ('APP-2026-00001', 3, 'INCOME_VERIFICATION', 'PASS', 'document_analysis_complete', '{"declared_income": 102638, "verified_income": 102638, "income_mismatch_flag": false, "income_stability": "CONSISTENT_6M", "mismatch_delta": 0}'::JSONB),
    ('APP-2026-00001', 4, 'BANK_STATEMENT_ANALYSIS', 'PASS', 'standard_pipeline', '{"bank_balance": 427599, "bounce_count": 0, "spending_ratio": 0.42, "negative_month_count": 0, "existing_emi_total": 12307}'::JSONB),
    ('APP-2026-00001', 5, 'CIBIL_FETCH', 'PASS', 'bank_analysis_complete', '{"cibil_score": 745, "default_flag": false, "written_off_flag": false, "credit_enquiries_6m": 0, "cibil_check": "above_threshold"}'::JSONB),
    ('APP-2026-00001', 6, 'FEATURE_ENGINEERING', 'PASS', 'all_api_calls_complete', '{"dti_ratio": 0.2391, "proposed_emi": 12236, "interest_rate": 8.5, "risk_score": "LOW", "dti_band": "LOW"}'::JSONB),
    ('APP-2026-00001', 7, 'DECISION_ENGINE', 'PASS', 'feature_engineering_complete', '{"decision": "APPROVED", "risk_category": "LOW", "decision_reason_codes": "LOW_RISK", "confidence_score": 100, "recommendation": "approved", "hard_policy_breach": false}'::JSONB),
    ('APP-2026-00001', 8, 'FINAL_DECISION', 'PASS', 'decision_engine_complete', '{"final_decision": "APPROVED", "interest_rate": 8.5, "proposed_emi": 12236, "risk_category": "LOW"}'::JSONB),
    ('APP-2026-00002', 1, 'KYC_VALIDATION', 'PASS', 'application_intake', '{"pan_number": "ZVZYW1424B", "aadhaar_check": "match", "dob_verified": "1981-03-07", "identity_match": true, "dedupe_window_30d": "pass"}'::JSONB),
    ('APP-2026-00002', 2, 'DOCUMENT_ANALYSIS', 'FLAGGED', 'kyc_validation_complete', '{"ocr_confidence_score": 70, "document_consistency": false, "data_consistency": true, "ocr_result": "low_confidence"}'::JSONB),
    ('APP-2026-00002', 3, 'INCOME_VERIFICATION', 'PASS', 'document_analysis_complete', '{"declared_income": 103391, "verified_income": 103391, "income_mismatch_flag": false, "income_stability": "CONSISTENT_6M", "mismatch_delta": 0}'::JSONB),
    ('APP-2026-00002', 4, 'BANK_STATEMENT_ANALYSIS', 'PASS', 'standard_pipeline', '{"bank_balance": 389402, "bounce_count": 1, "spending_ratio": 0.64, "negative_month_count": 0, "existing_emi_total": 22451}'::JSONB),
    ('APP-2026-00002', 5, 'CIBIL_FETCH', 'FAIL', 'bank_analysis_complete', '{"cibil_score": 635, "default_flag": true, "written_off_flag": false, "credit_enquiries_6m": 0, "cibil_check": "above_threshold"}'::JSONB),
    ('APP-2026-00002', 6, 'FEATURE_ENGINEERING', 'PASS', 'all_api_calls_complete', '{"dti_ratio": 0.5246, "proposed_emi": 31788, "interest_rate": 13.5, "risk_score": "HIGH", "dti_band": "HIGH"}'::JSONB),
    ('APP-2026-00002', 7, 'DECISION_ENGINE', 'PASS', 'feature_engineering_complete', '{"decision": "REJECTED", "risk_category": "HIGH", "decision_reason_codes": "DEFAULT_FLAG|LOW_CIBIL|HIGH_DTI", "confidence_score": 75, "recommendation": "rejected", "hard_policy_breach": true}'::JSONB),
    ('APP-2026-00002', 8, 'HIL_ESCALATION', 'ESCALATED', 'low_confidence_score', '{"hil_required": true, "escalation_reason": "low_confidence", "confidence_score": 75, "assigned_to": "credit_manager"}'::JSONB),
    ('APP-2026-00002', 9, 'FINAL_DECISION', 'PASS', 'hil_review_complete', '{"final_decision": "REJECTED", "interest_rate": 13.5, "proposed_emi": 31788, "risk_category": "HIGH"}'::JSONB),
    ('APP-2026-00003', 1, 'KYC_VALIDATION', 'PASS', 'application_intake', '{"pan_number": "BPNWE9015V", "aadhaar_check": "match", "dob_verified": "1974-11-24", "identity_match": true, "dedupe_window_30d": "pass"}'::JSONB),
    ('APP-2026-00003', 2, 'DOCUMENT_ANALYSIS', 'PASS', 'kyc_validation_complete', '{"ocr_confidence_score": 98, "document_consistency": true, "data_consistency": false, "ocr_result": "high_confidence"}'::JSONB),
    ('APP-2026-00003', 3, 'INCOME_VERIFICATION', 'FLAGGED', 'document_analysis_complete', '{"declared_income": 37631, "verified_income": 28024, "income_mismatch_flag": true, "income_stability": "ONE_ANOMALY", "mismatch_delta": 9607}'::JSONB),
    ('APP-2026-00003', 4, 'BANK_STATEMENT_ANALYSIS', 'PASS', 'income_mismatch_detected', '{"bank_balance": 18244, "bounce_count": 2, "spending_ratio": 0.79, "negative_month_count": 0, "existing_emi_total": 10855, "trigger_reason": "income_mismatch_in_prior_step"}'::JSONB),
    ('APP-2026-00003', 5, 'CIBIL_FETCH', 'PASS', 'bank_analysis_complete', '{"cibil_score": 763, "default_flag": false, "written_off_flag": false, "credit_enquiries_6m": 6, "cibil_check": "above_threshold"}'::JSONB),
    ('APP-2026-00003', 6, 'FEATURE_ENGINEERING', 'PASS', 'all_api_calls_complete', '{"dti_ratio": 0.7367, "proposed_emi": 9789, "interest_rate": 6.5, "risk_score": "HIGH", "dti_band": "HIGH"}'::JSONB),
    ('APP-2026-00003', 7, 'DECISION_ENGINE', 'PASS', 'feature_engineering_complete', '{"decision": "REJECTED", "risk_category": "HIGH", "decision_reason_codes": "HIGH_DTI|HIGH_ENQUIRIES|INCOME_MISMATCH", "confidence_score": 65, "recommendation": "rejected", "hard_policy_breach": true}'::JSONB),
    ('APP-2026-00003', 8, 'HIL_ESCALATION', 'ESCALATED', 'hil_required_flag=Y', '{"hil_required": true, "escalation_reason": "policy_flags", "confidence_score": 65, "assigned_to": "credit_manager"}'::JSONB),
    ('APP-2026-00003', 9, 'FINAL_DECISION', 'PASS', 'hil_review_complete', '{"final_decision": "REJECTED", "interest_rate": 6.5, "proposed_emi": 9789, "risk_category": "HIGH"}'::JSONB),
    ('APP-2026-00004', 1, 'KYC_VALIDATION', 'PASS', 'application_intake', '{"pan_number": "BLZZB2298H", "aadhaar_check": "match", "dob_verified": "1988-11-07", "identity_match": true, "dedupe_window_30d": "pass"}'::JSONB),
    ('APP-2026-00004', 2, 'DOCUMENT_ANALYSIS', 'PASS', 'kyc_validation_complete', '{"ocr_confidence_score": 97, "document_consistency": true, "data_consistency": true, "ocr_result": "high_confidence"}'::JSONB),
    ('APP-2026-00004', 3, 'INCOME_VERIFICATION', 'PASS', 'document_analysis_complete', '{"declared_income": 108664, "verified_income": 108664, "income_mismatch_flag": false, "income_stability": "CONSISTENT_3M", "mismatch_delta": 0}'::JSONB),
    ('APP-2026-00004', 4, 'BANK_STATEMENT_ANALYSIS', 'PASS', 'standard_pipeline', '{"bank_balance": 299847, "bounce_count": 1, "spending_ratio": 0.8, "negative_month_count": 0, "existing_emi_total": 34145}'::JSONB),
    ('APP-2026-00004', 5, 'CIBIL_FETCH', 'PASS', 'bank_analysis_complete', '{"cibil_score": 687, "default_flag": false, "written_off_flag": false, "credit_enquiries_6m": 0, "cibil_check": "above_threshold"}'::JSONB),
    ('APP-2026-00004', 6, 'FEATURE_ENGINEERING', 'PASS', 'all_api_calls_complete', '{"dti_ratio": 0.4387, "proposed_emi": 13528, "interest_rate": 10.5, "risk_score": "MEDIUM", "dti_band": "MEDIUM"}'::JSONB),
    ('APP-2026-00004', 7, 'DECISION_ENGINE', 'PASS', 'feature_engineering_complete', '{"decision": "REVIEW", "risk_category": "MEDIUM", "decision_reason_codes": "BORDERLINE_DTI", "confidence_score": 100, "recommendation": "review", "hard_policy_breach": false}'::JSONB),
    ('APP-2026-00004', 8, 'HIL_ESCALATION', 'ESCALATED', 'hil_required_flag=Y', '{"hil_required": true, "escalation_reason": "policy_flags", "confidence_score": 100, "assigned_to": "credit_manager"}'::JSONB),
    ('APP-2026-00004', 9, 'FINAL_DECISION', 'PASS', 'hil_review_complete', '{"final_decision": "REVIEW", "interest_rate": 10.5, "proposed_emi": 13528, "risk_category": "MEDIUM"}'::JSONB),
    ('APP-2026-00005', 1, 'KYC_VALIDATION', 'PASS', 'application_intake', '{"pan_number": "COHPS2624B", "aadhaar_check": "match", "dob_verified": "1965-01-08", "identity_match": true, "dedupe_window_30d": "pass"}'::JSONB),
    ('APP-2026-00005', 2, 'DOCUMENT_ANALYSIS', 'PASS', 'kyc_validation_complete', '{"ocr_confidence_score": 97, "document_consistency": true, "data_consistency": true, "ocr_result": "high_confidence"}'::JSONB),
    ('APP-2026-00005', 3, 'INCOME_VERIFICATION', 'PASS', 'document_analysis_complete', '{"declared_income": 83104, "verified_income": 83104, "income_mismatch_flag": false, "income_stability": "CONSISTENT_6M", "mismatch_delta": 0}'::JSONB),
    ('APP-2026-00005', 4, 'BANK_STATEMENT_ANALYSIS', 'PASS', 'standard_pipeline', '{"bank_balance": 145324, "bounce_count": 0, "spending_ratio": 0.6, "negative_month_count": 0, "existing_emi_total": 27308}'::JSONB),
    ('APP-2026-00005', 5, 'CIBIL_FETCH', 'FAIL', 'bank_analysis_complete', '{"cibil_score": 629, "default_flag": true, "written_off_flag": false, "credit_enquiries_6m": 0, "cibil_check": "above_threshold"}'::JSONB),
    ('APP-2026-00005', 6, 'FEATURE_ENGINEERING', 'PASS', 'all_api_calls_complete', '{"dti_ratio": 0.4726, "proposed_emi": 11969, "interest_rate": 13.5, "risk_score": "HIGH", "dti_band": "MEDIUM"}'::JSONB),
    ('APP-2026-00005', 7, 'DECISION_ENGINE', 'PASS', 'feature_engineering_complete', '{"decision": "REJECTED", "risk_category": "HIGH", "decision_reason_codes": "DEFAULT_FLAG|LOW_CIBIL|BORDERLINE_DTI", "confidence_score": 100, "recommendation": "rejected", "hard_policy_breach": true}'::JSONB),
    ('APP-2026-00005', 8, 'FINAL_DECISION', 'PASS', 'decision_engine_complete', '{"final_decision": "REJECTED", "interest_rate": 13.5, "proposed_emi": 11969, "risk_category": "HIGH"}'::JSONB),
    ('APP-2026-00006', 1, 'KYC_VALIDATION', 'PASS', 'application_intake', '{"pan_number": "OLBJY9036V", "aadhaar_check": "match", "dob_verified": "1962-05-03", "identity_match": true, "dedupe_window_30d": "pass"}'::JSONB),
    ('APP-2026-00006', 2, 'DOCUMENT_ANALYSIS', 'PASS', 'kyc_validation_complete', '{"ocr_confidence_score": 85, "document_consistency": true, "data_consistency": false, "ocr_result": "high_confidence"}'::JSONB),
    ('APP-2026-00006', 3, 'INCOME_VERIFICATION', 'FLAGGED', 'document_analysis_complete', '{"declared_income": 120032, "verified_income": 89720, "income_mismatch_flag": true, "income_stability": "CONSISTENT_3M", "mismatch_delta": 30312}'::JSONB),
    ('APP-2026-00006', 4, 'BANK_STATEMENT_ANALYSIS', 'PASS', 'income_mismatch_detected', '{"bank_balance": 429181, "bounce_count": 2, "spending_ratio": 0.79, "negative_month_count": 1, "existing_emi_total": 21749, "trigger_reason": "income_mismatch_in_prior_step"}'::JSONB),
    ('APP-2026-00006', 5, 'CIBIL_FETCH', 'FAIL', 'bank_analysis_complete', '{"cibil_score": 628, "default_flag": true, "written_off_flag": false, "credit_enquiries_6m": 4, "cibil_check": "above_threshold"}'::JSONB),
    ('APP-2026-00006', 6, 'FEATURE_ENGINEERING', 'PASS', 'all_api_calls_complete', '{"dti_ratio": 0.3935, "proposed_emi": 13558, "interest_rate": 13.5, "risk_score": "HIGH", "dti_band": "MEDIUM"}'::JSONB),
    ('APP-2026-00006', 7, 'DECISION_ENGINE', 'PASS', 'feature_engineering_complete', '{"decision": "REJECTED", "risk_category": "HIGH", "decision_reason_codes": "DEFAULT_FLAG|LOW_CIBIL|HIGH_ENQUIRIES|INCOME_MISMATCH", "confidence_score": 75, "recommendation": "rejected", "hard_policy_breach": true}'::JSONB),
    ('APP-2026-00006', 8, 'HIL_ESCALATION', 'ESCALATED', 'hil_required_flag=Y', '{"hil_required": true, "escalation_reason": "policy_flags", "confidence_score": 75, "assigned_to": "credit_manager"}'::JSONB),
    ('APP-2026-00006', 9, 'FINAL_DECISION', 'PASS', 'hil_review_complete', '{"final_decision": "REJECTED", "interest_rate": 13.5, "proposed_emi": 13558, "risk_category": "HIGH"}'::JSONB),
    ('APP-2026-00007', 1, 'KYC_VALIDATION', 'PASS', 'application_intake', '{"pan_number": "SJBMF9388H", "aadhaar_check": "match", "dob_verified": "2001-01-14", "identity_match": true, "dedupe_window_30d": "pass"}'::JSONB),
    ('APP-2026-00007', 2, 'DOCUMENT_ANALYSIS', 'FLAGGED', 'kyc_validation_complete', '{"ocr_confidence_score": 67, "document_consistency": false, "data_consistency": true, "ocr_result": "low_confidence"}'::JSONB),
    ('APP-2026-00007', 3, 'INCOME_VERIFICATION', 'PASS', 'document_analysis_complete', '{"declared_income": 190425, "verified_income": 190425, "income_mismatch_flag": false, "income_stability": "CONSISTENT_3M", "mismatch_delta": 0}'::JSONB),
    ('APP-2026-00007', 4, 'BANK_STATEMENT_ANALYSIS', 'PASS', 'standard_pipeline', '{"bank_balance": 1087594, "bounce_count": 0, "spending_ratio": 0.67, "negative_month_count": 0, "existing_emi_total": 16945}'::JSONB),
    ('APP-2026-00007', 5, 'CIBIL_FETCH', 'PASS', 'bank_analysis_complete', '{"cibil_score": 749, "default_flag": false, "written_off_flag": false, "credit_enquiries_6m": 0, "cibil_check": "above_threshold"}'::JSONB),
    ('APP-2026-00007', 6, 'FEATURE_ENGINEERING', 'PASS', 'all_api_calls_complete', '{"dti_ratio": 0.381, "proposed_emi": 55614, "interest_rate": 8.5, "risk_score": "LOW", "dti_band": "MEDIUM"}'::JSONB),
    ('APP-2026-00007', 7, 'DECISION_ENGINE', 'PASS', 'feature_engineering_complete', '{"decision": "APPROVED", "risk_category": "LOW", "decision_reason_codes": "LOW_RISK", "confidence_score": 85, "recommendation": "approved", "hard_policy_breach": false}'::JSONB),
    ('APP-2026-00007', 8, 'FINAL_DECISION', 'PASS', 'decision_engine_complete', '{"final_decision": "APPROVED", "interest_rate": 8.5, "proposed_emi": 55614, "risk_category": "LOW"}'::JSONB),
    ('APP-2026-00008', 1, 'KYC_VALIDATION', 'PASS', 'application_intake', '{"pan_number": "PZAPI7491S", "aadhaar_check": "match", "dob_verified": "1967-04-17", "identity_match": true, "dedupe_window_30d": "pass"}'::JSONB),
    ('APP-2026-00008', 2, 'DOCUMENT_ANALYSIS', 'PASS', 'kyc_validation_complete', '{"ocr_confidence_score": 98, "document_consistency": true, "data_consistency": true, "ocr_result": "high_confidence"}'::JSONB),
    ('APP-2026-00008', 3, 'INCOME_VERIFICATION', 'PASS', 'document_analysis_complete', '{"declared_income": 75501, "verified_income": 75501, "income_mismatch_flag": false, "income_stability": "TWO_PLUS_ANOMALIES", "mismatch_delta": 0}'::JSONB),
    ('APP-2026-00008', 4, 'BANK_STATEMENT_ANALYSIS', 'PASS', 'standard_pipeline', '{"bank_balance": 141298, "bounce_count": 1, "spending_ratio": 0.86, "negative_month_count": 0, "existing_emi_total": 30332}'::JSONB),
    ('APP-2026-00008', 5, 'CIBIL_FETCH', 'FAIL', 'bank_analysis_complete', '{"cibil_score": 590, "default_flag": true, "written_off_flag": false, "credit_enquiries_6m": 0, "cibil_check": "below_threshold"}'::JSONB),
    ('APP-2026-00008', 6, 'FEATURE_ENGINEERING', 'PASS', 'all_api_calls_complete', '{"dti_ratio": 0.5449, "proposed_emi": 10812, "interest_rate": 13.5, "risk_score": "HIGH", "dti_band": "HIGH"}'::JSONB),
    ('APP-2026-00008', 7, 'DECISION_ENGINE', 'PASS', 'feature_engineering_complete', '{"decision": "REJECTED", "risk_category": "HIGH", "decision_reason_codes": "DEFAULT_FLAG|LOW_CIBIL|HIGH_DTI", "confidence_score": 90, "recommendation": "rejected", "hard_policy_breach": true}'::JSONB),
    ('APP-2026-00008', 8, 'FINAL_DECISION', 'PASS', 'decision_engine_complete', '{"final_decision": "REJECTED", "interest_rate": 13.5, "proposed_emi": 10812, "risk_category": "HIGH"}'::JSONB),
    ('APP-2026-00009', 1, 'KYC_VALIDATION', 'PASS', 'application_intake', '{"pan_number": "DXNRI6516M", "aadhaar_check": "match", "dob_verified": "1965-03-08", "identity_match": true, "dedupe_window_30d": "pass"}'::JSONB),
    ('APP-2026-00009', 2, 'DOCUMENT_ANALYSIS', 'PASS', 'kyc_validation_complete', '{"ocr_confidence_score": 85, "document_consistency": true, "data_consistency": false, "ocr_result": "high_confidence"}'::JSONB),
    ('APP-2026-00009', 3, 'INCOME_VERIFICATION', 'FLAGGED', 'document_analysis_complete', '{"declared_income": 39712, "verified_income": 33329, "income_mismatch_flag": true, "income_stability": "ONE_ANOMALY", "mismatch_delta": 6383}'::JSONB),
    ('APP-2026-00009', 4, 'BANK_STATEMENT_ANALYSIS', 'PASS', 'income_mismatch_detected', '{"bank_balance": 33722, "bounce_count": 2, "spending_ratio": 0.8, "negative_month_count": 1, "existing_emi_total": 11596, "trigger_reason": "income_mismatch_in_prior_step"}'::JSONB),
    ('APP-2026-00009', 5, 'CIBIL_FETCH', 'FAIL', 'bank_analysis_complete', '{"cibil_score": 606, "default_flag": false, "written_off_flag": false, "credit_enquiries_6m": 7, "cibil_check": "below_threshold"}'::JSONB),
    ('APP-2026-00009', 6, 'FEATURE_ENGINEERING', 'PASS', 'all_api_calls_complete', '{"dti_ratio": 0.5696, "proposed_emi": 7387, "interest_rate": 13.5, "risk_score": "HIGH", "dti_band": "HIGH"}'::JSONB),
    ('APP-2026-00009', 7, 'DECISION_ENGINE', 'PASS', 'feature_engineering_complete', '{"decision": "REJECTED", "risk_category": "HIGH", "decision_reason_codes": "LOW_CIBIL|HIGH_DTI|HIGH_ENQUIRIES|INCOME_MISMATCH", "confidence_score": 65, "recommendation": "rejected", "hard_policy_breach": true}'::JSONB),
    ('APP-2026-00009', 8, 'HIL_ESCALATION', 'ESCALATED', 'hil_required_flag=Y', '{"hil_required": true, "escalation_reason": "policy_flags", "confidence_score": 65, "assigned_to": "credit_manager"}'::JSONB),
    ('APP-2026-00009', 9, 'FINAL_DECISION', 'PASS', 'hil_review_complete', '{"final_decision": "REJECTED", "interest_rate": 13.5, "proposed_emi": 7387, "risk_category": "HIGH"}'::JSONB),
    ('APP-2026-00010', 1, 'KYC_VALIDATION', 'PASS', 'application_intake', '{"pan_number": "RQCYG3810P", "aadhaar_check": "match", "dob_verified": "1994-03-03", "identity_match": true, "dedupe_window_30d": "pass"}'::JSONB),
    ('APP-2026-00010', 2, 'DOCUMENT_ANALYSIS', 'FLAGGED', 'kyc_validation_complete', '{"ocr_confidence_score": 70, "document_consistency": false, "data_consistency": true, "ocr_result": "low_confidence"}'::JSONB),
    ('APP-2026-00010', 3, 'INCOME_VERIFICATION', 'PASS', 'document_analysis_complete', '{"declared_income": 61640, "verified_income": 61640, "income_mismatch_flag": false, "income_stability": "CONSISTENT_3M", "mismatch_delta": 0}'::JSONB),
    ('APP-2026-00010', 4, 'BANK_STATEMENT_ANALYSIS', 'PASS', 'standard_pipeline', '{"bank_balance": 131150, "bounce_count": 0, "spending_ratio": 0.6, "negative_month_count": 0, "existing_emi_total": 16203}'::JSONB),
    ('APP-2026-00010', 5, 'CIBIL_FETCH', 'PASS', 'bank_analysis_complete', '{"cibil_score": 728, "default_flag": false, "written_off_flag": false, "credit_enquiries_6m": 0, "cibil_check": "above_threshold"}'::JSONB),
    ('APP-2026-00010', 6, 'FEATURE_ENGINEERING', 'PASS', 'all_api_calls_complete', '{"dti_ratio": 0.7372, "proposed_emi": 29236, "interest_rate": 8.5, "risk_score": "HIGH", "dti_band": "HIGH"}'::JSONB),
    ('APP-2026-00010', 7, 'DECISION_ENGINE', 'PASS', 'feature_engineering_complete', '{"decision": "REJECTED", "risk_category": "HIGH", "decision_reason_codes": "HIGH_DTI", "confidence_score": 75, "recommendation": "rejected", "hard_policy_breach": true}'::JSONB),
    ('APP-2026-00010', 8, 'HIL_ESCALATION', 'ESCALATED', 'low_confidence_score', '{"hil_required": true, "escalation_reason": "low_confidence", "confidence_score": 75, "assigned_to": "credit_manager"}'::JSONB),
    ('APP-2026-00010', 9, 'FINAL_DECISION', 'PASS', 'hil_review_complete', '{"final_decision": "REJECTED", "interest_rate": 8.5, "proposed_emi": 29236, "risk_category": "HIGH"}'::JSONB),
    ('APP-2026-00011', 1, 'KYC_VALIDATION', 'PASS', 'application_intake', '{"pan_number": "USMOX1145R", "aadhaar_check": "match", "dob_verified": "1970-01-05", "identity_match": true, "dedupe_window_30d": "pass"}'::JSONB),
    ('APP-2026-00011', 2, 'DOCUMENT_ANALYSIS', 'PASS', 'kyc_validation_complete', '{"ocr_confidence_score": 91, "document_consistency": true, "data_consistency": true, "ocr_result": "high_confidence"}'::JSONB),
    ('APP-2026-00011', 3, 'INCOME_VERIFICATION', 'PASS', 'document_analysis_complete', '{"declared_income": 277885, "verified_income": 277885, "income_mismatch_flag": false, "income_stability": "CONSISTENT_6M", "mismatch_delta": 0}'::JSONB),
    ('APP-2026-00011', 4, 'BANK_STATEMENT_ANALYSIS', 'PASS', 'standard_pipeline', '{"bank_balance": 1790710, "bounce_count": 0, "spending_ratio": 0.45, "negative_month_count": 0, "existing_emi_total": 34947}'::JSONB),
    ('APP-2026-00011', 5, 'CIBIL_FETCH', 'PASS', 'bank_analysis_complete', '{"cibil_score": 835, "default_flag": false, "written_off_flag": false, "credit_enquiries_6m": 0, "cibil_check": "above_threshold"}'::JSONB),
    ('APP-2026-00011', 6, 'FEATURE_ENGINEERING', 'PASS', 'all_api_calls_complete', '{"dti_ratio": 0.2375, "proposed_emi": 31058, "interest_rate": 6.5, "risk_score": "LOW", "dti_band": "LOW"}'::JSONB),
    ('APP-2026-00011', 7, 'DECISION_ENGINE', 'PASS', 'feature_engineering_complete', '{"decision": "APPROVED", "risk_category": "LOW", "decision_reason_codes": "LOW_RISK", "confidence_score": 100, "recommendation": "approved", "hard_policy_breach": false}'::JSONB),
    ('APP-2026-00011', 8, 'FINAL_DECISION', 'PASS', 'decision_engine_complete', '{"final_decision": "APPROVED", "interest_rate": 6.5, "proposed_emi": 31058, "risk_category": "LOW"}'::JSONB),
    ('APP-2026-00012', 1, 'KYC_VALIDATION', 'PASS', 'application_intake', '{"pan_number": "GQTNQ2022K", "aadhaar_check": "match", "dob_verified": "1982-05-16", "identity_match": true, "dedupe_window_30d": "pass"}'::JSONB),
    ('APP-2026-00012', 2, 'DOCUMENT_ANALYSIS', 'PASS', 'kyc_validation_complete', '{"ocr_confidence_score": 89, "document_consistency": true, "data_consistency": false, "ocr_result": "high_confidence"}'::JSONB),
    ('APP-2026-00012', 3, 'INCOME_VERIFICATION', 'FLAGGED', 'document_analysis_complete', '{"declared_income": 112760, "verified_income": 85105, "income_mismatch_flag": true, "income_stability": "CONSISTENT_6M", "mismatch_delta": 27655}'::JSONB),
    ('APP-2026-00012', 4, 'BANK_STATEMENT_ANALYSIS', 'PASS', 'income_mismatch_detected', '{"bank_balance": 552568, "bounce_count": 0, "spending_ratio": 0.53, "negative_month_count": 0, "existing_emi_total": 9545, "trigger_reason": "income_mismatch_in_prior_step"}'::JSONB),
    ('APP-2026-00012', 5, 'CIBIL_FETCH', 'PASS', 'bank_analysis_complete', '{"cibil_score": 789, "default_flag": false, "written_off_flag": false, "credit_enquiries_6m": 2, "cibil_check": "above_threshold"}'::JSONB),
    ('APP-2026-00012', 6, 'FEATURE_ENGINEERING', 'PASS', 'all_api_calls_complete', '{"dti_ratio": 0.1945, "proposed_emi": 7010, "interest_rate": 6.5, "risk_score": "MEDIUM", "dti_band": "LOW"}'::JSONB),
    ('APP-2026-00012', 7, 'DECISION_ENGINE', 'PASS', 'feature_engineering_complete', '{"decision": "REVIEW", "risk_category": "MEDIUM", "decision_reason_codes": "INCOME_MISMATCH", "confidence_score": 75, "recommendation": "review", "hard_policy_breach": false}'::JSONB),
    ('APP-2026-00012', 8, 'HIL_ESCALATION', 'ESCALATED', 'hil_required_flag=Y', '{"hil_required": true, "escalation_reason": "policy_flags", "confidence_score": 75, "assigned_to": "credit_manager"}'::JSONB),
    ('APP-2026-00012', 9, 'FINAL_DECISION', 'PASS', 'hil_review_complete', '{"final_decision": "REVIEW", "interest_rate": 6.5, "proposed_emi": 7010, "risk_category": "MEDIUM"}'::JSONB),
    ('APP-2026-00013', 1, 'KYC_VALIDATION', 'PASS', 'application_intake', '{"pan_number": "JAJTW9475T", "aadhaar_check": "match", "dob_verified": "1986-01-25", "identity_match": true, "dedupe_window_30d": "pass"}'::JSONB),
    ('APP-2026-00013', 2, 'DOCUMENT_ANALYSIS', 'PASS', 'kyc_validation_complete', '{"ocr_confidence_score": 86, "document_consistency": true, "data_consistency": true, "ocr_result": "high_confidence"}'::JSONB),
    ('APP-2026-00013', 3, 'INCOME_VERIFICATION', 'PASS', 'document_analysis_complete', '{"declared_income": 135200, "verified_income": 135200, "income_mismatch_flag": false, "income_stability": "CONSISTENT_6M", "mismatch_delta": 0}'::JSONB),
    ('APP-2026-00013', 4, 'BANK_STATEMENT_ANALYSIS', 'PASS', 'standard_pipeline', '{"bank_balance": 936094, "bounce_count": 0, "spending_ratio": 0.69, "negative_month_count": 0, "existing_emi_total": 20673}'::JSONB),
    ('APP-2026-00013', 5, 'CIBIL_FETCH', 'PASS', 'bank_analysis_complete', '{"cibil_score": 871, "default_flag": false, "written_off_flag": false, "credit_enquiries_6m": 0, "cibil_check": "above_threshold"}'::JSONB),
    ('APP-2026-00013', 6, 'FEATURE_ENGINEERING', 'PASS', 'all_api_calls_complete', '{"dti_ratio": 0.1961, "proposed_emi": 5841, "interest_rate": 6.5, "risk_score": "LOW", "dti_band": "LOW"}'::JSONB),
    ('APP-2026-00013', 7, 'DECISION_ENGINE', 'PASS', 'feature_engineering_complete', '{"decision": "APPROVED", "risk_category": "LOW", "decision_reason_codes": "LOW_RISK", "confidence_score": 100, "recommendation": "approved", "hard_policy_breach": false}'::JSONB),
    ('APP-2026-00013', 8, 'FINAL_DECISION', 'PASS', 'decision_engine_complete', '{"final_decision": "APPROVED", "interest_rate": 6.5, "proposed_emi": 5841, "risk_category": "LOW"}'::JSONB),
    ('APP-2026-00014', 1, 'KYC_VALIDATION', 'PASS', 'application_intake', '{"pan_number": "AQDMB3237M", "aadhaar_check": "match", "dob_verified": "1988-11-12", "identity_match": true, "dedupe_window_30d": "pass"}'::JSONB),
    ('APP-2026-00014', 2, 'DOCUMENT_ANALYSIS', 'PASS', 'kyc_validation_complete', '{"ocr_confidence_score": 88, "document_consistency": true, "data_consistency": true, "ocr_result": "high_confidence"}'::JSONB),
    ('APP-2026-00014', 3, 'INCOME_VERIFICATION', 'PASS', 'document_analysis_complete', '{"declared_income": 97955, "verified_income": 97955, "income_mismatch_flag": false, "income_stability": "CONSISTENT_6M", "mismatch_delta": 0}'::JSONB),
    ('APP-2026-00014', 4, 'BANK_STATEMENT_ANALYSIS', 'PASS', 'standard_pipeline', '{"bank_balance": 418243, "bounce_count": 0, "spending_ratio": 0.81, "negative_month_count": 0, "existing_emi_total": 25440}'::JSONB),
    ('APP-2026-00014', 5, 'CIBIL_FETCH', 'PASS', 'bank_analysis_complete', '{"cibil_score": 683, "default_flag": false, "written_off_flag": false, "credit_enquiries_6m": 0, "cibil_check": "above_threshold"}'::JSONB),
    ('APP-2026-00014', 6, 'FEATURE_ENGINEERING', 'PASS', 'all_api_calls_complete', '{"dti_ratio": 0.5045, "proposed_emi": 23982, "interest_rate": 10.5, "risk_score": "HIGH", "dti_band": "HIGH"}'::JSONB),
    ('APP-2026-00014', 7, 'DECISION_ENGINE', 'PASS', 'feature_engineering_complete', '{"decision": "REJECTED", "risk_category": "HIGH", "decision_reason_codes": "HIGH_DTI", "confidence_score": 90, "recommendation": "rejected", "hard_policy_breach": true}'::JSONB),
    ('APP-2026-00014', 8, 'FINAL_DECISION', 'PASS', 'decision_engine_complete', '{"final_decision": "REJECTED", "interest_rate": 10.5, "proposed_emi": 23982, "risk_category": "HIGH"}'::JSONB)
ON CONFLICT (application_id, step_order) DO NOTHING;

COMMIT;

-- ============================================================
-- VERIFICATION QUERIES — run after insert to sanity-check counts
-- ============================================================
-- SELECT 'applications',        COUNT(*) FROM applications;
-- SELECT 'kyc_api_table',        COUNT(*) FROM kyc_api_table;
-- SELECT 'cibil_api_table',      COUNT(*) FROM cibil_api_table;
-- SELECT 'bank_api_table',       COUNT(*) FROM bank_api_table;
-- SELECT 'income_api_table',     COUNT(*) FROM income_api_table;
-- SELECT 'document_analysis',   COUNT(*) FROM document_analysis_table;
-- SELECT 'decision_engine',     COUNT(*) FROM decision_engine_output;
-- SELECT 'application_timeline',COUNT(*) FROM application_timeline;
