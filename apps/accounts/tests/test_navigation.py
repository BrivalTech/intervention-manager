import pytest
from django.urls import reverse

from apps.accounts.models import User


@pytest.fixture
def authenticated_user(client, django_user_model, request):
    role = request.param
    user = django_user_model.objects.create_user(
        username=f"user-{role.lower()}",
        password="TestPassword123",
        role=role,
    )
    client.force_login(user)
    return user


@pytest.mark.django_db
@pytest.mark.parametrize(
    "authenticated_user",
    [
        User.Role.ADMIN,
        User.Role.MANAGER,
        User.Role.TECHNICIAN,
    ],
    indirect=True,
)
def test_authenticated_navigation(
    client,
    authenticated_user,
):
    response = client.get(reverse("core:home"))

    assert response.status_code == 200
    assert "Se déconnecter" in response.content.decode()
    assert "Se connecter" not in response.content.decode()
    assert "Accueil" in response.content.decode()


@pytest.mark.django_db
def test_home_navigation_current_page(client, django_user_model):
    user = django_user_model.objects.create_user(
        username="admin",
        password="TestPassword123",
        role=User.Role.ADMIN,
    )
    client.force_login(user)
    response = client.get(reverse("core:home"))

    assert response.status_code == 200

    links = response.context["request"].resolver_match
    assert links.view_name == "core:home"
    assert 'aria-current="page"' in response.content.decode()
