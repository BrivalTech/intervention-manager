from django.contrib.auth.decorators import login_required
from django.shortcuts import render


def design_system(request):
    """Display the application design system reference page"""
    return render(request, "design-system.html")


@login_required
def home(request):
    """Display the application home page"""
    return render(request, "home.html")
