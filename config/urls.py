from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from accounts.views import (
    EmailTokenObtainPairView,
    LogoutView,
    RegisterView,
    SendEmailOTPView,
    UserOnboardingViewSet,
    UserViewSet,
    VerifyEmailOTPView,
)
from agreements.views import AgreementViewSet, KeyHandoverViewSet
from audit.views import AuditLogViewSet
from flatmates.views import (
    FlatmateConversationViewSet,
    FlatmateListingViewSet,
    FlatmateProfileViewSet,
)
from notifications.views import NotificationViewSet
from payments.views import CommissionLedgerViewSet, PaymentTransactionViewSet, stripe_webhook
from properties.views import PropertyViewSet, VerificationReportViewSet
from rentals.views import LeaveNoticeViewSet, PropertyIssueViewSet, RentalTenancyViewSet
from services_marketplace.views import ServiceOrderViewSet
from visits.views import VisitCheckInViewSet, VisitQRTokenViewSet, VisitRequestViewSet

router = DefaultRouter()
router.register("users", UserViewSet, basename="user")
router.register("onboarding", UserOnboardingViewSet, basename="onboarding")
router.register("properties", PropertyViewSet, basename="property")
router.register(
    "verification-reports",
    VerificationReportViewSet,
    basename="verification-report",
)
router.register("visit-requests", VisitRequestViewSet, basename="visit-request")
router.register("visit-qr-tokens", VisitQRTokenViewSet, basename="visit-qr-token")
router.register("visit-checkins", VisitCheckInViewSet, basename="visit-checkin")
router.register("agreements", AgreementViewSet, basename="agreement")
router.register("key-handovers", KeyHandoverViewSet, basename="key-handover")
router.register("payments", PaymentTransactionViewSet, basename="payment")
router.register("rental-tenancies", RentalTenancyViewSet, basename="rental-tenancy")
router.register("property-issues", PropertyIssueViewSet, basename="property-issue")
router.register("leave-notices", LeaveNoticeViewSet, basename="leave-notice")
router.register(
    "commission-ledger",
    CommissionLedgerViewSet,
    basename="commission-ledger",
)
router.register("service-orders", ServiceOrderViewSet, basename="service-order")
router.register(
    "flatmate-profiles",
    FlatmateProfileViewSet,
    basename="flatmate-profile",
)
router.register(
    "flatmate-listings",
    FlatmateListingViewSet,
    basename="flatmate-listing",
)
router.register(
    "flatmate-conversations",
    FlatmateConversationViewSet,
    basename="flatmate-conversation",
)
router.register("audit-logs", AuditLogViewSet, basename="audit-log")
router.register("notifications", NotificationViewSet, basename="notification")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/register/", RegisterView.as_view(), name="register"),
    path("api/auth/logout/", LogoutView.as_view(), name="logout"),
    path(
        "api/auth/token/",
        EmailTokenObtainPairView.as_view(),
        name="token_obtain_pair",
    ),
    path("api/auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/auth/email/send-otp/", SendEmailOTPView.as_view(), name="send_email_otp"),
    path(
        "api/auth/email/verify/",
        VerifyEmailOTPView.as_view(),
        name="verify_email_otp",
    ),
    path("api/", include(router.urls)),
    path("api/payments/stripe/webhook/", stripe_webhook, name="stripe-webhook"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
