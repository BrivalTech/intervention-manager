# Create your views here.
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render

from apps.accounts.models import User
from apps.accounts.permissions import can_manage_technicians, can_view_technicians


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
            "can_create_technicians": can_manage_technicians(request.user),
        },
    )
