import pytest
from django.urls import reverse

from apps.accounts.models import User


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


@pytest.mark.django_db
def test_navigation_uses_post_logout(client, django_user_model):
    user = django_user_model.objects.create_user(
        username="admin",
        password="TestPassword123!",
        role=User.Role.ADMIN,
    )

    client.force_login(user)
    response = client.get(reverse("core:home"))
    content = response.content.decode()

    assert response.status_code == 200
    assert 'method="post"' in content
    assert f'action="{reverse("accounts:logout")}"' in content
