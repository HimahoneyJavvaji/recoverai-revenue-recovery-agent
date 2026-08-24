# RecoverAI Product Specification

## Problem

B2B merchants lose revenue when invoices become overdue and customer payment commitments are not systematically tracked.

Customers may communicate payment promises such as:

- "We'll pay ₹50,000 on Friday."
- "We'll pay half this month and the rest next month."
- "Give us another 10 days."

These commitments are often handled manually, resulting in missed follow-ups, delayed collections, and avoidable revenue loss.

## Solution

RecoverAI is an AI-powered revenue recovery agent that:

1. Detects revenue at risk.
2. Understands customer payment commitments.
3. Tracks promise-to-pay commitments.
4. Determines the appropriate recovery intervention.
5. Executes only policy-approved actions.
6. Verifies payment outcomes.
7. Measures recovered revenue.
8. Maintains a complete audit trail.

## Target User

B2B merchants and finance/collections teams.

## MVP

The MVP focuses on overdue B2B invoices and promise-to-pay tracking.

## Recovery Actions

- Wait
- Send reminder
- Create payment request
- Escalate to human
- Stop recovery

## Core Metrics

- Revenue at risk
- Revenue recovered
- Recovery rate
- Number of recovery interventions
- Number of escalations
- Number of stopped cases
- AI decision accuracy
- Policy violations prevented

## Safety Principles

- AI cannot bypass policy controls.
- Financial calculations are deterministic.
- Payment actions are bounded.
- High-value cases can require human approval.
- Every action is logged.
- Failed actions are handled safely.