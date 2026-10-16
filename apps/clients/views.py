from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from apps.clients.forms import ClientForm
from apps.clients.models import Client
from apps.clients.permissions import can_manage_clients, can_view_clients


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
        {"form": form},
    )


@login_required
def client_detail(request, pk):
    """Display client detailed information"""
    if not can_view_clients(request.user):
        raise PermissionDenied

    client_obj = get_object_or_404(Client, pk=pk)

    return render(
        request,
        "clients/client_detail.html",
        {
            "client_obj": client_obj,
        },
    )
