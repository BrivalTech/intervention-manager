from datetime import timedelta

import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone

from apps.accounts.models import User
from apps.clients.models import Client
from apps.interventions.models import Intervention
from apps.interventions.services import create_intervention, update_intervention


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


@pytest.mark.django_db
def test_update_intervention_keeps_data_on_validation_error(
    intervention_author,
):
    customer = Client.objects.create(name="Client validation")
    intervention = create_intervention(
        client=customer,
        created_by=intervention_author,
        title="Titre initial",
    )

    with pytest.raises(ValidationError):
        update_intervention(
            user=intervention_author,
            intervention=intervention,
            title="Titre modifié",
            starts_at=timezone.now() + timedelta(days=1),
        )

    intervention.refresh_from_db()

    assert intervention.title == "Titre initial"
    assert intervention.starts_at is None
    assert intervention.status == Intervention.Status.TO_PLAN


@pytest.mark.django_db
def test_cannot_update_completed_intervention(
    intervention_author,
):
    customer = Client.objects.create(name="Client terminé")
    intervention = create_intervention(
        client=customer,
        created_by=intervention_author,
        title="Intervention terminée",
    )

    intervention.status = Intervention.Status.COMPLETED
    intervention.report = "Intervention réalisée."
    intervention.save(update_fields=["status", "report"])

    with pytest.raises(PermissionError):
        update_intervention(
            user=intervention_author,
            intervention=intervention,
            title="Modification interdite",
        )

    intervention.refresh_from_db()
    assert intervention.title == "Intervention terminée"
