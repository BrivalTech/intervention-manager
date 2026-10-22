import pytest
from django.urls import reverse

from apps.accounts.models import User


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("role", "expected_links"),
    [
        (User.Role.ADMIN, True),
        (User.Role.MANAGER, True),
        (User.Role.TECHNICIAN, False),
    ],
)
def test_navigation_links_by_role(
    client,
    django_user_model,
    role,
    expected_links,
):
    user = django_user_model.objects.create_user(
        username=f"user_{role.lower()}",
        role=role,
    )

    client.force_login(user)
    response = client.get(reverse("core:home"))

    assert response.status_code == 200

    clients_url = reverse("clients:list")
    technicians_url = reverse("accounts:technician_list")

    assert (f'href="{clients_url}"' in response.content.decode()) is expected_links
    assert (f'href="{technicians_url}"' in response.content.decode()) is expected_links


@pytest.mark.django_db
def test_clients_navigation_has_current_page(client, django_user_model):
    user = django_user_model.objects.create_user(
        username="admin",
        role=User.Role.ADMIN,
    )

    client.force_login(user)
    response = client.get(reverse("clients:list"))

    assert response.status_code == 200
    assert 'aria-current="page"' in response.content.decode()
