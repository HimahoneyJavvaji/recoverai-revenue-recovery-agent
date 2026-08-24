from datetime import date, datetime
from enum import Enum

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class InvoiceStatus(str, Enum):
    OPEN = "OPEN"
    PARTIALLY_PAID = "PARTIALLY_PAID"
    PAID = "PAID"
    OVERDUE = "OVERDUE"
    CANCELLED = "CANCELLED"


class PaymentStatus(str, Enum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    PENDING = "PENDING"
    REFUNDED = "REFUNDED"


class PromiseStatus(str, Enum):
    PENDING = "PENDING"
    FULFILLED = "FULFILLED"
    PARTIALLY_FULFILLED = "PARTIALLY_FULFILLED"
    BROKEN = "BROKEN"
    CANCELLED = "CANCELLED"


class RiskReason(str, Enum):
    PAYMENT_FAILED = "PAYMENT_FAILED"
    CHECKOUT_ABANDONED = "CHECKOUT_ABANDONED"
    SUBSCRIPTION_FAILED = "SUBSCRIPTION_FAILED"
    INVOICE_OVERDUE = "INVOICE_OVERDUE"
    PROMISE_BROKEN = "PROMISE_BROKEN"
    PAYMENT_DEGRADED = "PAYMENT_DEGRADED"


class CasePriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class CaseStatus(str, Enum):
    ACTIVE = "ACTIVE"
    RECOVERED = "RECOVERED"
    ESCALATED = "ESCALATED"
    STOPPED = "STOPPED"
    CLOSED = "CLOSED"


class ActionType(str, Enum):
    WAIT = "WAIT"
    SEND_REMINDER = "SEND_REMINDER"
    SEND_PAYMENT_LINK = "SEND_PAYMENT_LINK"
    RETRY_PAYMENT = "RETRY_PAYMENT"
    REQUEST_PROMISE = "REQUEST_PROMISE"
    ESCALATE = "ESCALATE"
    STOP = "STOP"


class ActionStatus(str, Enum):
    PROPOSED = "PROPOSED"
    APPROVED = "APPROVED"
    EXECUTED = "EXECUTED"
    FAILED = "FAILED"
    BLOCKED = "BLOCKED"


# ---------------------------------------------------------------------------
# Customer
# ---------------------------------------------------------------------------


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    email: Mapped[str] = mapped_column(String(320), nullable=False, index=True)
    phone: Mapped[str | None] = mapped_column(String(30))
    segment: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    invoices: Mapped[list["Invoice"]] = relationship(
        back_populates="customer",
        cascade="all, delete-orphan",
    )

    communications: Mapped[list["Communication"]] = relationship(
        back_populates="customer",
        cascade="all, delete-orphan",
    )

    promises_to_pay: Mapped[list["PromiseToPay"]] = relationship(
        back_populates="customer",
        cascade="all, delete-orphan",
    )

    recovery_cases: Mapped[list["RecoveryCase"]] = relationship(
        back_populates="customer",
        cascade="all, delete-orphan",
    )


# ---------------------------------------------------------------------------
# Invoice
# ---------------------------------------------------------------------------


class Invoice(Base):
    __tablename__ = "invoices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    customer_id: Mapped[int] = mapped_column(
        ForeignKey("customers.id"),
        nullable=False,
        index=True,
    )

    invoice_number: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
        index=True,
    )

    # All monetary values are stored in paise.
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    outstanding_amount: Mapped[int] = mapped_column(Integer, nullable=False)

    due_date: Mapped[date] = mapped_column(Date, nullable=False)

    status: Mapped[InvoiceStatus] = mapped_column(
        String(30),
        nullable=False,
        default=InvoiceStatus.OPEN,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    customer: Mapped["Customer"] = relationship(
        back_populates="invoices",
    )

    payments: Mapped[list["Payment"]] = relationship(
        back_populates="invoice",
        cascade="all, delete-orphan",
    )

    communications: Mapped[list["Communication"]] = relationship(
        back_populates="invoice",
    )

    promises_to_pay: Mapped[list["PromiseToPay"]] = relationship(
        back_populates="invoice",
    )

    recovery_cases: Mapped[list["RecoveryCase"]] = relationship(
        back_populates="invoice",
        cascade="all, delete-orphan",
    )


# ---------------------------------------------------------------------------
# Payment
# ---------------------------------------------------------------------------


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    invoice_id: Mapped[int] = mapped_column(
        ForeignKey("invoices.id"),
        nullable=False,
        index=True,
    )

    amount: Mapped[int] = mapped_column(Integer, nullable=False)

    payment_date: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )

    status: Mapped[PaymentStatus] = mapped_column(
        String(30),
        nullable=False,
    )

    reference: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        unique=True,
    )

    invoice: Mapped["Invoice"] = relationship(
        back_populates="payments",
    )


# ---------------------------------------------------------------------------
# Communication
# ---------------------------------------------------------------------------


class Communication(Base):
    __tablename__ = "communications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    customer_id: Mapped[int] = mapped_column(
        ForeignKey("customers.id"),
        nullable=False,
        index=True,
    )

    invoice_id: Mapped[int | None] = mapped_column(
        ForeignKey("invoices.id"),
        index=True,
    )

    channel: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    direction: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    message: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    timestamp: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    customer: Mapped["Customer"] = relationship(
        back_populates="communications",
    )

    invoice: Mapped["Invoice | None"] = relationship(
        back_populates="communications",
    )

    promises_to_pay: Mapped[list["PromiseToPay"]] = relationship(
        back_populates="source_communication",
    )


# ---------------------------------------------------------------------------
# Promise To Pay
# ---------------------------------------------------------------------------


class PromiseToPay(Base):
    __tablename__ = "promises_to_pay"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    customer_id: Mapped[int] = mapped_column(
        ForeignKey("customers.id"),
        nullable=False,
        index=True,
    )

    invoice_id: Mapped[int] = mapped_column(
        ForeignKey("invoices.id"),
        nullable=False,
        index=True,
    )

    source_communication_id: Mapped[int | None] = mapped_column(
        ForeignKey("communications.id"),
        index=True,
    )

    promised_amount: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    promise_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    status: Mapped[PromiseStatus] = mapped_column(
        String(40),
        nullable=False,
        default=PromiseStatus.PENDING,
    )

    confidence: Mapped[int | None] = mapped_column(
        Integer,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    customer: Mapped["Customer"] = relationship(
        back_populates="promises_to_pay",
    )

    invoice: Mapped["Invoice"] = relationship(
        back_populates="promises_to_pay",
    )

    source_communication: Mapped["Communication | None"] = relationship(
        back_populates="promises_to_pay",
    )


# ---------------------------------------------------------------------------
# Recovery Case
# ---------------------------------------------------------------------------


class RecoveryCase(Base):
    __tablename__ = "recovery_cases"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    customer_id: Mapped[int] = mapped_column(
        ForeignKey("customers.id"),
        nullable=False,
        index=True,
    )

    invoice_id: Mapped[int] = mapped_column(
        ForeignKey("invoices.id"),
        nullable=False,
        index=True,
    )

    risk_amount: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    risk_reason: Mapped[RiskReason] = mapped_column(
        String(40),
        nullable=False,
    )

    priority: Mapped[CasePriority] = mapped_column(
        String(20),
        nullable=False,
    )

    status: Mapped[CaseStatus] = mapped_column(
        String(20),
        nullable=False,
        default=CaseStatus.ACTIVE,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    customer: Mapped["Customer"] = relationship(
        back_populates="recovery_cases",
    )

    invoice: Mapped["Invoice"] = relationship(
        back_populates="recovery_cases",
    )

    actions: Mapped[list["RecoveryAction"]] = relationship(
        back_populates="case",
        cascade="all, delete-orphan",
    )

    audit_events: Mapped[list["AuditEvent"]] = relationship(
        back_populates="case",
        cascade="all, delete-orphan",
    )


# ---------------------------------------------------------------------------
# Recovery Action
# ---------------------------------------------------------------------------


class RecoveryAction(Base):
    __tablename__ = "recovery_actions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    case_id: Mapped[int] = mapped_column(
        ForeignKey("recovery_cases.id"),
        nullable=False,
        index=True,
    )

    action_type: Mapped[ActionType] = mapped_column(
        String(40),
        nullable=False,
    )

    reason: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    status: Mapped[ActionStatus] = mapped_column(
        String(20),
        nullable=False,
    )

    attempt_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    executed_at: Mapped[datetime | None] = mapped_column(
        DateTime,
    )

    result: Mapped[str | None] = mapped_column(
        Text,
    )

    payment_id: Mapped[int | None] = mapped_column(
        ForeignKey("payments.id"),
        nullable=True,
        index=True,
    )

    recovered_amount: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    payment: Mapped["Payment | None"] = relationship()

    case: Mapped["RecoveryCase"] = relationship(
        back_populates="actions",
    )


# ---------------------------------------------------------------------------
# Audit Event
# ---------------------------------------------------------------------------


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    case_id: Mapped[int] = mapped_column(
        ForeignKey("recovery_cases.id"),
        nullable=False,
        index=True,
    )

    event_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    actor: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    event_metadata: Mapped[dict | None] = mapped_column(
        "metadata",
        JSON,
    )

    timestamp: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    case: Mapped["RecoveryCase"] = relationship(
        back_populates="audit_events",
    )