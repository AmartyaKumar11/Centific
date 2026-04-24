# MASTER_CONTEXT.md

## AI-Infused BFSI Loan Prequalification Agent (MVP)

---

## 1. PRIMARY GOAL (VERY IMPORTANT)

The goal of this project is to build a:

> **Virtual Dashboard UI for a Loan Prequalification Agent**

This dashboard is used by a **Credit Manager** to:

* View all loan applications
* Understand agent-generated decisions
* Inspect step-by-step agent reasoning
* Review flagged cases (HIL)
* Make final approval/rejection decisions

---

## 2. WHAT IS BEING BUILT RIGHT NOW

Current focus:

> **Frontend-first system that visualizes the behavior of an AI Loan Prequalification Agent**

The system must simulate:

* Agent processing flow
* Tool calls (KYC, CIBIL, Income, Bank)
* Decision logic
* Confidence scoring
* Human-in-the-Loop escalation

---

## 3. WHAT THIS IS NOT (IMPORTANT)

This is NOT currently:

* A production backend system
* A real API-integrated system
* A machine learning model

Instead:

> The system simulates agent behavior using structured data

---

## 4. SYSTEM OVERVIEW

This system represents a **Virtual Loan Officer Agent** operating inside a BFSI workflow.

The agent:

1. Ingests applicant data
2. Extracts structured information
3. Validates across multiple sources
4. Detects inconsistencies
5. Computes financial metrics (DTI, EMI)
6. Generates a recommendation
7. Escalates to Human-in-the-Loop (HIL)

---

## 5. FRONTEND-FIRST APPROACH

The frontend defines:

* Data structure
* API contract
* System behavior

The backend (FastAPI + Postgres) will be built AFTER the frontend is finalized.

---

## 6. CORE UX REQUIREMENTS

### Dashboard must show:

* Total applications
* Approved / Rejected / Review
* Risk distribution
* Confidence distribution
* HIL queue

---

### Application Table:

Each row includes:

* applicant_name
* loan_amount
* decision
* risk
* confidence_score
* hil_required_flag
* created_at

---

### Application Detail View (CRITICAL)

When a row is clicked:

The UI must display:

#### 1. Application Summary

* Income (declared vs verified)
* CIBIL score
* DTI
* Risk category
* Decision + reasons

---

#### 2. Agent Timeline (CORE FEATURE)

The UI must show a **step-by-step execution timeline** of the agent.

This includes:

1. KYC Validation
2. CIBIL Fetch
3. Income Validation
4. Conditional steps (Bank API if mismatch)
5. Decision Engine
6. HIL Escalation

Each step must display:

* step_name
* tool_name
* status
* trigger_reason (if conditional)
* reasoning
* output_data

---

## 7. KEY IDEA

This system is designed to:

> **Show HOW the agent thinks, not just WHAT it decides**

---

## 8. DATA SOURCE

Currently:

* Data comes from a pre-generated dataset (Excel)
* Timeline is dynamically generated from data
* Tool calls are simulated

---

## 9. NEXT PHASE (NOT CURRENT FOCUS)

Later:

* Backend (FastAPI)
* Database (Postgres on Aiven)
* API layer
* Real tool integrations

---

## 10. FINAL SUMMARY

This project builds a:

> **Visual, explainable interface for an AI-driven loan prequalification agent**

The emphasis is on:

* Transparency
* Explainability
* Structured reasoning
* Human oversight

---

END OF CONTEXT
