import pytest

from apps.accounts.models import User
from apps.accounts.permissions import (
    can_manage_technicians,
    can_view_technicians,
)


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("role", "can_view", "can_manage"),
    [
        (User.Role.ADMIN, True, True),
        (User.Role.MANAGER, True, False),
        (User.Role.TECHNICIAN, False, False),
    ],
)
def test_technician_permissions(django_user_model, role, can_view, can_manage):
    user = django_user_model.objects.create_user(
        username=f"user-{role.lower()}",
        password="TestPassword123",
        role=role,
    )

    assert can_view_technicians(user) is can_view
    assert can_manage_technicians(user) is can_manage
