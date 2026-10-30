from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from apps.clients.forms import ClientForm
from apps.clients.models import Client
from apps.clients.permissions import (
    can_archive_client,
    can_manage_clients,
    can_restore_client,
    can_view_clients,
)


@login_required
def client_list(request):
    """Display clients filtered by search term and status"""
    if not can_view_clients(request.user):
        raise PermissionDenied

    query = request.GET.get("q", "").strip()
    status = request.GET.get("status", "active")

    if status not in {"active", "archived", "all"}:
        status = "active"

    clients = Client.objects.all()

    if status == "active":
        clients = clients.filter(is_active=True)
    elif status == "archived":
        clients = clients.filter(is_active=False)

    if query:
        clients = clients.filter(
            Q(name__icontains=query)
            | Q(contact_name__icontains=query)
            | Q(email__icontains=query)
            | Q(city__icontains=query)
        )

    clients = clients.order_by("name", "pk")

    paginator = Paginator(clients, 10)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(
        request,
        "clients/client_list.html",
        {
            "clients": page_obj,
            "page_obj": page_obj,
            "query": query,
            "status": status,
            "result_count": paginator.count,
            "can_create_client": can_manage_clients(request.user),
        },
    )


@login_required
def client_create(request):
    """Create a new client"""
    if not can_view_clients(request.user):
        raise PermissionDenied

    if request.method == "POST":
        form = ClientForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Le client a été créé avec succès")
            return redirect("clients:list")
    else:
        form = ClientForm()

    return render(
        request,
        "clients/client_form.html",
        {
            "form": form,
            "is_edit": False,
        },
    )


@login_required
def client_detail(request, public_id):
    """Display client detailed information"""
    if not can_view_clients(request.user):
        raise PermissionDenied

    client_obj = get_object_or_404(Client, public_id=public_id)

    return render(
        request,
        "clients/client_detail.html",
        {
            "client_obj": client_obj,
            "can_edit_client": (
                can_manage_clients(request.user) and client_obj.is_active
            ),
            "can_archive_client": (
                can_archive_client(request.user) and client_obj.is_active
            ),
            "can_restore_client": (
                can_archive_client(request.user) and not client_obj.is_active
            ),
        },
    )


@login_required
def client_update(request, public_id):
    """Update an existing client"""
    if not can_manage_clients(request.user):
        raise PermissionDenied

    client_obj = get_object_or_404(Client, public_id=public_id)

    if not client_obj.is_active:
        raise PermissionDenied(
            "Un client archivé doit être réactivé avant modification."
        )

    if request.method == "POST":
        form = ClientForm(request.POST, instance=client_obj)

        if form.is_valid():
            form.save()
            messages.success(request, "Les informations du client on été mises à jour.")

            return redirect("clients:detail", public_id=client_obj.public_id)

    else:
        form = ClientForm(instance=client_obj)

    return render(
        request,
        "clients/client_form.html",
        {
            "form": form,
            "client_obj": client_obj,
            "is_edit": True,
        },
    )


@login_required
def client_archive(request, public_id):
    """Archive a client if no active interventions remain."""
    if not can_archive_client(request.user):
        raise PermissionDenied

    client_obj = get_object_or_404(Client, public_id=public_id)

    if not client_obj.is_active:
        messages.info(
            request,
            "Ce client est déjà archivé.",
        )
        return redirect("clients:detail", public_id=client_obj.public_id)

    if request.method == "POST":
        try:
            client_obj.archive()
        except ValidationError as exc:
            messages.error(
                request,
                "; ".join(exc.messages),
            )
        else:
            messages.success(
                request,
                "Le client a été archivé avec succès.",
            )

        return redirect("clients:detail", public_id=client_obj.public_id)

    return render(
        request,
        "clients/client_confirm_archive.html",
        {
            "client_obj": client_obj,
        },
    )


@login_required
def client_restore(request, public_id):
    """Restore an archived client"""
    if not can_restore_client(request.user):
        raise PermissionDenied

    client_obj = get_object_or_404(Client, public_id=public_id)

    if client_obj.is_active:
        messages.info(
            request,
            "Ce client est déjà actif.",
        )

        return redirect("clients:detail", public_id=client_obj.public_id)

    if request.method == "POST":
        client_obj.restore()

        messages.success(
            request,
            "Le client a été réactivé avec succès.",
        )

        return redirect("clients:detail", public_id=client_obj.public_id)

    return render(
        request,
        "clients/client_confirm_restore.html",
        {
            "client_obj": client_obj,
        },
    )
