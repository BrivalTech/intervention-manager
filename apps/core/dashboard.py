from django.utils import timezone

from apps.accounts.models import User
from apps.interventions.models import Intervention

DASHBOARD_INTERVENTION_LIMIT = 5


def get_dashboard_data(user):
    """Return intervention dashboard data according to the user's role."""
    data = {
        "today_count": 0,
        "today_interventions": [],
        "to_plan_count": 0,
        "in_progress_count": 0,
        "upcoming_count": 0,
    }

    if not user.is_authenticated or not user.is_active:
        return data

    if user.role not in {
        User.Role.ADMIN,
        User.Role.MANAGER,
        User.Role.TECHNICIAN,
    }:
        return data

    interventions = Intervention.objects.all()

    if user.role == User.Role.TECHNICIAN:
        interventions = interventions.filter(technician=user)

    today = timezone.localdate()

    data["to_plan_count"] = interventions.filter(
        status=Intervention.Status.TO_PLAN
    ).count()

    data["in_progress_count"] = interventions.filter(
        status=Intervention.Status.IN_PROGRESS
    ).count()

    today_interventions = interventions.filter(starts_at__date=today)

    data["today_count"] = today_interventions.count()

    data["today_interventions"] = list(
        today_interventions.select_related(
            "client",
            "technician",
        ).order_by(
            "starts_at",
            "pk",
        )[:DASHBOARD_INTERVENTION_LIMIT]
    )

    if user.role == User.Role.TECHNICIAN:
        data["upcoming_count"] = interventions.filter(
            status=Intervention.Status.PLANNED,
            starts_at__date__gt=today,
        ).count()

    return data
