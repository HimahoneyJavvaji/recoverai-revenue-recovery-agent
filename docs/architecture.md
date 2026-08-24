# RecoverAI Architecture

## High-Level Flow

Revenue Data
    ↓
Revenue-at-Risk Detection
    ↓
Promise-to-Pay Extraction
    ↓
Recovery Decision Agent
    ↓
Policy & Guardrails
    ↓
Action Executor
    ↓
Outcome Verification
    ↓
Metrics + Audit Trail

## AI Responsibilities

AI is responsible for:

- Understanding natural-language payment commitments.
- Extracting promise-to-pay information.
- Interpreting ambiguous customer communication.
- Recommending recovery actions.
- Generating context-aware recovery messages.

## Deterministic Responsibilities

Traditional application logic is responsible for:

- Financial calculations.
- Date calculations.
- Invoice/payment status.
- Policy enforcement.
- Stopping rules.
- Action authorization.
- API execution.
- Audit logging.