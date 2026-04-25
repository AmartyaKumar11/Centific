-- ============================================================
-- LOAN PREQUALIFICATION AGENT - PostgreSQL Schema
-- Compatible with Aiven Postgres (SSL enabled)
-- ============================================================

-- ============================================================
-- TABLE 1: applications (master application register)
-- ============================================================
CREATE TABLE IF NOT EXISTS applications (
    application_id          VARCHAR(20)     PRIMARY KEY,
    pan_number              VARCHAR(10)     NOT NULL UNIQUE,
    applicant_name          VARCHAR(100)    NOT NULL,
    requested_loan_amount   INTEGER         NOT NULL,
    requested_tenure_months INTEGER         NOT NULL,
    application_date        TIMESTAMPTZ     NOT NULL,
    decision                VARCHAR(20)     NOT NULL,
    risk_category           VARCHAR(20)     NOT NULL,
    confidence_score        INTEGER         NOT NULL,
    hil_required_flag       BOOLEAN         NOT NULL,
    decision_reason_codes   TEXT,
    created_at              TIMESTAMPTZ     DEFAULT NOW()
);

-- ============================================================
-- TABLE 2: kyc_api_table (identity verification)
-- ============================================================
CREATE TABLE IF NOT EXISTS kyc_api_table (
    kyc_id                  SERIAL          PRIMARY KEY,
    application_id          VARCHAR(20)     NOT NULL REFERENCES applications(application_id),
    pan_number              VARCHAR(10)     NOT NULL,
    applicant_name          VARCHAR(100)    NOT NULL,
    aadhaar_number          BIGINT          NOT NULL,
    date_of_birth           DATE            NOT NULL,
    phone_number            BIGINT          NOT NULL,
    email                   VARCHAR(150)    NOT NULL,
    address                 TEXT            NOT NULL,
    employer_name           VARCHAR(100)    NOT NULL,
    employer_type           VARCHAR(20)     NOT NULL,
    employment_tenure_years NUMERIC(5,1)    NOT NULL,
    data_consistency_flag   BOOLEAN         NOT NULL,
    created_at              TIMESTAMPTZ     DEFAULT NOW()
);

-- ============================================================
-- TABLE 3: cibil_api_table (credit bureau data)
-- ============================================================
CREATE TABLE IF NOT EXISTS cibil_api_table (
    cibil_id                SERIAL          PRIMARY KEY,
    application_id          VARCHAR(20)     NOT NULL REFERENCES applications(application_id),
    pan_number              VARCHAR(10)     NOT NULL,
    cibil_score             INTEGER         NOT NULL,
    default_flag            BOOLEAN         NOT NULL,
    written_off_flag        BOOLEAN         NOT NULL,
    credit_enquiries_6m     INTEGER         NOT NULL,
    negative_items_count    NUMERIC(4,1),
    oldest_account_years    NUMERIC(4,1),
    inquiries_12m           NUMERIC(4,1),
    accounts_good_standing  NUMERIC(4,1),
    derogatory_marks        NUMERIC(4,1),
    created_at              TIMESTAMPTZ     DEFAULT NOW()
);

-- ============================================================
-- TABLE 4: bank_api_table (banking behaviour)
-- ============================================================
CREATE TABLE IF NOT EXISTS bank_api_table (
    bank_id                 SERIAL          PRIMARY KEY,
    application_id          VARCHAR(20)     NOT NULL REFERENCES applications(application_id),
    pan_number              VARCHAR(10)     NOT NULL,
    bank_balance            INTEGER         NOT NULL,
    bounce_count            INTEGER         NOT NULL,
    statement_months        INTEGER         NOT NULL,
    spending_ratio          NUMERIC(5,2)    NOT NULL,
    negative_month_count    INTEGER         NOT NULL,
    existing_emi_total      INTEGER         NOT NULL,
    created_at              TIMESTAMPTZ     DEFAULT NOW()
);

-- ============================================================
-- TABLE 5: income_api_table (income verification)
-- ============================================================
CREATE TABLE IF NOT EXISTS income_api_table (
    income_id               SERIAL          PRIMARY KEY,
    application_id          VARCHAR(20)     NOT NULL REFERENCES applications(application_id),
    pan_number              VARCHAR(10)     NOT NULL,
    gross_salary            INTEGER         NOT NULL,
    total_deductions        INTEGER         NOT NULL,
    declared_income         INTEGER         NOT NULL,
    verified_income         INTEGER         NOT NULL,
    income_mismatch_flag    BOOLEAN         NOT NULL,
    income_stability        VARCHAR(30)     NOT NULL,
    created_at              TIMESTAMPTZ     DEFAULT NOW()
);

-- ============================================================
-- TABLE 6: document_analysis_table (OCR & doc consistency)
-- ============================================================
CREATE TABLE IF NOT EXISTS document_analysis_table (
    doc_id                  SERIAL          PRIMARY KEY,
    application_id          VARCHAR(20)     NOT NULL REFERENCES applications(application_id),
    pan_number              VARCHAR(10)     NOT NULL,
    ocr_confidence_score    INTEGER         NOT NULL,
    document_consistency_flag BOOLEAN       NOT NULL,
    data_consistency_flag   BOOLEAN         NOT NULL,
    created_at              TIMESTAMPTZ     DEFAULT NOW()
);

-- ============================================================
-- TABLE 7: decision_engine_output (final underwriting output)
-- ============================================================
CREATE TABLE IF NOT EXISTS decision_engine_output (
    decision_id             SERIAL          PRIMARY KEY,
    application_id          VARCHAR(20)     NOT NULL REFERENCES applications(application_id),
    pan_number              VARCHAR(10)     NOT NULL,
    decision                VARCHAR(20)     NOT NULL,
    risk_category           VARCHAR(20)     NOT NULL,
    decision_reason_codes   TEXT,
    confidence_score        INTEGER         NOT NULL,
    hil_required_flag       BOOLEAN         NOT NULL,
    interest_rate           NUMERIC(5,2)    NOT NULL,
    proposed_emi            INTEGER         NOT NULL,
    dti_ratio               NUMERIC(8,6)    NOT NULL,
    created_at              TIMESTAMPTZ     DEFAULT NOW()
);

-- ============================================================
-- TABLE 8: application_timeline (agent reasoning trace)
-- ============================================================
CREATE TABLE IF NOT EXISTS application_timeline (
    timeline_id             SERIAL          PRIMARY KEY,
    application_id          VARCHAR(20)     NOT NULL REFERENCES applications(application_id),
    step_order              INTEGER         NOT NULL,
    step_name               VARCHAR(50)     NOT NULL,
    step_status             VARCHAR(20)     NOT NULL,   -- PASS / FAIL / FLAGGED / ESCALATED
    triggered_by            VARCHAR(100),               -- what caused this step
    output_data             JSONB,                      -- structured step output
    created_at              TIMESTAMPTZ     DEFAULT NOW()
);

-- ============================================================
-- INDEXES for fast API simulation queries
-- ============================================================
CREATE INDEX IF NOT EXISTS idx_kyc_pan          ON kyc_api_table(pan_number);
CREATE INDEX IF NOT EXISTS idx_kyc_app          ON kyc_api_table(application_id);
CREATE INDEX IF NOT EXISTS idx_cibil_pan        ON cibil_api_table(pan_number);
CREATE INDEX IF NOT EXISTS idx_cibil_app        ON cibil_api_table(application_id);
CREATE INDEX IF NOT EXISTS idx_bank_pan         ON bank_api_table(pan_number);
CREATE INDEX IF NOT EXISTS idx_bank_app         ON bank_api_table(application_id);
CREATE INDEX IF NOT EXISTS idx_income_pan       ON income_api_table(pan_number);
CREATE INDEX IF NOT EXISTS idx_income_app       ON income_api_table(application_id);
CREATE INDEX IF NOT EXISTS idx_doc_pan          ON document_analysis_table(pan_number);
CREATE INDEX IF NOT EXISTS idx_doc_app          ON document_analysis_table(application_id);
CREATE INDEX IF NOT EXISTS idx_decision_pan     ON decision_engine_output(pan_number);
CREATE INDEX IF NOT EXISTS idx_decision_app     ON decision_engine_output(application_id);
CREATE INDEX IF NOT EXISTS idx_timeline_app     ON application_timeline(application_id);
CREATE INDEX IF NOT EXISTS idx_timeline_order   ON application_timeline(application_id, step_order);
