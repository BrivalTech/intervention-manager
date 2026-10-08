from django.urls import path

from . import views

app_name = "core"
urlpatterns = [
    path("design-system/", views.design_system, name="design-system"),
    path("", views.home, name="home"),
]
