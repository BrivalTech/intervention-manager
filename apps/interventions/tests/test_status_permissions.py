import pytest
from django.contrib.auth.models import AnonymousUser

from apps.accounts.models import User
from apps.clients.models import Client
from apps.interventions.permissions import can_update_status

from ..models import Intervention


@pytest.mark.parametrize(
    "role",
    [
        User.Role.ADMIN,
        User.Role.MANAGER,
    ],
)
@pytest.mark.parametrize(
    "action",
    [
        "start",
        "complete",
        "cancel",
    ],
)
@pytest.mark.django_db
def test_admin_and_manager_can_update_intervention(role, action, intervention_author):
    user = User.objects.create_user(
        username=f"user-{role.lower()}-{action}",
        password="test-password",
        role=role,
    )
    client = Client.objects.create(name="Entreprise Test")
    status_by_action = {
        "start": Intervention.Status.PLANNED,
        "complete": Intervention.Status.IN_PROGRESS,
        "cancel": Intervention.Status.TO_PLAN,
    }
    intervention = Intervention.objects.create(
        created_by=intervention_author,
        client=client,
        title="Maintenance du poste de travail",
        status=status_by_action[action],
    )

    assert can_update_status(user, intervention, action) is True


@pytest.mark.parametrize(
    ("action", "expected"),
    [
        ("start", True),
        ("complete", True),
        ("cancel", False),
    ],
)
@pytest.mark.django_db
def test_technician_can_only_start_or_complete_own_intervention(
    action, expected, intervention_author
):
    technician = User.objects.create_user(
        username=f"technician-{action}",
        password="test-password",
        role=User.Role.TECHNICIAN,
    )
    client = Client.objects.create(name="Entreprise Test")
    status_by_action = {
        "start": Intervention.Status.PLANNED,
        "complete": Intervention.Status.IN_PROGRESS,
        "cancel": Intervention.Status.TO_PLAN,
    }
    intervention = Intervention.objects.create(
        created_by=intervention_author,
        client=client,
        title="Maintenance du poste de travail",
        technician=technician,
        status=status_by_action[action],
    )

    assert can_update_status(technician, intervention, action) is expected


@pytest.mark.parametrize(
    "action",
    [
        "start",
        "complete",
        "cancel",
    ],
)
@pytest.mark.django_db
def test_technician_cannot_update_other_technician_intervention(
    action, intervention_author
):
    technician = User.objects.create_user(
        username=f"technician-{action}",
        password="test-password",
        role=User.Role.TECHNICIAN,
    )
    other_technician = User.objects.create_user(
        username=f"other-technician-{action}",
        password="test-password",
        role=User.Role.TECHNICIAN,
    )
    client = Client.objects.create(name="Entreprise Test")
    intervention = Intervention.objects.create(
        created_by=intervention_author,
        client=client,
        title="Maintenance du poste de travail",
        technician=other_technician,
    )

    assert can_update_status(technician, intervention, action) is False


@pytest.mark.parametrize(
    "action",
    [
        "start",
        "complete",
        "cancel",
    ],
)
@pytest.mark.django_db
def test_technician_cannot_update_unassigned_intervention(action, intervention_author):
    technician = User.objects.create_user(
        username=f"technician-{action}",
        password="test-password",
        role=User.Role.TECHNICIAN,
    )
    client = Client.objects.create(name="Entreprise Test")
    intervention = Intervention.objects.create(
        created_by=intervention_author,
        client=client,
        title="Maintenance du poste de travail",
    )

    assert can_update_status(technician, intervention, action) is False


@pytest.mark.parametrize(
    "role",
    [
        User.Role.ADMIN,
        User.Role.MANAGER,
        User.Role.TECHNICIAN,
    ],
)
@pytest.mark.django_db
def test_unknown_status_action_is_denied(role, intervention_author):
    user = User.objects.create_user(
        username=f"user-{role.lower()}",
        password="test-password",
        role=role,
    )
    client = Client.objects.create(name="Entreprise Test")
    intervention = Intervention.objects.create(
        created_by=intervention_author,
        client=client,
        title="Maintenance du poste de travail",
        technician=user if role == User.Role.TECHNICIAN else None,
    )

    assert can_update_status(user, intervention, role) is False


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("status", "action", "expected"),
    [
        (Intervention.Status.TO_PLAN, "start", False),
        (Intervention.Status.TO_PLAN, "complete", False),
        (Intervention.Status.TO_PLAN, "cancel", True),
        (Intervention.Status.PLANNED, "start", True),
        (Intervention.Status.PLANNED, "complete", False),
        (Intervention.Status.PLANNED, "cancel", True),
        (Intervention.Status.IN_PROGRESS, "start", False),
        (Intervention.Status.IN_PROGRESS, "complete", True),
        (Intervention.Status.IN_PROGRESS, "cancel", True),
        (Intervention.Status.COMPLETED, "start", False),
        (Intervention.Status.COMPLETED, "complete", False),
        (Intervention.Status.COMPLETED, "cancel", False),
        (Intervention.Status.CANCELLED, "start", False),
        (Intervention.Status.CANCELLED, "complete", False),
        (Intervention.Status.CANCELLED, "cancel", False),
    ],
)
def test_status_transition_permissions(
    intervention_author,
    intervention,
    status,
    action,
    expected,
):
    intervention.status = status

    assert (
        can_update_status(
            intervention_author,
            intervention,
            action,
        )
        is expected
    )


def test_anonymous_user_cannot_update_status(intervention):
    intervention.status = Intervention.Status.PLANNED

    assert (
        can_update_status(
            AnonymousUser(),
            intervention,
            "start",
        )
        is False
    )


@pytest.mark.django_db
def test_inactive_user_cannot_update_status(django_user_model, intervention):
    user = django_user_model.objects.create_user(
        username="inactive-status-user",
        role=User.Role.ADMIN,
        is_active=False,
    )

    intervention.status = Intervention.Status.PLANNED

    assert can_update_status(user, intervention, "start") is False
