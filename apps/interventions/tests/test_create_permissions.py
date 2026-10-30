import pytest
from django.contrib.auth.models import AnonymousUser

from apps.accounts.models import User
from apps.interventions.permissions import can_create_intervention


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("role", "expected"),
    [
        (User.Role.ADMIN, True),
        (User.Role.MANAGER, True),
        (User.Role.TECHNICIAN, False),
    ],
)
def test_can_create_intervention_by_role(
    django_user_model,
    role,
    expected,
):
    user = django_user_model.objects.create_user(
        username=f"create-{role.lower()}",
        role=role,
    )

    assert can_create_intervention(user) is expected


def test_anonymous_user_cannot_create_intervention():
    assert can_create_intervention(AnonymousUser()) is False


@pytest.mark.django_db
def test_inactive_user_cannot_create_intervention(django_user_model):
    user = django_user_model.objects.create_user(
        username="inactive-creator",
        role=User.Role.ADMIN,
        is_active=False,
    )

    assert can_create_intervention(user) is False
