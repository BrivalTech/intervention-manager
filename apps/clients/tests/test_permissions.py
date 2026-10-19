import pytest

from apps.accounts.models import User
from apps.clients.permissions import (
    can_archive_client,
    can_manage_clients,
    can_view_clients,
)


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("role", "can_view", "can_manage", "can_archive"),
    [
        (User.Role.ADMIN, True, True, True),
        (User.Role.MANAGER, True, True, False),
        (User.Role.TECHNICIAN, False, False, False),
    ],
)
def test_client_permissions(
    django_user_model,
    role,
    can_view,
    can_manage,
    can_archive,
):
    user = django_user_model.objects.create_user(
        username=f"user-{role.lower()}",
        password="TestPassword123",
        role=role,
    )

    assert can_view_clients(user) is can_view
    assert can_manage_clients(user) is can_manage
    assert can_archive_client(user) is can_archive


@pytest.mark.django_db
def test_inactive_user_cannot_access_clients(django_user_model):
    user = django_user_model.objects.create_user(
        username="inactive-user",
        password="TestPassword123",
        role=User.Role.ADMIN,
        is_active=False,
    )

    assert not can_view_clients(user)
    assert not can_manage_clients(user)
    assert not can_archive_client(user)
