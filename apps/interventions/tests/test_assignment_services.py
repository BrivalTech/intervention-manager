import pytest

from apps.accounts.models import User
from apps.clients.models import Client
from apps.interventions.services import (
    assign_technician,
    create_intervention,
    unassign_technician,
)


@pytest.mark.django_db
def test_manager_can_assign_technician(intervention_author):
    client = Client.objects.create(
        name="Entreprise Test",
    )
    manager = User.objects.create_user(
        username="manager",
        password="test-password",
        role=User.Role.MANAGER,
    )
    technician = User.objects.create_user(
        username="technician",
        password="test-password",
        role=User.Role.TECHNICIAN,
    )
    intervention = create_intervention(
        created_by=intervention_author,
        client=client,
        title="Maintenance du poste de travail",
    )

    assign_technician(
        user=manager,
        intervention=intervention,
        technician=technician,
    )

    intervention.refresh_from_db()

    assert intervention.technician == technician


@pytest.mark.django_db
def test_admin_can_assign_technician(intervention_author):
    client = Client.objects.create(
        name="Entreprise Test",
    )
    admin = User.objects.create_user(
        username="admin",
        password="test-password",
        role=User.Role.ADMIN,
    )
    technician = User.objects.create_user(
        username="technician",
        password="test-password",
        role=User.Role.TECHNICIAN,
    )
    intervention = create_intervention(
        created_by=intervention_author,
        client=client,
        title="Maintenance du poste de travail",
    )

    assign_technician(
        user=admin,
        intervention=intervention,
        technician=technician,
    )

    intervention.refresh_from_db()

    assert intervention.technician == technician


@pytest.mark.django_db
def test_technician_cannot_assign_technician(intervention_author):
    client = Client.objects.create(
        name="Entreprise Test",
    )
    technician = User.objects.create_user(
        username="technician",
        password="test-password",
        role=User.Role.TECHNICIAN,
    )
    other_technician = User.objects.create_user(
        username="other_technician",
        password="test-password",
        role=User.Role.TECHNICIAN,
    )
    intervention = create_intervention(
        created_by=intervention_author,
        client=client,
        title="Maintenance du poste de travail",
    )

    with pytest.raises(PermissionError):
        assign_technician(
            user=technician,
            intervention=intervention,
            technician=other_technician,
        )


@pytest.mark.django_db
def test_manager_can_unassign_technician(intervention_author):
    client = Client.objects.create(
        name="Entreprise Test",
    )
    manager = User.objects.create_user(
        username="manager",
        password="test-password",
        role=User.Role.MANAGER,
    )
    technician = User.objects.create_user(
        username="technician",
        password="test-password",
        role=User.Role.TECHNICIAN,
    )
    intervention = create_intervention(
        created_by=intervention_author,
        client=client,
        title="Maintenance du poste de travail",
        technician=technician,
    )

    unassign_technician(
        user=manager,
        intervention=intervention,
    )

    intervention.refresh_from_db()

    assert intervention.technician is None


@pytest.mark.django_db
def test_admin_can_unassign_technician(intervention_author):
    client = Client.objects.create(
        name="Entreprise Test",
    )
    admin = User.objects.create_user(
        username="admin",
        password="test-password",
        role=User.Role.ADMIN,
    )
    technician = User.objects.create_user(
        username="technician",
        password="test-password",
        role=User.Role.TECHNICIAN,
    )
    intervention = create_intervention(
        created_by=intervention_author,
        client=client,
        title="Maintenance du poste de travail",
        technician=technician,
    )

    unassign_technician(
        user=admin,
        intervention=intervention,
    )

    intervention.refresh_from_db()

    assert intervention.technician is None


@pytest.mark.django_db
def test_technician_cannot_unassign_technician(intervention_author):
    client = Client.objects.create(
        name="Entreprise Test",
    )
    technician = User.objects.create_user(
        username="technician",
        password="test-password",
        role=User.Role.TECHNICIAN,
    )
    intervention = create_intervention(
        created_by=intervention_author,
        client=client,
        title="Maintenance du poste de travail",
        technician=technician,
    )

    with pytest.raises(PermissionError):
        unassign_technician(
            user=technician,
            intervention=intervention,
        )
