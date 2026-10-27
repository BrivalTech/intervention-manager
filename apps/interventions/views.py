from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.accounts.models import User
from apps.interventions.forms import InterventionForm
from apps.interventions.models import Intervention
from apps.interventions.permissions import (
    can_create_intervention,
    can_edit_intervention,
    can_update_status,
    can_view_interventions,
)
from apps.interventions.services import (
    create_intervention,
    update_intervention,
    update_intervention_status,
)


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
            "can_create_intervention": can_create_intervention(request.user),
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
            "can_edit_intervention": can_edit_intervention(
                request.user,
                intervention,
            ),
        },
    )


@login_required
def intervention_create(request):
    """Create an intervention for an authorized user."""
    if not can_create_intervention(request.user):
        raise PermissionDenied

    if request.method == "POST":
        form = InterventionForm(request.POST)
        form.instance.created_by = request.user

        if form.is_valid():
            try:
                intervention = create_intervention(
                    created_by=request.user,
                    **form.cleaned_data,
                )
            except ValidationError as exc:
                if hasattr(exc, "error_dict"):
                    for field, errors in exc.error_dict.items():
                        form.add_error(
                            field if field in form.fields else None,
                            errors,
                        )
                else:
                    form.add_error(None, exc)
            else:
                messages.success(
                    request,
                    "L'intervention a été créée avec succès.",
                )
                return redirect(
                    "interventions:detail",
                    pk=intervention.pk,
                )
    else:
        form = InterventionForm()

    return render(
        request,
        "interventions/intervention_form.html",
        {"form": form},
    )


@login_required
def intervention_edit(request, pk):
    """Edit an intervention when the user has permission."""
    intervention = get_object_or_404(
        Intervention.objects.select_related(
            "client",
            "technician",
            "created_by",
        ),
        pk=pk,
    )

    if not can_edit_intervention(request.user, intervention):
        raise PermissionDenied

    if request.method == "POST":
        form = InterventionForm(request.POST, instance=intervention)
        if form.is_valid():
            try:
                update_intervention(
                    user=request.user,
                    intervention=intervention,
                    **form.cleaned_data,
                )
            except ValidationError as exc:
                if hasattr(exc, "error_dict"):
                    for field, errors in exc.error_dict.items():
                        form.add_error(
                            field if field in form.fields else None,
                            errors,
                        )
                else:
                    form.add_error(None, exc)
            else:
                messages.success(
                    request,
                    "L'intervention a été modifiée avec succès.",
                )
                return redirect(
                    "interventions:detail",
                    pk=intervention.pk,
                )
    else:
        form = InterventionForm(instance=intervention)

    return render(
        request,
        "interventions/intervention_form.html",
        {
            "form": form,
            "intervention": intervention,
            "is_edit": True,
        },
    )


@login_required
@require_POST
def intervention_status_update(request, pk, action):
    """Perform an authorized intervention status transition."""
    intervention = get_object_or_404(Intervention, pk=pk)

    if not can_update_status(request.user, intervention, action):
        raise PermissionDenied

    report = request.POST.get("report") if action == "complete" else None

    try:
        update_intervention_status(
            user=request.user,
            intervention=intervention,
            action=action,
            report=report,
        )
    except ValidationError as exc:
        messages.error(
            request,
            "; ".join(exc.messages),
        )
    else:
        success_messages = {
            "start": "L'intervention a été démarrée.",
            "complete": "L'intervention a été terminée.",
            "cancel": "L'intervention a été annulée.",
        }

        messages.success(request, success_messages[action])

    return redirect(
        "interventions:detail",
        pk=intervention.pk,
    )
