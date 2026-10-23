import logging
from smtplib import SMTPException

from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.core.mail import BadHeaderError
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from apps.accounts.models import User
from apps.accounts.services import send_account_invitation

logger = logging.getLogger(__name__)


def account_list(request, config):
    if not config.can_view(request.user):
        raise PermissionDenied

    query = request.GET.get("q", "").strip()
    status = request.GET.get("status", "active")

    if status not in {"active", "inactive", "all"}:
        status = "active"

    accounts = User.objects.filter(role=config.role)

    if status == "active":
        accounts = accounts.filter(is_active=True)
    elif status == "inactive":
        accounts = accounts.filter(is_active=False)

    if query:
        accounts = accounts.filter(
            Q(first_name__icontains=query)
            | Q(last_name__icontains=query)
            | Q(username__icontains=query)
            | Q(email__icontains=query)
        )

    accounts = accounts.order_by("first_name", "last_name", "pk")
    paginator = Paginator(accounts, 10)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(
        request,
        config.list_template,
        {
            "technicians": page_obj,
            "accounts": page_obj,
            "page_obj": page_obj,
            "query": query,
            "status": status,
            "result_count": paginator.count,
            "can_create_technician": config.can_manage(request.user),
            "can_manage_accounts": config.can_manage(request.user),
            "account_config": config,
        },
    )


def account_create(request, config):
    if not config.can_manage(request.user):
        raise PermissionDenied

    if request.method == "POST":
        form = config.create_form(request.POST)

        if form.is_valid():
            account = form.save()

            try:
                sent_count = send_account_invitation(account, request)
            except (SMTPException, OSError, BadHeaderError):
                logger.exception(
                    "Failed to send invitation for account %s",
                    account.pk,
                )
                sent_count = 0

            if sent_count == 1:
                messages.success(
                    request,
                    f"Le compte {config.label} a été créé et "
                    "l'invitation a été envoyée par e-mail.",
                )
            else:
                messages.warning(
                    request,
                    f"Le compte {config.label} a été créé, mais "
                    "l'invitation n'a pas pu être envoyée. "
                    "Un nouvel envoi sera nécessaire.",
                )

            return redirect(config.list_url)
    else:
        form = config.create_form()

    return render(
        request,
        config.form_template,
        {
            "form": form,
            "is_edit": False,
            "account_config": config,
        },
    )


def account_update(request, pk, config):
    if not config.can_manage(request.user):
        raise PermissionDenied

    account = get_object_or_404(User, pk=pk, role=config.role)

    if request.method == "POST":
        form = config.update_form(request.POST, instance=account)

        if form.is_valid():
            form.save()
            messages.success(
                request,
                f"Les informations du {config.label} ont été mises à jour.",
            )
            return redirect(config.list_url)
    else:
        form = config.update_form(instance=account)

    return render(
        request,
        config.form_template,
        {
            "form": form,
            "is_edit": True,
            "account": account,
            "account_config": config,
        },
    )


def account_resend_invitation(request, pk, config):
    if not config.can_manage(request.user):
        raise PermissionDenied

    account = get_object_or_404(User, pk=pk, role=config.role)

    if not account.is_active:
        messages.error(
            request,
            f"Impossible d'inviter un {config.label} désactivé.",
        )
    elif account.has_usable_password():
        messages.error(
            request,
            f"Ce {config.label} a déjà défini son mot de passe.",
        )
    else:
        try:
            sent_count = send_account_invitation(account, request)
        except (SMTPException, OSError, BadHeaderError):
            logger.exception(
                "Failed to resend invitation for account %s",
                account.pk,
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
                "L'invitation n'a pas pu être envoyée. "
                "Vous pourrez réessayer ultérieurement.",
            )

    return redirect(config.list_url)


def account_set_active(request, pk, config, *, active):
    if not config.can_manage(request.user):
        raise PermissionDenied

    account = get_object_or_404(User, pk=pk, role=config.role)

    if account.is_active != active:
        account.is_active = active
        account.save(update_fields=["is_active"])

        action = "réactivé" if active else "désactivé"
        messages.success(
            request,
            f"Le {config.label} a été {action}.",
        )
    else:
        state = "actif" if active else "désactivé"
        messages.info(
            request,
            f"Ce {config.label} est déjà {state}.",
        )

    return redirect(config.list_url)
