from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render

from apps.accounts.models import User
from apps.core.dashboard import get_dashboard_data


@login_required
def design_system(request):
    """Display the design system for administrators only."""
    if request.user.role != User.Role.ADMIN:
        raise PermissionDenied

    return render(request, "design-system.html")


@login_required
def home(request):
    """Display the dashboard according to the user's role."""
    dashboard_data = get_dashboard_data(request.user)

    return render(
        request,
        "home.html",
        {
            "dashboard": dashboard_data,
        },
    )
