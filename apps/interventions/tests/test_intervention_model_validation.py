from datetime import datetime
from zoneinfo import ZoneInfo

import pytest
from django.core.exceptions import ValidationError

from apps.clients.models import Client
from apps.interventions.models import Intervention


@pytest.mark.django_db
def test_intervention_can_be_created_for_active_client(intervention_author):
    client = Client.objects.create(name="Entreprise Test")
    starts_at = datetime(2026, 11, 10, 9, tzinfo=ZoneInfo("Europe/Paris"))
    ends_at = datetime(2026, 11, 10, 11, tzinfo=ZoneInfo("Europe/Paris"))
    intervention = Intervention.objects.create(
        created_by=intervention_author,
        client=client,
        title="Maintenance du poste de travail",
        starts_at=starts_at,
        ends_at=ends_at,
    )

    assert intervention.client == client
    assert intervention.title == "Maintenance du poste de travail"
    assert intervention.starts_at == starts_at
    assert intervention.ends_at == ends_at


@pytest.mark.django_db
def test_intervention_is_to_plan_by_default(intervention_author):
    client = Client.objects.create(name="Entreprise Test")
    intervention = Intervention.objects.create(
        created_by=intervention_author,
        client=client,
        title="Maintenance du poste de travail",
    )

    assert intervention.status == Intervention.Status.TO_PLAN


@pytest.mark.django_db
def test_intervention_can_be_created_without_schedule(intervention_author):
    client = Client.objects.create(name="Entreprise Test")
    intervention = Intervention.objects.create(
        created_by=intervention_author,
        client=client,
        title="Maintenance du poste de travail",
        description="Vérifier le poste utilisateur.",
    )

    assert intervention.description == "Vérifier le poste utilisateur."
    assert intervention.starts_at is None


@pytest.mark.django_db
def test_intervention_title_is_required(intervention_author):
    client = Client.objects.create(name="Entreprise Test")
    intervention = Intervention.objects.create(
        created_by=intervention_author,
        client=client,
        title="",
    )

    with pytest.raises(ValidationError):
        intervention.full_clean()


@pytest.mark.django_db
def test_intervention_client_is_required(intervention_author):
    intervention = Intervention(
        created_by=intervention_author,
        title="Maintenance du poste de travail",
    )

    with pytest.raises(ValidationError):
        intervention.full_clean()


@pytest.mark.django_db
def test_intervention_cannot_be_created_for_archived_client(intervention_author):
    client = Client.objects.create(name="Entreprise Test", is_active=False)
    intervention = Intervention.objects.create(
        created_by=intervention_author,
        client=client,
        title="Maintenance du poste de travail",
    )

    with pytest.raises(ValidationError):
        intervention.full_clean()


@pytest.mark.django_db
def test_intervention_string_representation_is_title(intervention_author):
    client = Client.objects.create(name="Entreprise Test")
    intervention = Intervention.objects.create(
        created_by=intervention_author,
        client=client,
        title="Maintenance du poste de travail",
    )

    assert str(intervention) == "Maintenance du poste de travail"


@pytest.mark.django_db
def test_intervention_status_must_be_valid(intervention_author):
    client = Client.objects.create(name="Entreprise Test")
    intervention = Intervention.objects.create(
        created_by=intervention_author,
        client=client,
        title="Maintenance du poste de travail",
        status="INVALID",
    )

    with pytest.raises(ValidationError):
        intervention.full_clean()


@pytest.mark.parametrize(
    "status",
    [
        Intervention.Status.TO_PLAN,
        Intervention.Status.PLANNED,
        Intervention.Status.IN_PROGRESS,
        Intervention.Status.COMPLETED,
        Intervention.Status.CANCELLED,
    ],
)
@pytest.mark.django_db
def test_intervention_accepts_valid_status(status, intervention_author):
    client = Client.objects.create(name="Entreprise Test")
    starts_at = datetime(2026, 11, 10, 9, tzinfo=ZoneInfo("Europe/Paris"))
    ends_at = datetime(2026, 11, 10, 11, tzinfo=ZoneInfo("Europe/Paris"))
    intervention = Intervention.objects.create(
        created_by=intervention_author,
        client=client,
        title="Maintenance du poste de travail",
        starts_at=starts_at if status != Intervention.Status.TO_PLAN else None,
        ends_at=ends_at if status != Intervention.Status.TO_PLAN else None,
        status=(
            Intervention.Status.PLANNED
            if status != Intervention.Status.TO_PLAN
            else Intervention.Status.TO_PLAN
        ),
    )

    if status == Intervention.Status.IN_PROGRESS:
        intervention.start()
    elif status == Intervention.Status.COMPLETED:
        intervention.start()
        intervention.complete("Intervention terminée et vérifiée.")
    elif status == Intervention.Status.CANCELLED:
        intervention.cancel()

    intervention.refresh_from_db()

    assert intervention.status == status
    intervention.full_clean()
