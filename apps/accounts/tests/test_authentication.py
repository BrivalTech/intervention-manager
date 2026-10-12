import pytest
from django.urls import reverse


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
