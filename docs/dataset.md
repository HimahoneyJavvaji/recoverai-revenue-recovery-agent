# RecoverAI Synthetic Dataset

## Purpose

RecoverAI uses synthetic merchant revenue data to evaluate revenue recovery across a batch of cases.

The dataset is designed to simulate realistic revenue-risk scenarios without using real customer data.

## Initial Scenarios

### 1. Failed Payment

A payment attempt fails against an invoice.

Expected recovery flow:

Payment Failure
→ Risk Detection
→ Recovery Decision
→ Bounded Action
→ Successful Payment
→ Recovery Verification

### 2. Overdue Invoice

An invoice remains unpaid after its due date.

Expected recovery flow:

Overdue Detection
→ Risk Assessment
→ Reminder
→ Payment
→ Recovery Verification

### 3. Broken Promise-to-Pay

A customer promises to pay by a specific date but does not pay.

Expected recovery flow:

Promise Extraction
→ Promise Monitoring
→ Broken Promise Detection
→ Recovery Action
→ Payment Verification

## Dataset Requirements

The generator must:

- Produce deterministic data using a fixed random seed.
- Generate multiple customers.
- Generate multiple invoices.
- Generate payment attempts.
- Generate realistic revenue-risk cases.
- Include successful and unsuccessful recovery outcomes.
- Support batch evaluation.
- Never use real customer data.

## Money Representation

All monetary values are stored as integer paise.

Example:

₹10,000.00 = 1,000,000 paise.

## Evaluation

The dataset will eventually be used to measure:

- Revenue at risk
- Revenue recovered
- Recovery rate
- Action success rate
- Escalations
- Stopped cases
- Failed recovery attempts