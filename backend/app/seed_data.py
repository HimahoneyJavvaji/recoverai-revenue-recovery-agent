import random
from datetime import datetime, timedelta, timezone

from backend.app.database import SessionLocal
from backend.app.models import (
    AuditEvent,
    Communication,
    Customer,
    Invoice,
    Payment,
    PromiseToPay,
    RecoveryAction,
    RecoveryCase,
)


RANDOM_SEED = 42


def generate_seed_data() -> None:
    random.seed(RANDOM_SEED)

    db = SessionLocal()

    try:
        # ---------------------------------------------------------
        # Prevent duplicate seed data
        # ---------------------------------------------------------
        existing_customers = db.query(Customer).count()

        if existing_customers > 0:
            print(
                f"Database already contains {existing_customers} customers."
            )
            print("Skipping seed generation to avoid duplicates.")
            return

        print("Generating RecoverAI synthetic dataset...")

        now = datetime.now(timezone.utc)

        customers = []

        # ---------------------------------------------------------
        # 1. Generate customers
        # ---------------------------------------------------------
        for i in range(1, 21):
            customer = Customer(
                name=f"Merchant {i}",
                email=f"merchant{i}@example.com",
                phone=f"+919000000{i:03d}",
                segment=random.choice(
                    ["SMB", "MID_MARKET", "ENTERPRISE"]
                ),
            )

            db.add(customer)
            customers.append(customer)

        db.flush()

        print(f"Created {len(customers)} customers")

        # ---------------------------------------------------------
        # 2. Failed payment scenarios
        # ---------------------------------------------------------
        for i, customer in enumerate(customers[:7], start=1):

            amount = random.choice(
                [500000, 1000000, 2500000]
            )

            invoice = Invoice(
                customer_id=customer.id,
                invoice_number=f"FAIL-{i:03d}",
                amount=amount,
                outstanding_amount=amount,
                due_date=(now - timedelta(days=random.randint(1, 10))).date(),
                status="OVERDUE",
            )

            db.add(invoice)
            db.flush()

            failed_payment = Payment(
                invoice_id=invoice.id,
                amount=amount,
                payment_date=now - timedelta(days=1),
                status="FAILED",
                reference=f"failed-payment-{i:03d}",
            )

            db.add(failed_payment)
            db.flush()

            recovery_case = RecoveryCase(
                customer_id=customer.id,
                invoice_id=invoice.id,
                risk_amount=amount,
                risk_reason="PAYMENT_FAILED",
                priority=random.choice(["HIGH", "MEDIUM"]),
                status="ACTIVE",
            )

            db.add(recovery_case)
            db.flush()

            action = RecoveryAction(
                case_id=recovery_case.id,
                action_type="SEND_PAYMENT_LINK",
                reason="Payment attempt failed.",
                status="EXECUTED",
                attempt_number=1,
                executed_at=now,
                result="Payment reminder sent.",
                recovered_amount=0,
            )

            db.add(action)

            audit_event = AuditEvent(
                case_id=recovery_case.id,
                event_type="PAYMENT_FAILED",
                actor="SYSTEM",
                description="Failed payment detected.",
                event_metadata={
                    "payment_id": failed_payment.id,
                    "amount": amount,
                },
                timestamp=now,
            )

            db.add(audit_event)

        # ---------------------------------------------------------
        # 3. Overdue invoice scenarios
        # ---------------------------------------------------------
        for i, customer in enumerate(customers[7:14], start=1):

            amount = random.choice(
                [750000, 1500000, 3000000]
            )

            invoice = Invoice(
                customer_id=customer.id,
                invoice_number=f"OVERDUE-{i:03d}",
                amount=amount,
                outstanding_amount=amount,
                due_date=(now - timedelta(days=random.randint(15, 45))).date(),
                status="OVERDUE",
            )

            db.add(invoice)
            db.flush()

            recovery_case = RecoveryCase(
                customer_id=customer.id,
                invoice_id=invoice.id,
                risk_amount=amount,
                risk_reason="OVERDUE_INVOICE",
                priority=random.choice(["HIGH", "MEDIUM", "LOW"]),
                status="ACTIVE",
            )

            db.add(recovery_case)
            db.flush()

            communication = Communication(
                customer_id=customer.id,
                invoice_id=invoice.id,
                channel="EMAIL",
                direction="OUTBOUND",
                message="Your invoice is overdue. Please complete payment.",
                timestamp=now,
            )

            db.add(communication)
            db.flush()

            action = RecoveryAction(
                case_id=recovery_case.id,
                action_type="SEND_REMINDER",
                reason="Invoice is overdue.",
                status="EXECUTED",
                attempt_number=1,
                executed_at=now,
                result="Reminder sent successfully.",
                recovered_amount=0,
            )

            db.add(action)

            audit_event = AuditEvent(
                case_id=recovery_case.id,
                event_type="OVERDUE_DETECTED",
                actor="SYSTEM",
                description="Overdue invoice detected.",
                event_metadata={
                    "invoice_id": invoice.id,
                    "days_overdue": random.randint(15, 45),
                },
                timestamp=now,
            )

            db.add(audit_event)

        # ---------------------------------------------------------
        # 4. Broken promise-to-pay scenarios
        # ---------------------------------------------------------
        for i, customer in enumerate(customers[14:], start=1):

            amount = random.choice(
                [1000000, 2000000, 5000000]
            )

            invoice = Invoice(
                customer_id=customer.id,
                invoice_number=f"PROMISE-{i:03d}",
                amount=amount,
                outstanding_amount=amount,
                due_date=(now - timedelta(days=10)).date(),
                status="OVERDUE",
            )

            db.add(invoice)
            db.flush()

            communication = Communication(
                customer_id=customer.id,
                invoice_id=invoice.id,
                channel="EMAIL",
                direction="INBOUND",
                message="I will make the payment within three days.",
                timestamp=now - timedelta(days=7),
            )

            db.add(communication)
            db.flush()

            promise = PromiseToPay(
                customer_id=customer.id,
                invoice_id=invoice.id,
                source_communication_id=communication.id,
                promised_amount=amount,
                promise_date=(now - timedelta(days=4)).date(),
                status="BROKEN",
                confidence=90,
                created_at=now - timedelta(days=7),
            )

            db.add(promise)
            db.flush()

            recovery_case = RecoveryCase(
                customer_id=customer.id,
                invoice_id=invoice.id,
                risk_amount=amount,
                risk_reason="BROKEN_PROMISE",
                priority="HIGH",
                status="ACTIVE",
            )

            db.add(recovery_case)
            db.flush()

            action = RecoveryAction(
                case_id=recovery_case.id,
                action_type="ESCALATE",
                reason="Promise-to-pay deadline passed without payment.",
                status="EXECUTED",
                attempt_number=1,
                executed_at=now,
                result="Case escalated.",
                recovered_amount=0,
            )

            db.add(action)

            audit_event = AuditEvent(
                case_id=recovery_case.id,
                event_type="PROMISE_BROKEN",
                actor="SYSTEM",
                description="Customer failed to honor promise-to-pay.",
                event_metadata={
                    "promise_id": promise.id,
                    "amount": amount,
                },
                timestamp=now,
            )

            db.add(audit_event)

        # ---------------------------------------------------------
        # Commit
        # ---------------------------------------------------------
        db.commit()

        print()
        print("SYNTHETIC DATA GENERATION COMPLETED")
        print("-----------------------------------")
        print(f"Customers: {db.query(Customer).count()}")
        print(f"Invoices: {db.query(Invoice).count()}")
        print(f"Payments: {db.query(Payment).count()}")
        print(f"Communications: {db.query(Communication).count()}")
        print(f"Promises to Pay: {db.query(PromiseToPay).count()}")
        print(f"Recovery Cases: {db.query(RecoveryCase).count()}")
        print(f"Recovery Actions: {db.query(RecoveryAction).count()}")
        print(f"Audit Events: {db.query(AuditEvent).count()}")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    generate_seed_data()