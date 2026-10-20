from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy

from apps.accounts import views

app_name = "accounts"

urlpatterns = [
    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="accounts/login.html",
        ),
        name="login",
    ),
    path(
        "logout/",
        auth_views.LogoutView.as_view(),
        name="logout",
    ),
    path("technicians/", views.technician_list, name="technician_list"),
    path("technicians/create/", views.technician_create, name="technician_create"),
    path(
        "invitation/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="accounts/invitation_confirm.html",
            success_url=reverse_lazy("accounts:login"),
        ),
        name="invitation_confirm",
    ),
    path(
        "technicians/<int:pk>/resend-invitation/",
        views.technician_resend_invitation,
        name="technician_resend_invitation",
    ),
]
