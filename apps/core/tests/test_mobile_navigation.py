import pytest
from django.urls import reverse

from apps.accounts.models import User


@pytest.mark.django_db
def test_navigation_uses_native_details_without_javascript(client, django_user_model):
    user = django_user_model.objects.create_user(
        username="mobile_nav_admin",
        role=User.Role.ADMIN,
    )

    client.force_login(user)
    response = client.get(reverse("core:home"))

    assert response.status_code == 200

    content = response.content.decode()
    assert '<details class="navigation-disclosure">' in content
    assert '<summary class="navigation-toggle">' in content
    assert 'aria-label="Navigation principale"' in content
    assert 'aria-current="page"' in content
    assert "<script" not in content


@pytest.mark.django_db
def test_mobile_navigation_keeps_post_logout(client, django_user_model):
    user = django_user_model.objects.create_user(
        username="mobile_nav_logout",
        role=User.Role.ADMIN,
    )

    client.force_login(user)
    response = client.get(reverse("core:home"))

    content = response.content.decode()
    assert 'method="post"' in content
    assert f'action="{reverse("accounts:logout")}"' in content
