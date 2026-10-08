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
