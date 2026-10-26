from django.urls import path

from . import views

app_name = "interventions"

urlpatterns = [
    path("", views.intervention_list, name="list"),
]
