from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from accounts.views import RegisterView, UserViewSet
from agreements.views import AgreementViewSet, KeyHandoverViewSet
from audit.views import AuditLogViewSet
from flatmates.views import FlatmateProfileViewSet
from payments.views import CommissionLedgerViewSet, PaymentTransactionViewSet
from properties.views import PropertyViewSet, VerificationReportViewSet
from services_marketplace.views import ServiceOrderViewSet
from visits.views import VisitCheckInViewSet, VisitQRTokenViewSet, VisitRequestViewSet

router = DefaultRouter()
router.register("users", UserViewSet, basename="user")
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
router.register("audit-logs", AuditLogViewSet, basename="audit-log")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/register/", RegisterView.as_view(), name="register"),
    path("api/auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/", include(router.urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
