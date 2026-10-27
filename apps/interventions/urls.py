from django.urls import path

from . import views

app_name = "interventions"

urlpatterns = [
    path("", views.intervention_list, name="list"),
    path("create/", views.intervention_create, name="create"),
    path("<int:pk>/", views.intervention_detail, name="detail"),
    path("<int:pk>/edit/", views.intervention_edit, name="edit"),
    path(
        "<int:pk>/status/<str:action>/",
        views.intervention_status_update,
        name="status_update",
    ),
]
