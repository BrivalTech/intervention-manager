from django.urls import path

from . import views

app_name = "interventions"

urlpatterns = [
    path("", views.intervention_list, name="list"),
    path("create/", views.intervention_create, name="create"),
    path("<uuid:public_id>/", views.intervention_detail, name="detail"),
    path("<uuid:public_id>/edit/", views.intervention_edit, name="edit"),
    path(
        "<uuid:public_id>/status/<str:action>/",
        views.intervention_status_update,
        name="status_update",
    ),
    path(
        "<uuid:public_id>/complete/",
        views.intervention_complete,
        name="complete",
    ),
]
