from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render

from apps.accounts.models import User


@login_required
def design_system(request):
    """Display the design system for administrators only."""
    if request.user.role != User.Role.ADMIN:
        raise PermissionDenied

    return render(request, "design-system.html")


@login_required
def home(request):
    """Display the application home page."""
    return render(request, "home.html")
