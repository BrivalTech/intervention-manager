from uuid import uuid4

import pytest
from django.test import override_settings
from django.urls import reverse

from apps.accounts.models import User


@override_settings(DEBUG=False)
def test_unknown_url_uses_custom_404_template(client):
    response = client.get("/page-inexistante/")

    assert response.status_code == 404
    assert "404.html" in [template.name for template in response.templates]
    assert 'id="error-title"' in response.content.decode()
    assert "Page introuvable" in response.content.decode()
    assert reverse("core:home") in response.content.decode()


@pytest.mark.django_db
@override_settings(DEBUG=False)
def test_missing_client_uses_custom_404_template(client, django_user_model):
    user = django_user_model.objects.create_user(
        username="admin-404-page",
        password="TestPassword123!",
        role=User.Role.ADMIN,
    )

    client.force_login(user)
    response = client.get(reverse("clients:detail", kwargs={"public_id": uuid4()}))

    assert response.status_code == 404
    assert "404.html" in [template.name for template in response.templates]
