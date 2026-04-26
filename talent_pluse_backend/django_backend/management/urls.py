from rest_framework.routers import DefaultRouter
from .views import (
    LeadViewSet,
    TicketViewSet,
    CandidateViewSet,
    ReminderViewSet,
)

router = DefaultRouter()

router.register(
    r"leads",
    LeadViewSet,
    basename="leads"
)

router.register(
    r"tickets",
    TicketViewSet,
    basename="tickets"
)

router.register(
    r"candidates",
    CandidateViewSet,
    basename="candidates"
)

router.register(
    r"reminders",
    ReminderViewSet,
    basename="reminders"
)

urlpatterns = router.urls