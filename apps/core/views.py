from django.shortcuts import render


def home(request):
    """Display the application home page"""
    return render(request, "home.html")
