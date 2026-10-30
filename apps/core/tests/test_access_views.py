from urllib.parse import parse_qs, urlsplit

import pytest
from django.urls import reverse

from apps.accounts.models import User


@pytest.mark.django_db
def test_design_system_page(client):
    response = client.get(reverse("core:design-system"))

    assert response.status_code == 302
    assert response.url.startswith(reverse("accounts:login"))


@pytest.mark.django_db
@pytest.mark.parametrize(
    "role",
    [User.Role.MANAGER, User.Role.TECHNICIAN],
)
def test_design_system_restricted_to_admin(client, django_user_model, role):
    user = django_user_model.objects.create_user(
        username=f"user-{role.lower()}",
        password="TestPassword123!",
        role=role,
    )

    client.force_login(user)
    response = client.get(reverse("core:design-system"))

    assert response.status_code == 403


def test_home_requires_authentication(client):
    response = client.get(reverse("core:home"))

    assert response.status_code == 302
    assert response.url == "/accounts/login/?next=/"


@pytest.mark.django_db
def test_home_accessible_to_authenticated_user(client, django_user_model):
    user = django_user_model.objects.create_user(
        username="testUser",
        password="TestPassword123!",
    )
    client.force_login(user)
    response = client.get(reverse("core:home"))

    assert response.status_code == 200
    assert "home.html" in [t.name for t in response.templates]


@pytest.mark.django_db
def test_home_handles_user_without_role(client, django_user_model):
    user = django_user_model.objects.create_user(
        username="user-whitout-role",
        password="TestPassword123",
    )
    client.force_login(user)
    response = client.get(reverse("core:home"))

    assert response.status_code == 200
    assert "Aucun rôle valide" in response.content.decode()


def test_home_redirects_anonymous_user_to_login(client):
    home_url = reverse("core:home")
    login_url = reverse("accounts:login")

    response = client.get(home_url)
    assert response.status_code == 302

    redirect = urlsplit(response.url)
    assert redirect.path == login_url
    assert parse_qs(redirect.query) == {"next": [home_url]}


@pytest.mark.django_db
@pytest.mark.parametrize(
    "role",
    [
        User.Role.ADMIN,
        User.Role.MANAGER,
        User.Role.TECHNICIAN,
    ],
)
def test_authenticated_users_access_home(
    client,
    django_user_model,
    role,
):
    user = django_user_model.objects.create_user(
        username=f"user-{role.lower()}",
        password="TestPassword123",
        role=role,
    )
    client.force_login(user)
    response = client.get(reverse("core:home"))

    assert response.status_code == 200
    assert response.wsgi_request.user.is_authenticated
