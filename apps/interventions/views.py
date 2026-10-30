from urllib.parse import parse_qsl, urlencode

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods, require_POST

from apps.accounts.models import User
from apps.interventions.forms import InterventionCompletionForm, InterventionForm
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


def get_list_query(request):
    """Return supported intervention list parameters."""
    raw_query = request.POST.get("next") or request.GET.get("next", "")

    allowed = {"q", "status", "page"}

    return urlencode(
        [(key, value) for key, value in parse_qsl(raw_query) if key in allowed]
    )


def get_intervention_detail_url(request, intervention):
    """Build the detail URL preserving list navigation."""
    detail_url = reverse(
        "interventions:detail",
        kwargs={"public_id": intervention.public_id},
    )

    list_query = get_list_query(request)

    if list_query:
        return f"{detail_url}?{list_query}"

    return detail_url


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
def intervention_detail(request, public_id):
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

    intervention = get_object_or_404(interventions, public_id=public_id)

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
            "can_start": can_update_status(
                request.user,
                intervention,
                "start",
            ),
            "can_cancel": can_update_status(
                request.user,
                intervention,
                "cancel",
            ),
            "can_complete": can_update_status(
                request.user,
                intervention,
                "complete",
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
                    public_id=intervention.public_id,
                )
    else:
        form = InterventionForm()

    return render(
        request,
        "interventions/intervention_form.html",
        {"form": form},
    )


@login_required
def intervention_edit(request, public_id):
    """Edit an intervention when the user has permission."""
    intervention = get_object_or_404(
        Intervention.objects.select_related(
            "client",
            "technician",
            "created_by",
        ),
        public_id=public_id,
    )

    if not can_edit_intervention(request.user, intervention):
        raise PermissionDenied

    list_query = get_list_query(request)

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
                    get_intervention_detail_url(
                        request,
                        intervention,
                    )
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
            "list_query": list_query,
        },
    )


@login_required
@require_POST
def intervention_status_update(request, public_id, action):
    """Start or cancel an intervention when authorized."""
    intervention = get_object_or_404(Intervention, public_id=public_id)

    if action not in {"start", "cancel"}:
        raise PermissionDenied

    if not can_update_status(request.user, intervention, action):
        raise PermissionDenied

    try:
        update_intervention_status(
            user=request.user,
            intervention=intervention,
            action=action,
        )
    except ValidationError as exc:
        messages.error(
            request,
            "; ".join(exc.messages),
        )
    else:
        success_messages = {
            "start": "L'intervention a été démarrée.",
            "cancel": "L'intervention a été annulée.",
        }

        messages.success(
            request,
            success_messages[action],
        )

    return redirect(
        get_intervention_detail_url(
            request,
            intervention,
        )
    )


@login_required
@require_http_methods(["GET", "POST"])
def intervention_complete(request, public_id):
    """Complete an intervention with a mandatory report."""
    intervention = get_object_or_404(Intervention, public_id=public_id)

    if not can_update_status(request.user, intervention, "complete"):
        raise PermissionDenied

    list_query = get_list_query(request)

    if request.method == "POST":
        form = InterventionCompletionForm(request.POST)

        if form.is_valid():
            try:
                update_intervention_status(
                    user=request.user,
                    intervention=intervention,
                    action="complete",
                    report=form.cleaned_data["report"],
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
                    "L'intervention a été terminée avec succès.",
                )

                return redirect(
                    get_intervention_detail_url(
                        request,
                        intervention,
                    )
                )
    else:
        form = InterventionCompletionForm()

    return render(
        request,
        "interventions/intervention_complete.html",
        {
            "form": form,
            "intervention": intervention,
            "list_query": list_query,
        },
    )
