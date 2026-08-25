import pytest
from django.core.exceptions import ValidationError

from apps.accounts.models import User
from apps.clients.models import Client
from apps.interventions.models import Intervention
from apps.interventions.services import (
    assign_technician,
    create_intervention,
    unassign_technician,
    update_intervention_status,
)


@pytest.mark.django_db
def test_create_intervention_for_active_client():
    client = Client.objects.create(
        name="Entreprise Test",
    )
    intervention = create_intervention(
        client=client,
        title="Maintenance du poste de travail",
    )

    assert intervention.client == client
    assert intervention.title == "Maintenance du poste de travail"
    assert intervention.pk is not None


@pytest.mark.django_db
def test_cannot_create_intervention_for_archived_client():
    client = Client.objects.create(
        name="Entreprise Test",
        is_active=False,
    )

    with pytest.raises(ValidationError):
        create_intervention(
            client=client,
            title="Maintenance du poste de travail",
        )


@pytest.mark.django_db
def test_create_intervention_with_technician():
    client = Client.objects.create(
        name="Entreprise Test",
    )
    technician = User.objects.create_user(
        username="technician",
        password="test-password",
        role=User.Role.TECHNICIAN,
    )
    intervention = create_intervention(
        client=client,
        title="Maintenance du poste de travail",
        technician=technician,
    )

    assert intervention.technician == technician


@pytest.mark.django_db
def test_cannot_create_intervention_with_non_technician():
    client = Client.objects.create(
        name="Entreprise Test",
    )
    manager = User.objects.create_user(
        username="manager",
        password="test-password",
        role=User.Role.MANAGER,
    )

    with pytest.raises(ValidationError):
        create_intervention(
            client=client,
            title="Maintenance du poste de travail",
            technician=manager,
        )


@pytest.mark.django_db
def test_manager_can_assign_technician():
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
def test_admin_can_assign_technician():
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
def test_technician_cannot_assign_technician():
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
def test_manager_can_unassign_technician():
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
def test_admin_can_unassign_technician():
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
def test_technician_cannot_unassign_technician():
    client = Client.objects.create(
        name="Entreprise Test",
    )
    technician = User.objects.create_user(
        username="technician",
        password="test-password",
        role=User.Role.TECHNICIAN,
    )
    intervention = create_intervention(
        client=client,
        title="Maintenance du poste de travail",
        technician=technician,
    )

    with pytest.raises(PermissionError):
        unassign_technician(
            user=technician,
            intervention=intervention,
        )


@pytest.mark.django_db
def test_manager_can_start_intervention():
    client = Client.objects.create(
        name="Entreprise Test",
    )
    manager = User.objects.create_user(
        username="manager",
        password="test-password",
        role=User.Role.MANAGER,
    )
    intervention = create_intervention(
        client=client,
        title="Maintenance du poste de travail",
    )

    update_intervention_status(
        user=manager,
        intervention=intervention,
        action="start",
    )

    intervention.refresh_from_db()

    assert intervention.status == Intervention.Status.IN_PROGRESS


@pytest.mark.django_db
def test_technician_can_complete_own_intervention():
    client = Client.objects.create(
        name="Entreprise Test",
    )
    technician = User.objects.create_user(
        username="technician",
        password="test-password",
        role=User.Role.TECHNICIAN,
    )
    intervention = create_intervention(
        client=client,
        title="Maintenance du poste de travail",
        technician=technician,
    )

    intervention.start()
    update_intervention_status(
        user=technician,
        intervention=intervention,
        action="complete",
    )

    intervention.refresh_from_db()

    assert intervention.status == Intervention.Status.COMPLETED


@pytest.mark.django_db
def test_technician_cannot_cancel_intervention():
    client = Client.objects.create(
        name="Entreprise Test",
    )
    technician = User.objects.create_user(
        username="technician",
        password="test-password",
        role=User.Role.TECHNICIAN,
    )
    intervention = create_intervention(
        client=client,
        title="Maintenance du poste de travail",
        technician=technician,
    )

    with pytest.raises(PermissionError):
        update_intervention_status(
            user=technician,
            intervention=intervention,
            action="cancel",
        )


@pytest.mark.django_db
def test_unknown_status_action_is_rejected_by_service():
    client = Client.objects.create(
        name="Entreprise Test",
    )
    manager = User.objects.create_user(
        username="manager",
        password="test-password",
        role=User.Role.MANAGER,
    )
    intervention = create_intervention(
        client=client,
        title="Maintenance du poste de travail",
    )

    with pytest.raises(PermissionError):
        update_intervention_status(
            user=manager,
            intervention=intervention,
            action="unknown",
        )


@pytest.mark.parametrize(
    "final_status",
    [
        Intervention.Status.COMPLETED,
        Intervention.Status.CANCELLED,
    ],
)
@pytest.mark.django_db
def test_status_service_preserves_final_intervention_state(final_status):
    client = Client.objects.create(
        name="Entreprise Test",
    )
    manager = User.objects.create_user(
        username="manager",
        password="test-password",
        role=User.Role.MANAGER,
    )
    intervention = create_intervention(
        client=client,
        title="Maintenance du poste de travail",
    )

    if final_status == Intervention.Status.COMPLETED:
        intervention.start()
        intervention.complete()
    else:
        intervention.cancel()

        with pytest.raises(ValidationError):
            update_intervention_status(
                user=manager,
                intervention=intervention,
                action="start",
            )
