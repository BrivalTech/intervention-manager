from datetime import timedelta

import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone

from apps.accounts.models import User
from apps.clients.models import Client
from apps.interventions.models import Intervention
from apps.interventions.services import (
    assign_technician,
    create_intervention,
    unassign_technician,
    update_intervention,
    update_intervention_status,
)


@pytest.mark.django_db
def test_create_intervention_for_active_client(intervention_author):
    client = Client.objects.create(
        name="Entreprise Test",
    )
    intervention = create_intervention(
        created_by=intervention_author,
        client=client,
        title="Maintenance du poste de travail",
    )

    assert intervention.client == client
    assert intervention.title == "Maintenance du poste de travail"
    assert intervention.pk is not None


@pytest.mark.django_db
def test_cannot_create_intervention_for_archived_client(intervention_author):
    client = Client.objects.create(
        name="Entreprise Test",
        is_active=False,
    )

    with pytest.raises(ValidationError):
        create_intervention(
            created_by=intervention_author,
            client=client,
            title="Maintenance du poste de travail",
        )


@pytest.mark.django_db
def test_create_intervention_with_technician(intervention_author):
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

    assert intervention.technician == technician


@pytest.mark.django_db
def test_cannot_create_intervention_with_non_technician(intervention_author):
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
            created_by=intervention_author,
            client=client,
            title="Maintenance du poste de travail",
            technician=manager,
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


@pytest.mark.django_db
def test_manager_can_start_intervention(intervention_author):
    client = Client.objects.create(
        name="Entreprise Test",
    )
    manager = User.objects.create_user(
        username="manager",
        password="test-password",
        role=User.Role.MANAGER,
    )
    start = timezone.now() + timedelta(days=1)
    intervention = create_intervention(
        created_by=intervention_author,
        client=client,
        title="Maintenance du poste de travail",
        starts_at=start,
        ends_at=start + timedelta(hours=2),
    )

    update_intervention_status(
        user=manager,
        intervention=intervention,
        action="start",
    )

    intervention.refresh_from_db()

    assert intervention.status == Intervention.Status.IN_PROGRESS


@pytest.mark.django_db
def test_technician_can_complete_own_intervention(intervention_author):
    client = Client.objects.create(
        name="Entreprise Test",
    )
    technician = User.objects.create_user(
        username="technician",
        password="test-password",
        role=User.Role.TECHNICIAN,
    )
    start = timezone.now() + timedelta(days=1)
    intervention = create_intervention(
        created_by=intervention_author,
        client=client,
        title="Maintenance du poste de travail",
        technician=technician,
        starts_at=start,
        ends_at=start + timedelta(hours=2),
    )

    intervention.start()
    update_intervention_status(
        user=technician,
        intervention=intervention,
        action="complete",
        report="Intervention terminée et vérifiée.",
    )

    intervention.refresh_from_db()

    assert intervention.status == Intervention.Status.COMPLETED


@pytest.mark.django_db
def test_technician_cannot_cancel_intervention(intervention_author):
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
        update_intervention_status(
            user=technician,
            intervention=intervention,
            action="cancel",
        )


@pytest.mark.django_db
def test_unknown_status_action_is_rejected_by_service(intervention_author):
    client = Client.objects.create(
        name="Entreprise Test",
    )
    manager = User.objects.create_user(
        username="manager",
        password="test-password",
        role=User.Role.MANAGER,
    )
    intervention = create_intervention(
        created_by=intervention_author,
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
def test_status_service_preserves_final_intervention_state(
    final_status, intervention_author
):
    client = Client.objects.create(
        name="Entreprise Test",
    )
    manager = User.objects.create_user(
        username="manager",
        password="test-password",
        role=User.Role.MANAGER,
    )
    start = timezone.now() + timedelta(days=1)
    intervention = create_intervention(
        created_by=intervention_author,
        client=client,
        title="Maintenance du poste de travail",
        starts_at=start,
        ends_at=start + timedelta(hours=2),
    )

    if final_status == Intervention.Status.COMPLETED:
        intervention.start()
        intervention.complete("Intervention terminée et vérifiée.")
    else:
        intervention.cancel()

        with pytest.raises(ValidationError):
            update_intervention_status(
                user=manager,
                intervention=intervention,
                action="start",
            )


@pytest.mark.django_db
def test_create_intervention_without_dates_is_to_plan(intervention_author):
    client = Client.objects.create(name="Client à planifier")
    intervention = create_intervention(
        client=client,
        created_by=intervention_author,
        title="Intervention à planifier",
    )

    assert intervention.status == Intervention.Status.TO_PLAN
    assert intervention.starts_at is None
    assert intervention.ends_at is None


@pytest.mark.django_db
def test_create_intervention_with_dates_is_planned(intervention_author):
    client = Client.objects.create(name="Client planifié")
    start = timezone.now() + timedelta(days=1)
    intervention = create_intervention(
        client=client,
        created_by=intervention_author,
        title="Intervention planifiée",
        starts_at=start,
        ends_at=start + timedelta(hours=2),
    )

    assert intervention.status == Intervention.Status.PLANNED


@pytest.mark.django_db
def test_update_intervention_general_information(intervention_author):
    client = Client.objects.create(name="Client modification")
    intervention = create_intervention(
        client=client,
        created_by=intervention_author,
        title="Ancien titre",
    )

    update_intervention(
        user=intervention_author,
        intervention=intervention,
        title="Nouveau titre",
        description="Nouvelle description",
    )

    intervention.refresh_from_db()

    assert intervention.title == "Nouveau titre"
    assert intervention.description == "Nouvelle description"
    assert intervention.status == Intervention.Status.TO_PLAN


@pytest.mark.django_db
def test_update_intervention_sets_planned_status(intervention_author):
    client = Client.objects.create(name="Client planification")
    intervention = create_intervention(
        client=client,
        created_by=intervention_author,
        title="Intervention à planifier",
    )

    start = timezone.now() + timedelta(days=1)

    update_intervention(
        user=intervention_author,
        intervention=intervention,
        starts_at=start,
        ends_at=start + timedelta(hours=2),
    )

    intervention.refresh_from_db()

    assert intervention.status == Intervention.Status.PLANNED


@pytest.mark.django_db
def test_update_intervention_removes_schedule(intervention_author):
    client = Client.objects.create(name="Client déplanification")
    start = timezone.now() + timedelta(days=1)

    intervention = create_intervention(
        client=client,
        created_by=intervention_author,
        title="Intervention planifiée",
        starts_at=start,
        ends_at=start + timedelta(hours=2),
    )

    update_intervention(
        user=intervention_author,
        intervention=intervention,
        starts_at=None,
        ends_at=None,
    )

    intervention.refresh_from_db()

    assert intervention.status == Intervention.Status.TO_PLAN
    assert intervention.starts_at is None
    assert intervention.ends_at is None


@pytest.mark.django_db
def test_update_intervention_rejects_incomplete_schedule(intervention_author):
    client = Client.objects.create(name="Client dates invalides")
    intervention = create_intervention(
        client=client,
        created_by=intervention_author,
        title="Intervention sans dates",
    )

    with pytest.raises(ValidationError):
        update_intervention(
            user=intervention_author,
            intervention=intervention,
            starts_at=timezone.now() + timedelta(days=1),
        )

    intervention.refresh_from_db()

    assert intervention.status == Intervention.Status.TO_PLAN
    assert intervention.starts_at is None


@pytest.mark.django_db
def test_technician_cannot_update_intervention(intervention_author):
    client = Client.objects.create(name="Client permissions")
    technician = User.objects.create_user(
        username="technician-update",
        role=User.Role.TECHNICIAN,
    )

    intervention = create_intervention(
        client=client,
        created_by=intervention_author,
        title="Intervention protégée",
    )

    with pytest.raises(PermissionError):
        update_intervention(
            user=technician,
            intervention=intervention,
            title="Modification interdite",
        )

    intervention.refresh_from_db()
    assert intervention.title == "Intervention protégée"
