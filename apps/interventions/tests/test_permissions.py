import pytest
from django.contrib.auth.models import AnonymousUser

from apps.accounts.models import User
from apps.clients.models import Client
from apps.interventions.models import Intervention
from apps.interventions.permissions import (
    can_create_intervention,
    can_edit_intervention,
    can_manage_assignment,
    can_update_status,
)


@pytest.fixture
def intervention(db, intervention_author):
    customer = Client.objects.create(name="Client modification")

    return Intervention.objects.create(
        client=customer,
        created_by=intervention_author,
        title="Intervention à modifier",
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
def test_admin_and_manager_can_update_intervention(role, action, intervention_author):
    user = User.objects.create_user(
        username=f"user-{role.lower()}-{action}",
        password="test-password",
        role=role,
    )
    client = Client.objects.create(name="Entreprise Test")
    intervention = Intervention.objects.create(
        created_by=intervention_author,
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
def test_technician_can_only_start_or_complete_own_intervention(
    action, expected, intervention_author
):
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
