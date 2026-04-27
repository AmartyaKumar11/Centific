-- ============================================================
-- LOAN PREQUALIFICATION AGENT — PostgreSQL DDL (schema.sql)
-- Production-grade schema | Aiven PostgreSQL compatible
-- ============================================================
CREATE SCHEMA IF NOT EXISTS maria;
SET search_path TO maria;
-- ============================================================
-- ENUMS — Constrained categorical values for key fields
-- ============================================================

DO $$ BEGIN
    CREATE TYPE employer_type_enum      AS ENUM ('PRIVATE', 'GOVERNMENT', 'SELF_EMPLOYED', 'CONTRACT');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE decision_enum           AS ENUM ('APPROVED', 'REJECTED', 'REVIEW');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE risk_category_enum      AS ENUM ('LOW', 'MEDIUM', 'HIGH');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE income_stability_enum   AS ENUM ('CONSISTENT_6M', 'CONSISTENT_3M', 'ONE_ANOMALY', 'TWO_PLUS_ANOMALIES', 'IRREGULAR');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE step_status_enum        AS ENUM ('PASS', 'FAIL', 'FLAGGED', 'ESCALATED');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE step_name_enum          AS ENUM (
        'KYC_VALIDATION',
        'DOCUMENT_ANALYSIS',
        'INCOME_VERIFICATION',
        'BANK_STATEMENT_ANALYSIS',
        'CIBIL_FETCH',
        'FEATURE_ENGINEERING',
        'DECISION_ENGINE',
        'HIL_ESCALATION',
        'FINAL_DECISION'
    );
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- ============================================================
-- TABLE 1: applications
-- Master register — one row per loan application.
-- All child tables reference this via application_id (FK).
-- ============================================================

CREATE TABLE IF NOT EXISTS applications (
    application_id          VARCHAR(20)             PRIMARY KEY,
    pan_number              VARCHAR(10)             NOT NULL UNIQUE,
    applicant_name          VARCHAR(100)            NOT NULL,
    requested_loan_amount   INTEGER                 NOT NULL CHECK (requested_loan_amount > 0),
    requested_tenure_months INTEGER                 NOT NULL CHECK (requested_tenure_months IN (6,12,18,24,36,48,60,84,120)),
    application_date        TIMESTAMPTZ             NOT NULL,
    decision                decision_enum           NOT NULL,
    risk_category           risk_category_enum      NOT NULL,
    confidence_score        SMALLINT                NOT NULL CHECK (confidence_score BETWEEN 0 AND 100),
    hil_required_flag       BOOLEAN                 NOT NULL DEFAULT FALSE,
    decision_reason_codes   TEXT,
    created_at              TIMESTAMPTZ             NOT NULL DEFAULT NOW(),
    updated_at              TIMESTAMPTZ             NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE  applications IS 'Master loan application register. One row per applicant. Source of truth for application_id FK.';
COMMENT ON COLUMN applications.pan_number IS 'Indian Permanent Account Number — unique per individual, used as cross-table join key for API simulations.';
COMMENT ON COLUMN applications.decision_reason_codes IS 'Pipe-delimited reason codes e.g. LOW_CIBIL|HIGH_DTI|INCOME_MISMATCH. Parsed in rejection analysis queries.';
COMMENT ON COLUMN applications.confidence_score IS 'Model confidence 0–100. Values < 80 trigger HIL escalation in the agent pipeline.';

-- ============================================================
-- TABLE 2: kyc_api_table
-- Identity verification data — simulates KYC bureau API response.
-- ============================================================

CREATE TABLE IF NOT EXISTS kyc_api_table (
    kyc_id                  SERIAL                  PRIMARY KEY,
    application_id          VARCHAR(20)             NOT NULL REFERENCES applications(application_id) ON DELETE CASCADE,
    pan_number              VARCHAR(10)             NOT NULL,
    applicant_name          VARCHAR(100)            NOT NULL,
    aadhaar_number          BIGINT                  NOT NULL,   -- 12-digit Aadhaar; stored as BIGINT (too large for INTEGER)
    date_of_birth           DATE                    NOT NULL,
    phone_number            BIGINT                  NOT NULL,   -- Indian mobile numbers including country code (91XXXXXXXXXX)
    email                   VARCHAR(150)            NOT NULL CHECK (email LIKE '%@%'),
    address                 TEXT                    NOT NULL,
    employer_name           VARCHAR(100)            NOT NULL,
    employer_type           employer_type_enum      NOT NULL,
    employment_tenure_years NUMERIC(5,1)            NOT NULL CHECK (employment_tenure_years >= 0),
    data_consistency_flag   BOOLEAN                 NOT NULL,
    created_at              TIMESTAMPTZ             NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_kyc_application UNIQUE (application_id)      -- one KYC record per application
);

COMMENT ON TABLE  kyc_api_table IS 'KYC bureau response per application. Contains identity, employment, and contact details.';
COMMENT ON COLUMN kyc_api_table.aadhaar_number IS '12-digit government-issued biometric ID. Stored as BIGINT to avoid leading-zero truncation issues.';
COMMENT ON COLUMN kyc_api_table.data_consistency_flag IS 'TRUE if KYC data is internally consistent across submitted documents; FALSE triggers further review.';

-- ============================================================
-- TABLE 3: cibil_api_table
-- Credit bureau data — simulates TransUnion CIBIL API response.
-- ============================================================

CREATE TABLE IF NOT EXISTS cibil_api_table (
    cibil_id                SERIAL                  PRIMARY KEY,
    application_id          VARCHAR(20)             NOT NULL REFERENCES applications(application_id) ON DELETE CASCADE,
    pan_number              VARCHAR(10)             NOT NULL,
    cibil_score             SMALLINT                NOT NULL CHECK (cibil_score BETWEEN 300 AND 900),
    default_flag            BOOLEAN                 NOT NULL,
    written_off_flag        BOOLEAN                 NOT NULL,
    credit_enquiries_6m     SMALLINT                NOT NULL CHECK (credit_enquiries_6m >= 0),
    negative_items_count    NUMERIC(4,1),           -- nullable: not always returned by bureau
    oldest_account_years    NUMERIC(4,1),
    inquiries_12m           NUMERIC(4,1),
    accounts_good_standing  NUMERIC(4,1),
    derogatory_marks        NUMERIC(4,1),
    created_at              TIMESTAMPTZ             NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_cibil_application UNIQUE (application_id)
);

COMMENT ON TABLE  cibil_api_table IS 'CIBIL credit bureau response. Nullable credit history fields reflect sparse bureau data for thin-file applicants.';
COMMENT ON COLUMN cibil_api_table.cibil_score IS 'Range 300–900. Scores < 620 = POOR; 620–699 = FAIR; 700–749 = GOOD; 750+ = EXCELLENT.';
COMMENT ON COLUMN cibil_api_table.written_off_flag IS 'TRUE if any previous loan was written off by a lender — hard rejection trigger in the decision engine.';

-- ============================================================
-- TABLE 4: bank_api_table
-- Banking behaviour — simulates bank statement API / AA aggregator.
-- ============================================================

CREATE TABLE IF NOT EXISTS bank_api_table (
    bank_id                 SERIAL                  PRIMARY KEY,
    application_id          VARCHAR(20)             NOT NULL REFERENCES applications(application_id) ON DELETE CASCADE,
    pan_number              VARCHAR(10)             NOT NULL,
    bank_balance            INTEGER                 NOT NULL CHECK (bank_balance >= 0),
    bounce_count            SMALLINT                NOT NULL CHECK (bounce_count >= 0),
    statement_months        SMALLINT                NOT NULL CHECK (statement_months BETWEEN 1 AND 24),
    spending_ratio          NUMERIC(5,2)            NOT NULL CHECK (spending_ratio BETWEEN 0 AND 1),
    negative_month_count    SMALLINT                NOT NULL CHECK (negative_month_count >= 0),
    existing_emi_total      INTEGER                 NOT NULL CHECK (existing_emi_total >= 0),
    created_at              TIMESTAMPTZ             NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_bank_application UNIQUE (application_id)
);

COMMENT ON TABLE  bank_api_table IS 'Bank statement analysis output per application. Covers liquidity, behaviour, and existing obligations.';
COMMENT ON COLUMN bank_api_table.spending_ratio IS 'Monthly expenditure / monthly credit. Range 0–1. Values > 0.7 indicate financial stress.';
COMMENT ON COLUMN bank_api_table.negative_month_count IS 'Months where account balance went negative during the statement period.';

-- ============================================================
-- TABLE 5: income_api_table
-- Income verification — cross-references declared vs verified income.
-- ============================================================

CREATE TABLE IF NOT EXISTS income_api_table (
    income_id               SERIAL                  PRIMARY KEY,
    application_id          VARCHAR(20)             NOT NULL REFERENCES applications(application_id) ON DELETE CASCADE,
    pan_number              VARCHAR(10)             NOT NULL,
    gross_salary            INTEGER                 NOT NULL CHECK (gross_salary > 0),
    total_deductions        INTEGER                 NOT NULL CHECK (total_deductions >= 0),
    declared_income         INTEGER                 NOT NULL CHECK (declared_income > 0),
    verified_income         INTEGER                 NOT NULL CHECK (verified_income >= 0),
    income_mismatch_flag    BOOLEAN                 NOT NULL,
    income_stability        income_stability_enum   NOT NULL,
    created_at              TIMESTAMPTZ             NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_income_application UNIQUE (application_id),
    CONSTRAINT chk_deductions_lte_gross CHECK (total_deductions <= gross_salary)
);

COMMENT ON TABLE  income_api_table IS 'Income verification layer. declared_income vs verified_income delta drives income_mismatch_flag.';
COMMENT ON COLUMN income_api_table.income_mismatch_flag IS 'TRUE when |declared - verified| exceeds threshold (typically >10%). Triggers BANK_STATEMENT_ANALYSIS step in agent.';
COMMENT ON COLUMN income_api_table.income_stability IS 'Enum reflecting 6-month salary pattern. TWO_PLUS_ANOMALIES is a soft rejection signal.';

-- ============================================================
-- TABLE 6: document_analysis_table
-- OCR and document consistency — simulates LLM document analysis.
-- ============================================================

CREATE TABLE IF NOT EXISTS document_analysis_table (
    doc_id                  SERIAL                  PRIMARY KEY,
    application_id          VARCHAR(20)             NOT NULL REFERENCES applications(application_id) ON DELETE CASCADE,
    pan_number              VARCHAR(10)             NOT NULL,
    ocr_confidence_score    SMALLINT                NOT NULL CHECK (ocr_confidence_score BETWEEN 0 AND 100),
    document_consistency_flag BOOLEAN               NOT NULL,
    data_consistency_flag   BOOLEAN                 NOT NULL,
    created_at              TIMESTAMPTZ             NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_doc_application UNIQUE (application_id)
);

COMMENT ON TABLE  document_analysis_table IS 'LLM-driven OCR and document consistency check results.';
COMMENT ON COLUMN document_analysis_table.ocr_confidence_score IS 'Confidence of OCR extraction 0–100. < 75 = FLAGGED in DOCUMENT_ANALYSIS pipeline step.';
COMMENT ON COLUMN document_analysis_table.document_consistency_flag IS 'TRUE if all uploaded documents are mutually consistent (no field contradictions).';
COMMENT ON COLUMN document_analysis_table.data_consistency_flag IS 'TRUE if extracted data matches KYC data; FALSE triggers additional human review.';

-- ============================================================
-- TABLE 7: decision_engine_output
-- Final underwriting output — one row per application decision.
-- ============================================================

CREATE TABLE IF NOT EXISTS decision_engine_output (
    decision_id             SERIAL                  PRIMARY KEY,
    application_id          VARCHAR(20)             NOT NULL REFERENCES applications(application_id) ON DELETE CASCADE,
    pan_number              VARCHAR(10)             NOT NULL,
    decision                decision_enum           NOT NULL,
    risk_category           risk_category_enum      NOT NULL,
    decision_reason_codes   TEXT,
    confidence_score        SMALLINT                NOT NULL CHECK (confidence_score BETWEEN 0 AND 100),
    hil_required_flag       BOOLEAN                 NOT NULL DEFAULT FALSE,
    interest_rate           NUMERIC(5,2)            NOT NULL CHECK (interest_rate > 0),
    proposed_emi            INTEGER                 NOT NULL CHECK (proposed_emi > 0),
    dti_ratio               NUMERIC(8,6)            NOT NULL CHECK (dti_ratio >= 0),
    created_at              TIMESTAMPTZ             NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_decision_application UNIQUE (application_id)
);

COMMENT ON TABLE  decision_engine_output IS 'Underwriting decision produced by the AI decision engine after all API calls complete.';
COMMENT ON COLUMN decision_engine_output.dti_ratio IS 'Debt-to-Income ratio = (existing_emi + proposed_emi) / verified_income. > 0.5 is HIGH risk trigger.';
COMMENT ON COLUMN decision_engine_output.interest_rate IS 'Proposed annual interest rate in %. Ranges: LOW risk = 6.5–8.5%, MEDIUM = 10.5%, HIGH = 13.5%.';

-- ============================================================
-- TABLE 8: application_timeline
-- Agent reasoning trace — one row per pipeline step per application.
-- JSONB output_data holds structured step-level metadata.
-- ============================================================

CREATE TABLE IF NOT EXISTS application_timeline (
    timeline_id             SERIAL                  PRIMARY KEY,
    application_id          VARCHAR(20)             NOT NULL REFERENCES applications(application_id) ON DELETE CASCADE,
    step_order              SMALLINT                NOT NULL CHECK (step_order >= 1),
    step_name               step_name_enum          NOT NULL,
    step_status             step_status_enum        NOT NULL,
    triggered_by            VARCHAR(150),
    output_data             JSONB,
    created_at              TIMESTAMPTZ             NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_timeline_step UNIQUE (application_id, step_order)
);

COMMENT ON TABLE  application_timeline IS 'Full agent reasoning trace. Each row is one processing step for one application. JSONB allows flexible per-step metadata.';
COMMENT ON COLUMN application_timeline.output_data IS 'JSONB blob containing step-specific outputs: scores, flags, deltas, escalation reasons, etc.';
COMMENT ON COLUMN application_timeline.triggered_by IS 'Human-readable trigger string explaining what caused this step to execute.';

-- ============================================================
-- INDEXES — Optimised for the query patterns in sample_queries.sql
-- ============================================================

-- Primary API simulation lookups by PAN number
CREATE INDEX IF NOT EXISTS idx_kyc_pan              ON kyc_api_table(pan_number);
CREATE INDEX IF NOT EXISTS idx_cibil_pan            ON cibil_api_table(pan_number);
CREATE INDEX IF NOT EXISTS idx_bank_pan             ON bank_api_table(pan_number);
CREATE INDEX IF NOT EXISTS idx_income_pan           ON income_api_table(pan_number);
CREATE INDEX IF NOT EXISTS idx_doc_pan              ON document_analysis_table(pan_number);
CREATE INDEX IF NOT EXISTS idx_decision_pan         ON decision_engine_output(pan_number);

-- FK join performance (child → parent)
CREATE INDEX IF NOT EXISTS idx_kyc_app              ON kyc_api_table(application_id);
CREATE INDEX IF NOT EXISTS idx_cibil_app            ON cibil_api_table(application_id);
CREATE INDEX IF NOT EXISTS idx_bank_app             ON bank_api_table(application_id);
CREATE INDEX IF NOT EXISTS idx_income_app           ON income_api_table(application_id);
CREATE INDEX IF NOT EXISTS idx_doc_app              ON document_analysis_table(application_id);
CREATE INDEX IF NOT EXISTS idx_decision_app         ON decision_engine_output(application_id);
CREATE INDEX IF NOT EXISTS idx_timeline_app         ON application_timeline(application_id);

-- Ordered step retrieval for agent trace replay
CREATE INDEX IF NOT EXISTS idx_timeline_app_order   ON application_timeline(application_id, step_order ASC);

-- HIL queue — partial index on flagged applications only
CREATE INDEX IF NOT EXISTS idx_apps_hil_queue       ON applications(risk_category, confidence_score)
    WHERE hil_required_flag = TRUE;

-- Decision analysis
CREATE INDEX IF NOT EXISTS idx_apps_decision        ON applications(decision);
CREATE INDEX IF NOT EXISTS idx_decision_risk        ON decision_engine_output(risk_category, decision);

-- Timeline escalation/failure monitoring
CREATE INDEX IF NOT EXISTS idx_timeline_status      ON application_timeline(step_status)
    WHERE step_status IN ('ESCALATED', 'FLAGGED', 'FAIL');

-- JSONB index on output_data for escalation reason queries
CREATE INDEX IF NOT EXISTS idx_timeline_output_gin  ON application_timeline USING GIN (output_data);

-- ============================================================
-- TRIGGER: auto-update updated_at on applications row change
-- ============================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_applications_updated_at ON applications;
CREATE TRIGGER trg_applications_updated_at
    BEFORE UPDATE ON applications
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
