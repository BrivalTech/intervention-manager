from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render

from apps.accounts.models import User
from apps.interventions.models import Intervention
from apps.interventions.permissions import can_view_interventions


@login_required
def intervention_list(request):
    """Display interventions according to the user's role."""
    if not can_view_interventions(request.user):
        raise PermissionDenied

    interventions = Intervention.objects.select_related(
        "client",
        "technician",
    )

    if request.user.role == User.Role.TECHNICIAN:
        interventions = interventions.filter(
            technician=request.user,
        )

    interventions = interventions.order_by(
        "starts_at",
        "pk",
    )

    return render(
        request,
        "interventions/intervention_list.html",
        {
            "interventions": interventions,
        },
    )
