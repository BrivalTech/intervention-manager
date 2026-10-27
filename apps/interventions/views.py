from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, render

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

    interventions = interventions.order_by("starts_at", "pk")

    paginator = Paginator(interventions, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "interventions/intervention_list.html",
        {
            "interventions": page_obj,
            "page_obj": page_obj,
            "search_query": search_query,
            "status_filter": status_filter,
            "status_choices": Intervention.Status.choices,
            "list_query": request.GET.urlencode(),
        },
    )


@login_required
def intervention_detail(request, pk):
    """Display an intervention according to the user's role."""
    if not can_view_interventions(request.user):
        raise PermissionDenied

    interventions = Intervention.objects.select_related(
        "client",
        "technician",
        "created_by",
    )

    if request.user.role == User.Role.TECHNICIAN:
        interventions = interventions.filter(
            technician=request.user,
        )

    intervention = get_object_or_404(interventions, pk=pk)

    return render(
        request,
        "interventions/intervention_detail.html",
        {
            "intervention": intervention,
            "list_query": request.GET.urlencode(),
        },
    )
