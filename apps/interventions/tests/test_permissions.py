import pytest

from apps.accounts.models import User
from apps.clients.models import Client
from apps.interventions.models import Intervention
from apps.interventions.permissions import (
    can_manage_assignment,
    can_update_status,
)


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
def test_admin_and_manager_can_update_intervention(role, action):
    user = User.objects.create_user(
        username=f"user-{role.lower()}-{action}",
        password="test-password",
        role=role,
    )
    client = Client.objects.create(name="Entreprise Test")
    intervention = Intervention.objects.create(
        client=client,
        title="Maintenance du poste de travail",
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
def test_technician_can_only_start_or_complete_own_intervention(action, expected):
    technician = User.objects.create_user(
        username=f"technician-{action}",
        password="test-password",
        role=User.Role.TECHNICIAN,
    )
    client = Client.objects.create(name="Entreprise Test")
    intervention = Intervention.objects.create(
        client=client,
        title="Maintenance du poste de travail",
        technician=technician,
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
def test_technician_cannot_update_other_technician_intervention(action):
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
def test_technician_cannot_update_unassigned_intervention(action):
    technician = User.objects.create_user(
        username=f"technician-{action}",
        password="test-password",
        role=User.Role.TECHNICIAN,
    )
    client = Client.objects.create(name="Entreprise Test")
    intervention = Intervention.objects.create(
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
def test_unknown_status_action_is_denied(role):
    user = User.objects.create_user(
        username=f"user-{role.lower()}",
        password="test-password",
        role=role,
    )
    client = Client.objects.create(name="Entreprise Test")
    intervention = Intervention.objects.create(
        client=client,
        title="Maintenance du poste de travail",
        technician=user if role == User.Role.TECHNICIAN else None,
    )

    assert can_update_status(user, intervention, role) is False
