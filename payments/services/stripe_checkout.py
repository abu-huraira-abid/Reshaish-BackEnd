from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from rest_framework.exceptions import ValidationError

from agreements.models import Agreement
from payments.models import PaymentTransaction
from properties.models import Property
from rentals.services import create_tenancy_from_payment

ZERO_DECIMAL_CURRENCIES = {
    "bif",
    "clp",
    "djf",
    "gnf",
    "jpy",
    "kmf",
    "krw",
    "mga",
    "pyg",
    "rwf",
    "ugx",
    "vnd",
    "vuv",
    "xaf",
    "xof",
    "xpf",
}


def _stripe():
    try:
        import stripe
    except ImportError as exc:
        raise ImproperlyConfigured(
            "Stripe SDK is not installed. Run `poetry add stripe`."
        ) from exc

    if not settings.STRIPE_SECRET_KEY:
        raise ImproperlyConfigured("STRIPE_SECRET_KEY is not configured.")
    stripe.api_key = settings.STRIPE_SECRET_KEY
    return stripe


def _unit_amount(amount, currency):
    amount = int(amount or 0)
    if currency.lower() in ZERO_DECIMAL_CURRENCIES:
        return amount
    return amount * 100


def _payment_breakdown(property_obj):
    deposit = int(property_obj.deposit or 0)
    rent = int(property_obj.rent or 0)
    agreement_charges = 2500
    platform_fee = round(rent * 0.30)
    gst = 360
    return {
        "deposit": deposit,
        "rent": rent,
        "agreement_charges": agreement_charges,
        "platform_fee": platform_fee,
        "gst": gst,
    }


def _get_or_create_agreement(*, property_obj, tenant):
    base_queryset = Agreement.objects.filter(
        property=property_obj,
        tenant=tenant,
        landlord=property_obj.owner,
    )
    active_agreement = base_queryset.filter(status=Agreement.Status.ACTIVE).first()
    if active_agreement:
        raise ValidationError(
            "This property is already rented through an active agreement."
        )

    payment_agreement = (
        base_queryset.filter(status=Agreement.Status.PAYMENT_PENDING)
        .order_by("-updated_at", "-created_at", "-id")
        .first()
    )
    if payment_agreement:
        return payment_agreement

    if base_queryset.filter(status=Agreement.Status.PENDING_ACCEPTANCE).exists():
        raise ValidationError(
            "Landlord acceptance is required before starting payment."
        )

    raise ValidationError(
        "No accepted rental agreement found for this property."
    )


def create_initial_payment_checkout_session(*, payer, property_id):
    property_obj = Property.objects.select_related("owner").get(id=property_id)
    agreement = _get_or_create_agreement(property_obj=property_obj, tenant=payer)
    amount_breakdown = _payment_breakdown(property_obj)
    total_amount = sum(amount_breakdown.values())
    currency = settings.STRIPE_CURRENCY

    transaction = PaymentTransaction.objects.create(
        agreement=agreement,
        payer=payer,
        amount_breakdown=amount_breakdown,
        currency=currency,
        status=PaymentTransaction.Status.PENDING,
    )

    stripe = _stripe()
    success_url = (
        f"{settings.STRIPE_SUCCESS_URL}?session_id={{CHECKOUT_SESSION_ID}}"
        f"&transaction_id={transaction.id}&property_id={property_obj.id}"
    )
    cancel_url = (
        f"{settings.STRIPE_CANCEL_URL.rstrip('/')}/{property_obj.id}"
        f"?transaction_id={transaction.id}"
    )
    session = stripe.checkout.Session.create(
        mode="payment",
        payment_method_types=settings.STRIPE_PAYMENT_METHOD_TYPES,
        customer_email=payer.email,
        success_url=success_url,
        cancel_url=cancel_url,
        client_reference_id=str(transaction.id),
        metadata={
            "transaction_id": str(transaction.id),
            "property_id": str(property_obj.id),
            "agreement_id": str(agreement.id),
            "payer_id": str(payer.id),
        },
        line_items=[
            {
                "quantity": 1,
                "price_data": {
                    "currency": currency,
                    "unit_amount": _unit_amount(total_amount, currency),
                    "product_data": {
                        "name": f"Rehaish initial payment - {property_obj.title}",
                        "description": (
                            "Security deposit, first month rent, agreement "
                            "charges, platform fee, and tax."
                        ),
                    },
                },
            }
        ],
    )

    transaction.gateway_ref = session.id
    transaction.stripe_checkout_session_id = session.id
    transaction.stripe_customer_id = session.get("customer") or ""
    transaction.save(
        update_fields=[
            "gateway_ref",
            "stripe_checkout_session_id",
            "stripe_customer_id",
        ]
    )
    return transaction, session


def mark_checkout_session_paid(session):
    transaction_id = session.get("metadata", {}).get("transaction_id")
    session_id = session.get("id", "")
    queryset = PaymentTransaction.objects.select_related("agreement")
    transaction = (
        queryset.filter(id=transaction_id).first()
        if transaction_id
        else queryset.filter(stripe_checkout_session_id=session_id).first()
    )
    if not transaction:
        return None
    if (
        transaction.status == PaymentTransaction.Status.SUCCESS
        and transaction.agreement.status == Agreement.Status.ACTIVE
    ):
        return transaction

    transaction.status = PaymentTransaction.Status.SUCCESS
    transaction.gateway_ref = session_id
    transaction.stripe_checkout_session_id = session_id
    transaction.stripe_payment_intent_id = session.get("payment_intent") or ""
    transaction.stripe_customer_id = session.get("customer") or ""
    transaction.save(
        update_fields=[
            "status",
            "gateway_ref",
            "stripe_checkout_session_id",
            "stripe_payment_intent_id",
            "stripe_customer_id",
        ]
    )

    agreement = transaction.agreement
    agreement.status = Agreement.Status.ACTIVE
    agreement.save(update_fields=["status", "updated_at"])
    create_tenancy_from_payment(transaction)
    return transaction


def confirm_checkout_session_paid(*, session_id, payer):
    if not session_id:
        raise ValidationError("Stripe session id is required.")

    existing_transaction = (
        PaymentTransaction.objects.select_related("agreement")
        .filter(stripe_checkout_session_id=session_id, payer=payer)
        .first()
    )
    if (
        existing_transaction
        and existing_transaction.status == PaymentTransaction.Status.SUCCESS
        and existing_transaction.agreement.status == Agreement.Status.ACTIVE
    ):
        return existing_transaction

    stripe = _stripe()
    session = stripe.checkout.Session.retrieve(session_id)
    if session.get("payment_status") != "paid":
        raise ValidationError("Stripe payment is not completed yet.")

    transaction = mark_checkout_session_paid(session)
    if not transaction:
        raise ValidationError("Payment transaction was not found for this session.")
    if transaction.payer_id != payer.id:
        raise ValidationError("This payment session belongs to another user.")
    return transaction


def mark_checkout_session_failed(session):
    session_id = session.get("id", "")
    transaction = PaymentTransaction.objects.filter(
        stripe_checkout_session_id=session_id,
    ).first()
    if not transaction:
        return None
    transaction.status = PaymentTransaction.Status.FAILED
    transaction.save(update_fields=["status"])
    return transaction
