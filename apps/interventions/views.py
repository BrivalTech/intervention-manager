from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Q
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

    search_query = request.GET.get("q", "").strip()
    status_filter = request.GET.get("status", "").strip()

    if search_query:
        interventions = interventions.filter(
            Q(title__icontains=search_query)
            | Q(description__icontains=search_query)
            | Q(client__name__icontains=search_query)
        )

    valid_statuses = set(Intervention.Status.values)

    if status_filter in valid_statuses:
        interventions = interventions.filter(status=status_filter)
    else:
        status_filter = ""

    interventions = interventions.order_by(
        "starts_at",
        "pk",
    )

    return render(
        request,
        "interventions/intervention_list.html",
        {
            "interventions": interventions,
            "search_query": search_query,
            "status_filter": status_filter,
            "status_choices": Intervention.Status.choices,
        },
    )
