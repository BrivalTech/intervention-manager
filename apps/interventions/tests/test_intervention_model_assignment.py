import pytest
from django.core.exceptions import ValidationError

from apps.accounts.models import User
from apps.clients.models import Client
from apps.interventions.models import Intervention


@pytest.mark.django_db
def test_intervention_can_be_created_without_technician(intervention_author):
    client = Client.objects.create(name="Entreprise Test")
    intervention = Intervention.objects.create(
        created_by=intervention_author,
        client=client,
        title="Maintenance du poste de travail",
    )

    assert intervention.technician is None


@pytest.mark.django_db
def test_technician_can_be_assigned_to_an_intervention(intervention_author):
    client = Client.objects.create(name="Entreprise Test")
    technician = User.objects.create_user(
        username="technician",
        password="test-password",
        role=User.Role.TECHNICIAN,
    )
    intervention = Intervention.objects.create(
        created_by=intervention_author,
        client=client,
        title="Maintenance du poste de travail",
        technician=technician,
    )

    assert intervention.technician == technician


@pytest.mark.parametrize(
    "role",
    [
        User.Role.ADMIN,
        User.Role.MANAGER,
    ],
)
@pytest.mark.django_db
def test_non_technician_cannot_be_assigned_to_an_intervention(
    role, intervention_author
):
    client = Client.objects.create(name="Entreprise Test")
    user = User.objects.create_user(
        username=f"user-{role.lower()}",
        password="test-password",
        role=role,
    )
    intervention = Intervention.objects.create(
        created_by=intervention_author,
        client=client,
        title="Maintenance du poste de travail",
        technician=user,
    )

    with pytest.raises(ValidationError):
        intervention.full_clean()


@pytest.mark.django_db
def test_technician_can_ne_assigned_after_intervention_created(intervention_author):
    client = Client.objects.create(name="Entreprise Test")
    technician = User.objects.create_user(
        username="technician",
        password="test-password",
        role=User.Role.TECHNICIAN,
    )
    intervention = Intervention.objects.create(
        created_by=intervention_author,
        client=client,
        title="Maintenance du poste de travail",
    )

    intervention.assign_technician(technician)
    intervention.refresh_from_db()

    assert intervention.technician == technician


@pytest.mark.parametrize(
    "role",
    [
        User.Role.ADMIN,
        User.Role.MANAGER,
    ],
)
@pytest.mark.django_db
def test_non_technician_cannot_be_assigned_after_intervention_created(
    role, intervention_author
):
    client = Client.objects.create(name="Entreprise Test")
    user = User.objects.create_user(
        username=f"user-{role.lower()}",
        password="test-password",
        role=role,
    )
    intervention = Intervention.objects.create(
        created_by=intervention_author,
        client=client,
        title="Maintenance du poste de travail",
        technician=user,
    )

    with pytest.raises(ValidationError):
        intervention.assign_technician(user)


@pytest.mark.parametrize(
    "status",
    [
        Intervention.Status.PLANNED,
        Intervention.Status.IN_PROGRESS,
    ],
)
@pytest.mark.django_db
def test_technician_can_be_unassigned_from_active_intervention(
    status, intervention_author
):
    client = Client.objects.create(name="Entreprise Test")
    technician = User.objects.create_user(
        username=f"technician-{status.lower()}",
        password="test-password",
        role=User.Role.TECHNICIAN,
    )
    intervention = Intervention.objects.create(
        created_by=intervention_author,
        client=client,
        title="Maintenance du poste de travail",
        technician=technician,
        status=status,
    )

    intervention.unassign_technician()
    intervention.refresh_from_db()

    assert intervention.technician is None


@pytest.mark.parametrize(
    "status",
    [
        Intervention.Status.COMPLETED,
        Intervention.Status.CANCELLED,
    ],
)
@pytest.mark.django_db
def test_technician_cannot_be_unassigned_from_final_intervention(
    status, intervention_author
):
    client = Client.objects.create(name="Entreprise Test")
    technician = User.objects.create_user(
        username=f"technician-{status.lower()}",
        password="test-password",
        role=User.Role.TECHNICIAN,
    )
    intervention = Intervention.objects.create(
        created_by=intervention_author,
        client=client,
        title="Maintenance du poste de travail",
        technician=technician,
        status=status,
    )

    with pytest.raises(ValidationError):
        intervention.unassign_technician()


@pytest.mark.parametrize(
    "status",
    [
        Intervention.Status.COMPLETED,
        Intervention.Status.CANCELLED,
    ],
)
@pytest.mark.django_db
def test_technician_cannot_be_assigned_to_finale_intervention(
    status, intervention_author
):
    client = Client.objects.create(name="Entreprise Test")
    technician = User.objects.create_user(
        username=f"technician-{status.lower()}",
        password="test-password",
        role=User.Role.TECHNICIAN,
    )
    intervention = Intervention.objects.create(
        created_by=intervention_author,
        client=client,
        title="Maintenance du poste de travail",
        technician=technician,
        status=status,
    )

    with pytest.raises(ValidationError):
        intervention.assign_technician(technician)


@pytest.mark.django_db
def test_technician_can_be_reassigned_on_active_intervention(intervention_author):
    client = Client.objects.create(name="Entreprise Test")
    first_technician = User.objects.create_user(
        username="first-technician",
        password="test-password",
        role=User.Role.TECHNICIAN,
    )
    second_technician = User.objects.create_user(
        username="second-technician",
        password="test-password",
        role=User.Role.TECHNICIAN,
    )
    intervention = Intervention.objects.create(
        created_by=intervention_author,
        client=client,
        title="Maintenance du poste de travail",
        technician=first_technician,
    )

    intervention.assign_technician(second_technician)
    intervention.refresh_from_db()

    assert intervention.technician == second_technician


@pytest.mark.django_db
def test_intervention_without_technician_can_be_unassigned(intervention_author):
    client = Client.objects.create(name="Entreprise Test")
    intervention = Intervention.objects.create(
        created_by=intervention_author,
        client=client,
        title="Maintenance du poste de travail",
    )

    intervention.unassign_technician()
    intervention.refresh_from_db()

    assert intervention.technician is None
