import pytest
from django.urls import reverse


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
