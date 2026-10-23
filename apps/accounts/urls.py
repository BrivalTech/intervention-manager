from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy

from apps.accounts import views
from apps.accounts.forms import TechnicianSetPasswordForm

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
        "technicians/<int:pk>/edit/", views.technician_update, name="technician_update"
    ),
    path(
        "invitation/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="accounts/invitation_confirm.html",
            form_class=TechnicianSetPasswordForm,
            success_url=reverse_lazy("accounts:login"),
        ),
        name="invitation_confirm",
    ),
    path(
        "technicians/<int:pk>/resend-invitation/",
        views.technician_resend_invitation,
        name="technician_resend_invitation",
    ),
    path(
        "technicians/<int:pk>/deactivate",
        views.technician_deactivate,
        name="technician_deactivate",
    ),
    path(
        "technicians/<int:pk>/reactivate",
        views.technician_reactivate,
        name="technician_reactivate",
    ),
    path("managers/", views.manager_list, name="manager_list"),
    path("managers/create/", views.manager_create, name="manager_create"),
    path(
        "managers/<int:pk>/edit/",
        views.manager_update,
        name="manager_update",
    ),
    path(
        "managers/<int:pk>/resend-invitation/",
        views.manager_resend_invitation,
        name="manager_resend_invitation",
    ),
    path(
        "managers/<int:pk>/deactivate/",
        views.manager_deactivate,
        name="manager_deactivate",
    ),
    path(
        "managers/<int:pk>/reactivate/",
        views.manager_reactivate,
        name="manager_reactivate",
    ),
]
