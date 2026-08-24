from datetime import datetime, timedelta, timezone

from backend.app.database import SessionLocal
from backend.app.models import (
    AuditEvent,
    Customer,
    Invoice,
    Payment,
    RecoveryAction,
    RecoveryCase,
)


def utc_now() -> datetime:
    """Return the current timezone-aware UTC datetime."""
    return datetime.now(timezone.utc)


def run_smoke_test() -> None:
    db = SessionLocal()

    try:
        # ---------------------------------------------------------
        # 1. Create customer
        # ---------------------------------------------------------
        customer = Customer(
            name="Smoke Test Customer",
            email="smoke@example.com",
            phone="+910000000000",
            segment="SMB",
        )

        db.add(customer)
        db.flush()

        # ---------------------------------------------------------
        # 2. Create overdue invoice
        #
        # Money is stored in integer paise.
        # ₹10,000.00 = 1,000,000 paise
        # ---------------------------------------------------------
        invoice = Invoice(
            customer_id=customer.id,
            invoice_number="SMOKE-001",
            amount=1_000_000,
            outstanding_amount=1_000_000,
            due_date=utc_now().date() - timedelta(days=5),
            status="OVERDUE",
        )

        db.add(invoice)
        db.flush()

        # ---------------------------------------------------------
        # 3. Create failed payment
        # ---------------------------------------------------------
        failed_payment = Payment(
            invoice_id=invoice.id,
            amount=1_000_000,
            payment_date=utc_now(),
            status="FAILED",
            reference="smoke-failed-001",
        )

        db.add(failed_payment)
        db.flush()

        # ---------------------------------------------------------
        # 4. Create recovery case
        # ---------------------------------------------------------
        recovery_case = RecoveryCase(
            customer_id=customer.id,
            invoice_id=invoice.id,
            risk_amount=1_000_000,
            risk_reason="PAYMENT_FAILED",
            priority="HIGH",
            status="ACTIVE",
        )

        db.add(recovery_case)
        db.flush()

        # ---------------------------------------------------------
        # 5. Create recovery action
        # ---------------------------------------------------------
        action = RecoveryAction(
            case_id=recovery_case.id,
            action_type="SEND_PAYMENT_LINK",
            reason="Previous payment failed and invoice is overdue.",
            status="EXECUTED",
            attempt_number=1,
            executed_at=utc_now(),
            result="Payment link sent successfully.",
            recovered_amount=0,
        )

        db.add(action)
        db.flush()

        # ---------------------------------------------------------
        # 6. Simulate successful recovery payment
        # ---------------------------------------------------------
        successful_payment = Payment(
            invoice_id=invoice.id,
            amount=1_000_000,
            payment_date=utc_now(),
            status="SUCCESS",
            reference="smoke-success-001",
        )

        db.add(successful_payment)
        db.flush()

        # A recovery action is only considered financially successful
        # when a SUCCESS payment proves the recovered amount.
        action.payment_id = successful_payment.id
        action.recovered_amount = successful_payment.amount

        # ---------------------------------------------------------
        # 7. Update invoice
        # ---------------------------------------------------------
        invoice.outstanding_amount = 0
        invoice.status = "PAID"

        # ---------------------------------------------------------
        # 8. Update recovery case
        # ---------------------------------------------------------
        recovery_case.status = "RECOVERED"

        # ---------------------------------------------------------
        # 9. Record audit event
        # ---------------------------------------------------------
        audit_event = AuditEvent(
            case_id=recovery_case.id,
            event_type="PAYMENT_VERIFIED",
            actor="SYSTEM",
            description=(
                "Successful payment verified as recovery "
                "for the recovery case."
            ),
            event_metadata={
                "payment_id": successful_payment.id,
                "amount_paise": successful_payment.amount,
            },
            timestamp=utc_now(),
        )

        db.add(audit_event)

        # ---------------------------------------------------------
        # 10. Commit everything
        # ---------------------------------------------------------
        db.commit()

        print("DATABASE SMOKE TEST PASSED")
        print("--------------------------------")
        print(f"Customer ID:          {customer.id}")
        print(f"Invoice ID:           {invoice.id}")
        print(f"Failed Payment ID:    {failed_payment.id}")
        print(f"Recovery Case ID:     {recovery_case.id}")
        print(f"Recovery Action ID:   {action.id}")
        print(f"Success Payment ID:   {successful_payment.id}")
        print(f"Recovered Amount:     ₹{successful_payment.amount / 100:,.2f}")
        print(f"Invoice Status:       {invoice.status}")
        print(f"Case Status:          {recovery_case.status}")
        print(f"Verified Payment ID:  {action.payment_id}")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    run_smoke_test()