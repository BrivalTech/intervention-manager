import pytest
from django.test import override_settings
from django.urls import reverse

from apps.accounts.models import User


@pytest.mark.django_db
@override_settings(DEBUG=False)
def test_permission_denied_uses_custom_403_template(client, django_user_model):
    user = django_user_model.objects.create_user(
        username="manager-error-page",
        password="TestPassword123!",
        role=User.Role.MANAGER,
    )

    client.force_login(user)
    response = client.get(reverse("core:design-system"))

    assert response.status_code == 403
    assert "403.html" in [template.name for template in response.templates]
    assert 'id="error-title"' in response.content.decode()
    assert "Accès interdit" in response.content.decode()
    assert reverse("core:home") in response.content.decode()


def test_anonymous_user_is_redirected_to_login_not_403(client):
    response = client.get(reverse("core:design-system"))

    assert response.status_code == 302
    assert response.url.startswith(reverse("accounts:login"))
