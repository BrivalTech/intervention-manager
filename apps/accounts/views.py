import logging
from smtplib import SMTPException

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.mail import BadHeaderError
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.accounts.forms import TechnicianCreatingForm, TechnicianUpdateForm
from apps.accounts.models import User
from apps.accounts.permissions import can_manage_technicians, can_view_technicians
from apps.accounts.services import send_technician_invitation

logger = logging.getLogger(__name__)


@login_required
def technician_list(request):
    """Display the list of all technicians filtered by search term and
    status."""
    if not can_view_technicians(request.user):
        raise PermissionDenied

    query = request.GET.get("q", "").strip()
    status = request.GET.get("status", "active")

    if status not in {"active", "inactive", "all"}:
        status = "active"

    technicians = User.objects.filter(role=User.Role.TECHNICIAN)

    if status == "active":
        technicians = technicians.filter(is_active=True)
    elif status == "inactive":
        technicians = technicians.filter(is_active=False)

    if query:
        technicians = technicians.filter(
            Q(first_name__icontains=query)
            | Q(last_name__icontains=query)
            | Q(username__icontains=query)
            | Q(email__icontains=query)
        )

    technicians = technicians.order_by("first_name", "last_name", "pk")

    paginator = Paginator(technicians, 10)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(
        request,
        "accounts/technician_list.html",
        {
            "technicians": page_obj,
            "page_obj": page_obj,
            "query": query,
            "status": status,
            "result_count": paginator.count,
            "can_create_technician": can_manage_technicians(request.user),
        },
    )


@login_required
def technician_create(request):
    """Create a technician and send an invitation email."""
    if not can_manage_technicians(request.user):
        raise PermissionDenied

    if request.method == "POST":
        form = TechnicianCreatingForm(request.POST)

        if form.is_valid():
            technician = form.save()

            try:
                sent_count = send_technician_invitation(
                    technician,
                    request,
                )
            except (SMTPException, OSError, BadHeaderError):
                logger.exception(
                    "Failed to send technician invitation for user %s",
                    technician.pk,
                )
                sent_count = 0

            if sent_count == 1:
                messages.success(
                    request,
                    "Le compte technicien a été créé et l'invitation a été "
                    "envoyée par e-mail.",
                )
            else:
                messages.warning(
                    request,
                    "Le compte technicien a été créé, mais l'invitation n'a "
                    "pas pu être envoyée. Un nouvel envoi sera nécessaire.",
                )

            return redirect("accounts:technician_list")
    else:
        form = TechnicianCreatingForm()

    return render(
        request,
        "accounts/technician_form.html",
        {
            "form": form,
        },
    )


@login_required
def technician_update(request, pk):
    """Update a technician's information."""
    if not can_manage_technicians(request.user):
        raise PermissionDenied

    technician = get_object_or_404(
        User,
        pk=pk,
        role=User.Role.TECHNICIAN,
    )

    if request.method == "POST":
        form = TechnicianUpdateForm(request.POST, instance=technician)

        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Les informations du technicien ont été mises à jour.",
            )
            return redirect("accounts:technician_list")
    else:
        form = TechnicianUpdateForm(instance=technician)

    return render(
        request,
        "accounts/technician_form.html",
        {
            "form": form,
            "is_edit": True,
            "technician": technician,
        },
    )


@login_required
@require_POST
def technician_resend_invitation(request, pk):
    """Resend an invitation to a technician without a password."""
    if not can_manage_technicians(request.user):
        raise PermissionDenied

    technician = get_object_or_404(
        User,
        pk=pk,
        role=User.Role.TECHNICIAN,
    )

    if not technician.is_active:
        messages.error(
            request,
            "Impossible d'inviter un technicien désactivé.",
        )

        return redirect("accounts:technician_list")

    if technician.has_usable_password():
        messages.error(
            request,
            "Ce technicien a déjà défini son mot de passe.",
        )

        return redirect("accounts:technician_list")

    try:
        sent_count = send_technician_invitation(
            technician,
            request,
        )
    except (SMTPException, OSError, BadHeaderError):
        logger.exception(
            "Failed to resend technician invitation for user %s",
            technician.pk,
        )
        sent_count = 0

    if sent_count == 1:
        messages.success(
            request,
            "Une nouvelle invitation a été envoyée par e-mail.",
        )
    else:
        messages.warning(
            request,
            "L'invitation n'a pas pu être envoyée. Vous pourrez réessayer "
            "ultérieurement.",
        )

    return redirect("accounts:technician_list")


@login_required
@require_POST
def technician_deactivate(request, pk):
    """Deactivate a technician account."""
    if not can_manage_technicians(request.user):
        raise PermissionDenied

    technician = get_object_or_404(
        User,
        pk=pk,
        role=User.Role.TECHNICIAN,
    )

    if technician.is_active:
        technician.is_active = False
        technician.save(update_fields=["is_active"])
        messages.success(request, "Le technicien a été désactivé.")
    else:
        messages.info(request, "Ce technicien est déjà désactivé.")

    return redirect("accounts:technician_list")


@login_required
@require_POST
def technician_reactivate(request, pk):
    """Reactivate a technician account."""
    if not can_manage_technicians(request.user):
        raise PermissionDenied

    technician = get_object_or_404(
        User,
        pk=pk,
        role=User.Role.TECHNICIAN,
    )

    if not technician.is_active:
        technician.is_active = True
        technician.save(update_fields=["is_active"])
        messages.success(request, "Le technicien a été réactivé.")
    else:
        messages.info(request, "Ce technicien est déjà actif.")

    return redirect("accounts:technician_list")
