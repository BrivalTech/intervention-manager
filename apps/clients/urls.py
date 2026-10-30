from django.urls import path

from . import views

app_name = "clients"

urlpatterns = [
    path("", views.client_list, name="list"),
    path("create/", views.client_create, name="create"),
    path("<uuid:public_id>/", views.client_detail, name="detail"),
    path("<uuid:public_id>/edit/", views.client_update, name="update"),
    path("<uuid:public_id>/archive/", views.client_archive, name="archive"),
    path("<uuid:public_id>/restore/", views.client_restore, name="restore"),
]
