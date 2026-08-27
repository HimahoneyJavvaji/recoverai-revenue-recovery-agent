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


def utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def run_smoke_test() -> None:
    db = SessionLocal()

    # Make every smoke-test run use unique business identifiers.
    run_id = utcnow().strftime("%Y%m%d%H%M%S%f")

    invoice_number = f"SMOKE-{run_id}"
    failed_reference = f"smoke-failed-{run_id}"
    success_reference = f"smoke-success-{run_id}"

    try:
        # ---------------------------------------------------------
        # 1. Create customer
        # ---------------------------------------------------------
        customer = Customer(
            name=f"Smoke Test Customer {run_id}",
            email=f"smoke-{run_id}@example.com",
            phone=f"+910000{run_id[-6:]}",
            segment="SMB",
        )

        db.add(customer)
        db.flush()

        # ---------------------------------------------------------
        # 2. Create overdue invoice
        # ---------------------------------------------------------
        invoice = Invoice(
            customer_id=customer.id,
            invoice_number=invoice_number,
            amount=1_000_000,              # ₹10,000 = 1,000,000 paise
            outstanding_amount=1_000_000,
            due_date=utcnow().date() - timedelta(days=5),
            status="OVERDUE",
        )

        db.add(invoice)
        db.flush()

        # ---------------------------------------------------------
        # 3. Create failed payment
        # ---------------------------------------------------------
        failed_payment = Payment(
            invoice_id=invoice.id,
            amount=10_000,                 # ₹100 = 10,000 paise
            payment_date=utcnow(),
            status="FAILED",
            reference=failed_reference,
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
            executed_at=utcnow(),
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
            amount=1_000_000,              # ₹10,000 = 1,000,000 paise
            payment_date=utcnow(),
            status="SUCCESS",
            reference=success_reference,
        )

        db.add(successful_payment)
        db.flush()

        # Link recovery action to successful payment.
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
                "amount": successful_payment.amount,
            },
            timestamp=utcnow(),
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
        print(f"Recovered Amount:     ₹{successful_payment.amount / 100:.2f}")
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