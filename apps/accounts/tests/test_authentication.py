import pytest
from django.urls import reverse

from apps.accounts.models import User


@pytest.mark.django_db
def test_logout_authenticated_user(client, django_user_model):
    user = django_user_model.objects.create_user(
        username="logoutuser",
        password="TestPassword123",
    )
    client.force_login(user)
    response = client.post(reverse("accounts:logout"))

    assert response.status_code == 302
    assert response.url == reverse("accounts:login")
    assert "_auth_user_id" not in client.session


@pytest.mark.django_db
def test_logout_is_not_allowed(client, django_user_model):
    user = django_user_model.objects.create_user(
        username="logoutuser",
        password="TestPassword123",
    )
    client.force_login(user)
    response = client.get(reverse("accounts:logout"))

    assert response.status_code == 405
    assert "_auth_user_id" in client.session


@pytest.mark.django_db
def test_login_redirects_to_home(client, django_user_model):
    django_user_model.objects.create_user(
        username="loginuser",
        password="TestPassword123",
    )

    response = client.post(
        reverse("accounts:login"),
        {"username": "loginuser", "password": "TestPassword123"},
    )

    assert response.status_code == 302
    assert response.url == reverse("core:home")
    assert "_auth_user_id" in client.session


@pytest.mark.django_db
def test_login_redirects_to_requested_page(client, django_user_model):
    django_user_model.objects.create_user(
        username="testuser",
        password="TestPassword123",
    )

    response = client.post(
        reverse("accounts:login"),
        {
            "username": "testuser",
            "password": "TestPassword123",
            "next": reverse("core:design-system"),
        },
    )

    assert response.status_code == 302
    assert response.url == reverse("core:design-system")


@pytest.mark.django_db
def test_login_rejects_external_redirects(client, django_user_model):
    django_user_model.objects.create_user(
        username="testuser",
        password="TestPassword123",
    )

    response = client.post(
        reverse("accounts:login"),
        {
            "username": "testuser",
            "password": "TestPassword123",
            "next": "https://example.com",
        },
    )

    assert response.status_code == 302
    assert response.url == reverse("core:home")


@pytest.mark.django_db
def test_session_persists_after_login(client, django_user_model):
    user = django_user_model.objects.create_user(
        username="testuser",
        password="TestPassword123",
    )

    client.force_login(user)
    response = client.get(reverse("core:home"))

    assert response.status_code == 200
    assert response.wsgi_request.user.is_authenticated
    assert response.wsgi_request.user.pk == user.pk


def test_navigation_for_anonymous_user(client):
    response = client.get(reverse("accounts:login"))

    assert response.status_code == 200
    content = response.content.decode()

    assert "Se connecter" in content
    assert "Se déconnecter" not in content
    assert 'class="nav-user-role"' not in content


# Redirections
@pytest.mark.django_db
def test_redirects_to_home_by_default(client, django_user_model):
    django_user_model.objects.create_user(
        username="manager",
        password="TestPassword123",
        role=User.Role.MANAGER,
    )

    response = client.post(
        reverse("accounts:login"),
        {
            "username": "manager",
            "password": "TestPassword123",
        },
    )

    assert response.status_code == 302
    assert response.url == reverse("core:home")


@pytest.mark.django_db
def test_login_accepts_internal_redirect(client, django_user_model):
    django_user_model.objects.create_user(
        username="manager",
        password="TestPassword123",
        role=User.Role.MANAGER,
    )
    target_url = reverse("core:design-system")
    response = client.post(
        reverse("accounts:login"),
        {
            "username": "manager",
            "password": "TestPassword123",
            "next": target_url,
        },
    )

    assert response.status_code == 302
    assert response.url == target_url


@pytest.mark.django_db
@pytest.mark.parametrize(
    "next_url",
    [
        "https://example.com",
        "http://example.com/",
        "javascript:alert(1)",
        "javascript:alert(1)",
    ],
)
def test_login_rejects_unsafe_redirect(client, django_user_model, next_url):
    django_user_model.objects.create_user(
        username="manager",
        password="TestPassword123",
        role=User.Role.MANAGER,
    )
    response = client.post(
        reverse("accounts:login"),
        {
            "username": "manager",
            "password": "TestPassword123",
            "next": next_url,
        },
    )

    assert response.status_code == 302
    assert response.url == reverse("core:home")


# Logout
@pytest.mark.django_db
def test_logout_invalidates_authenticated_session(client, django_user_model):
    user = django_user_model.objects.create_user(
        username="manager",
        password="TestPassword123",
        role=User.Role.MANAGER,
    )

    client.force_login(user)
    assert "_auth_user_id" in client.session

    response = client.post(reverse("accounts:logout"))
    assert response.status_code == 302
    assert response.url == reverse("accounts:login")

    response.client.get(reverse("core:home"))
    assert response.status_code == 302
    assert response.wsgi_request.user.is_anonymous
    assert response.url.startswith(reverse("accounts:login"))
