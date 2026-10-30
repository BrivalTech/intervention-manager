import pytest
from django.contrib.auth.models import AnonymousUser

from apps.accounts.models import User
from apps.interventions.permissions import can_edit_intervention

from ..models import Intervention


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("role", "expected"),
    [
        (User.Role.ADMIN, True),
        (User.Role.MANAGER, True),
        (User.Role.TECHNICIAN, False),
    ],
)
def test_can_edit_intervention_by_role(
    django_user_model,
    intervention,
    role,
    expected,
):
    user = django_user_model.objects.create_user(
        username=f"edit-{role.lower()}",
        role=role,
    )

    assert can_edit_intervention(user, intervention) is expected


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("status", "expected"),
    [
        (Intervention.Status.TO_PLAN, True),
        (Intervention.Status.PLANNED, True),
        (Intervention.Status.IN_PROGRESS, False),
        (Intervention.Status.COMPLETED, False),
        (Intervention.Status.CANCELLED, False),
    ],
)
def test_can_edit_intervention_by_status(
    intervention_author,
    intervention,
    status,
    expected,
):
    intervention.status = status

    assert can_edit_intervention(intervention_author, intervention) is expected


def test_anonymous_user_cannot_edit_intervention(intervention):
    assert can_edit_intervention(AnonymousUser(), intervention) is False


@pytest.mark.django_db
def test_inactive_user_cannot_edit_intervention(
    django_user_model,
    intervention,
):
    user = django_user_model.objects.create_user(
        username="inactive-editor",
        role=User.Role.ADMIN,
        is_active=False,
    )

    assert can_edit_intervention(user, intervention) is False
