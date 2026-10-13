from urllib.parse import parse_qs, urlsplit

import pytest
from django.urls import reverse

from apps.accounts.models import User


def test_design_system_page(client):
    response = client.get(reverse("core:design-system"))
    assert response.status_code == 200
    assert "design-system.html" in [t.name for t in response.templates]


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
@pytest.mark.parametrize(
    ("role", "expected_title", "expected_content"),
    [
        (
            "ADMIN",
            "Tableau de bord - Administration",
            "Administration de l'application",
        ),
        (
            "MANAGER",
            "Tableau de bord - Gestion",
            "Gestion des activités",
        ),
        (
            "TECHNICIAN",
            "Mes interventions",
            "Interventions attribuées",
        ),
    ],
)
def test_home_displays_dashboard_for_user_role(
    client,
    django_user_model,
    role,
    expected_title,
    expected_content,
):
    user = django_user_model.objects.create_user(
        username=f"user-{role.lower()}",
        password="TestPassword123",
        role=role,
    )
    client.force_login(user)
    response = client.get(reverse("core:home"))

    assert response.status_code == 200
    assert expected_title in response.content.decode()
    assert expected_content in response.content.decode()


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


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("username", "password"),
    [
        ("unknown_user", "TestPassword123!"),
        ("testuser", "WrongPassword123!"),
        ("", ""),
        ("testuser", ""),
        ("", "TestPassword123!"),
    ],
)
def test_login_rejects_invalid_credentials(
    client,
    django_user_model,
    username,
    password,
):
    django_user_model.objects.create_user(
        username="testuser",
        password="TestPassword123!",
        role=User.Role.MANAGER,
    )

    response = client.post(
        reverse("accounts:login"),
        {"username": username, "password": password},
    )

    assert response.status_code == 200
    assert not response.wsgi_request.user.is_authenticated
    assert "_auth_user_id" not in client.session
    assert response.context["form"].errors


@pytest.mark.django_db
def test_login_rejects_inactive_user(client, django_user_model):
    django_user_model.objects.create_user(
        username="inactive_user",
        password="TestPassword123!",
        role=User.Role.TECHNICIAN,
        is_active=False,
    )

    response = client.post(
        reverse("accounts:login"),
        {"username": "inactive_user", "password": "TestPassword123!"},
    )

    assert response.status_code == 200
    assert not response.wsgi_request.user.is_authenticated
    assert "_auth_user_id" not in client.session
    assert response.context["form"].errors


@pytest.mark.django_db
def test_invalid_login_displays_accessible_error(client, django_user_model):
    django_user_model.objects.create_user(
        username="testuser",
        password="TestPassword123!",
        role=User.Role.MANAGER,
    )

    response = client.post(
        reverse("accounts:login"),
        {"username": "testuser", "password": "WrongPassword123!"},
    )

    assert response.status_code == 200

    content = response.content.decode()
    assert 'class="message message--error"' in content
    assert 'role="alert"' in content
    assert "Connexion impossible" in content
