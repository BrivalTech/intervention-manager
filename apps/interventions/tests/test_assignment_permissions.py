import pytest

from apps.accounts.models import User
from apps.interventions.permissions import can_manage_assignment


@pytest.mark.parametrize(
    ("role", "expected"),
    [
        (User.Role.ADMIN, True),
        (User.Role.MANAGER, True),
        (User.Role.TECHNICIAN, False),
    ],
)
@pytest.mark.django_db
def test_user_can_manage_intervention_assignment_based_on_role(role, expected):
    user = User.objects.create_user(
        username=f"user-{role.lower()}",
        password="test-password",
        role=role,
    )

    assert can_manage_assignment(user) is expected
