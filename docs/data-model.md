# RecoverAI Data Model

## Purpose

The RecoverAI data model supports the complete revenue recovery lifecycle:

1. Detect revenue at risk
2. Understand why the revenue is at risk
3. Determine an appropriate intervention
4. Execute a bounded recovery action
5. Record the outcome
6. Measure recovered money
7. Maintain a complete audit trail

---

# Core Entities

## 1. Customer

Represents the merchant's customer who owes or may owe money.

### Fields

- `id` - Unique customer identifier
- `name` - Customer name
- `email` - Customer email
- `phone` - Customer phone number
- `segment` - Customer segment such as SMB, MID_MARKET, or ENTERPRISE
- `created_at` - Customer creation timestamp

---

## 2. Invoice

Represents money owed by a customer.

### Fields

- `id` - Unique invoice identifier
- `customer_id` - Customer who owes the money
- `invoice_number` - Human-readable invoice number
- `amount` - Original invoice amount
- `outstanding_amount` - Amount currently unpaid
- `due_date` - Invoice due date
- `status` - Invoice status
- `created_at` - Invoice creation timestamp

### Invoice statuses

- `OPEN`
- `PARTIALLY_PAID`
- `PAID`
- `OVERDUE`
- `CANCELLED`

---

## 3. Payment

Represents an actual payment received against an invoice.

### Fields

- `id` - Unique payment identifier
- `invoice_id` - Invoice being paid
- `amount` - Payment amount
- `payment_date` - Payment timestamp
- `status` - Payment status
- `reference` - External or simulated payment reference

### Payment statuses

- `SUCCESS`
- `FAILED`
- `PENDING`
- `REFUNDED`

A recovery amount is counted as recovered only when the corresponding payment has a `SUCCESS` status.

---

## 4. Communication

Represents communication between the merchant and customer.

### Fields

- `id` - Unique communication identifier
- `customer_id` - Customer involved
- `invoice_id` - Related invoice, if applicable
- `channel` - Communication channel
- `direction` - INBOUND or OUTBOUND
- `message` - Communication content
- `timestamp` - Communication timestamp

### Channels

- `EMAIL`
- `SMS`
- `WHATSAPP`
- `VOICE`
- `OTHER`

---

## 5. PromiseToPay

Represents a structured payment commitment extracted from a customer communication.

### Fields

- `id` - Unique promise identifier
- `customer_id` - Customer making the promise
- `invoice_id` - Invoice associated with the promise
- `source_communication_id` - Communication from which the promise was extracted
- `promised_amount` - Amount promised
- `promise_date` - Date by which payment is promised
- `status` - Current promise status
- `confidence` - AI extraction confidence
- `created_at` - Promise creation timestamp

### Promise statuses

- `PENDING`
- `FULFILLED`
- `PARTIALLY_FULFILLED`
- `BROKEN`
- `CANCELLED`

---

## 6. RecoveryCase

Represents a revenue recovery problem being handled by RecoverAI.

### Fields

- `id` - Unique recovery case identifier
- `customer_id` - Customer associated with the case
- `invoice_id` - Invoice associated with the case
- `risk_amount` - Amount currently considered at risk
- `risk_reason` - Why the revenue is at risk
- `priority` - Recovery priority
- `status` - Current case status
- `created_at` - Case creation timestamp
- `updated_at` - Last update timestamp

### Risk reasons

- `PAYMENT_FAILED`
- `CHECKOUT_ABANDONED`
- `SUBSCRIPTION_FAILED`
- `INVOICE_OVERDUE`
- `PROMISE_BROKEN`
- `PAYMENT_DEGRADED`

### Case priorities

- `LOW`
- `MEDIUM`
- `HIGH`
- `CRITICAL`

### Case statuses

- `ACTIVE`
- `RECOVERED`
- `ESCALATED`
- `STOPPED`
- `CLOSED`

---

## 7. RecoveryAction

Represents an action proposed or executed by the recovery system.

### Fields

- `id` - Unique action identifier
- `case_id` - Recovery case associated with the action
- `action_type` - Type of recovery action
- `reason` - Why this action was selected
- `status` - Action execution status
- `attempt_number` - Number of recovery attempts
- `executed_at` - Execution timestamp
- `result` - Result of the action
- `recovered_amount` - Amount recovered as a direct result of the action

### Action types

- `WAIT`
- `SEND_REMINDER`
- `SEND_PAYMENT_LINK`
- `RETRY_PAYMENT`
- `REQUEST_PROMISE`
- `ESCALATE`
- `STOP`

### Action statuses

- `PROPOSED`
- `APPROVED`
- `EXECUTED`
- `FAILED`
- `BLOCKED`

An action must not be considered successful merely because it was executed.

Money recovered must be verified through a successful payment.

---

## 8. AuditEvent

Records important decisions, policy checks, actions, failures, and outcomes.

### Fields

- `id` - Unique audit event identifier
- `case_id` - Related recovery case
- `event_type` - Type of event
- `actor` - HUMAN, AI_AGENT, or SYSTEM
- `description` - Human-readable explanation
- `metadata` - Additional structured information
- `timestamp` - Event timestamp

### Example event types

- `CASE_CREATED`
- `RISK_DETECTED`
- `AI_DECISION`
- `POLICY_CHECK`
- `ACTION_PROPOSED`
- `ACTION_EXECUTED`
- `ACTION_FAILED`
- `PAYMENT_VERIFIED`
- `CASE_ESCALATED`
- `CASE_STOPPED`
- `CASE_RECOVERED`

---

# Relationships

```text
Customer
  |
  +---- Invoice
  |       |
  |       +---- Payment
  |       |
  |       +---- RecoveryCase
  |               |
  |               +---- RecoveryAction
  |               |
  |               +---- AuditEvent
  |
  +---- Communication
          |
          +---- PromiseToPay