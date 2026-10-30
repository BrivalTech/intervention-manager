from django.urls import path


def trigger_server_error(request):
    raise RuntimeError("Simulated server error for test")


urlpatterns = [
    path("simulate-server-error/", trigger_server_error),
]
