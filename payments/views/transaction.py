from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import decorators, permissions, response, status, viewsets
from rest_framework.exceptions import PermissionDenied

from accounts.models import User
from payments.models import PaymentTransaction
from payments.serializers import PaymentTransactionSerializer
from payments.services import create_payment_transaction
from payments.services.stripe_checkout import (
    confirm_checkout_session_paid,
    create_initial_payment_checkout_session,
    mark_checkout_session_failed,
    mark_checkout_session_paid,
)


class PaymentTransactionViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = PaymentTransaction.objects.select_related("agreement", "payer")
        if user.role == User.Role.ADMIN:
            return queryset
        if user.role == User.Role.TENANT:
            return queryset.filter(payer=user)
        if user.role == User.Role.LANDLORD:
            return queryset.filter(agreement__landlord=user)
        return queryset.none()

    def perform_create(self, serializer):
        if self.request.user.role != User.Role.TENANT:
            raise PermissionDenied("Only tenants can create payment transactions.")
        serializer.instance = create_payment_transaction(
            payer=self.request.user,
            **serializer.validated_data,
        )

    @decorators.action(
        detail=False,
        methods=["post"],
        url_path="create-checkout-session",
    )
    def create_checkout_session(self, request):
        if request.user.role != User.Role.TENANT:
            raise PermissionDenied("Only tenants can start checkout.")
        property_id = request.data.get("property") or request.data.get("property_id")
        if not property_id:
            return response.Response(
                {"detail": "Property is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            transaction, session = create_initial_payment_checkout_session(
                payer=request.user,
                property_id=property_id,
            )
        except ImproperlyConfigured as exc:
            return response.Response(
                {"detail": str(exc)},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        return response.Response(
            {
                "checkout_url": session.url,
                "session_id": session.id,
                "transaction": self.get_serializer(transaction).data,
            },
            status=status.HTTP_201_CREATED,
        )

    @decorators.action(
        detail=False,
        methods=["post"],
        url_path="confirm-checkout-session",
    )
    def confirm_checkout_session(self, request):
        if request.user.role != User.Role.TENANT:
            raise PermissionDenied("Only tenants can confirm checkout.")
        session_id = request.data.get("session_id")
        try:
            transaction = confirm_checkout_session_paid(
                session_id=session_id,
                payer=request.user,
            )
        except ImproperlyConfigured as exc:
            return response.Response(
                {"detail": str(exc)},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        return response.Response(self.get_serializer(transaction).data)


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    signature = request.META.get("HTTP_STRIPE_SIGNATURE", "")
    try:
        import stripe
    except ImportError:
        return HttpResponse("Stripe SDK is not installed.", status=503)

    try:
        event = stripe.Webhook.construct_event(
            payload,
            signature,
            settings.STRIPE_WEBHOOK_SECRET,
        )
    except ValueError:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)

    event_type = event.get("type")
    session = event.get("data", {}).get("object", {})
    if event_type == "checkout.session.completed":
        mark_checkout_session_paid(session)
    elif event_type in {"checkout.session.expired", "payment_intent.payment_failed"}:
        mark_checkout_session_failed(session)

    return HttpResponse(status=200)
