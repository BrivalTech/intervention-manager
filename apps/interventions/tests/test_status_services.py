from datetime import timedelta

import pytest
from django.utils import timezone

from apps.accounts.models import User
from apps.clients.models import Client
from apps.interventions.models import Intervention
from apps.interventions.services import create_intervention, update_intervention_status


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

    with pytest.raises(PermissionError):
        update_intervention_status(
            user=manager,
            intervention=intervention,
            action="start",
        )

    intervention.refresh_from_db()
    assert intervention.status == final_status
