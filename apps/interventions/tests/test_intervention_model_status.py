from datetime import datetime
from zoneinfo import ZoneInfo

import pytest
from django.core.exceptions import ValidationError

from apps.clients.models import Client
from apps.interventions.models import Intervention


@pytest.mark.django_db
def test_planned_intervention_can_be_started(intervention_author):
    client = Client.objects.create(name="Entreprise Test")
    intervention = Intervention.objects.create(
        created_by=intervention_author,
        client=client,
        title="Maintenance du poste de travail",
        status=Intervention.Status.PLANNED,
        starts_at=datetime(2026, 11, 10, 9, tzinfo=ZoneInfo("Europe/Paris")),
        ends_at=datetime(2026, 11, 10, 11, tzinfo=ZoneInfo("Europe/Paris")),
    )

    intervention.start()
    intervention.refresh_from_db()

    assert intervention.status == Intervention.Status.IN_PROGRESS


@pytest.mark.django_db
def test_in_progress_intervention_can_be_completed(intervention_author):
    client = Client.objects.create(name="Entreprise Test")
    intervention = Intervention.objects.create(
        created_by=intervention_author,
        client=client,
        title="Maintenance du poste de travail",
        status=Intervention.Status.IN_PROGRESS,
    )

    intervention.complete("Intervention terminée et vérifiée.")
    intervention.refresh_from_db()

    assert intervention.status == Intervention.Status.COMPLETED


@pytest.mark.parametrize(
    "status",
    [
        Intervention.Status.TO_PLAN,
        Intervention.Status.PLANNED,
        Intervention.Status.IN_PROGRESS,
    ],
)
@pytest.mark.django_db
def test_intervention_can_be_cancelled(status, intervention_author):
    client = Client.objects.create(name="Entreprise Test")
    intervention = Intervention.objects.create(
        created_by=intervention_author,
        client=client,
        title="Maintenance du poste de travail",
        status=status,
    )

    intervention.cancel()
    intervention.refresh_from_db()

    assert intervention.status == Intervention.Status.CANCELLED


@pytest.mark.parametrize(
    "status",
    [
        Intervention.Status.TO_PLAN,
        Intervention.Status.IN_PROGRESS,
        Intervention.Status.COMPLETED,
        Intervention.Status.CANCELLED,
    ],
)
@pytest.mark.django_db
def test_only_planned_intervention_can_be_started(status, intervention_author):
    client = Client.objects.create(name="Entreprise Test")
    intervention = Intervention.objects.create(
        created_by=intervention_author,
        client=client,
        title="Maintenance du poste de travail",
        status=status,
    )

    with pytest.raises(ValidationError):
        intervention.start()


@pytest.mark.parametrize(
    "status",
    [
        Intervention.Status.PLANNED,
        Intervention.Status.COMPLETED,
        Intervention.Status.CANCELLED,
    ],
)
@pytest.mark.django_db
def test_only_in_progress_intervention_can_be_completed(status, intervention_author):
    client = Client.objects.create(name="Entreprise Test")
    intervention = Intervention.objects.create(
        created_by=intervention_author,
        client=client,
        title="Maintenance du poste de travail",
        status=status,
    )

    with pytest.raises(ValidationError):
        intervention.complete("Intervention terminée et vérifiée.")


@pytest.mark.parametrize(
    "initial_status",
    [
        Intervention.Status.COMPLETED,
        Intervention.Status.CANCELLED,
    ],
)
@pytest.mark.django_db
def test_completed_or_cancelled_intervention_cannot_be_cancelled(
    initial_status, intervention_author
):
    client = Client.objects.create(name="Entreprise Test")
    intervention = Intervention.objects.create(
        created_by=intervention_author,
        client=client,
        title="Maintenance du poste de travail",
        status=initial_status,
    )

    with pytest.raises(ValidationError):
        intervention.cancel()
