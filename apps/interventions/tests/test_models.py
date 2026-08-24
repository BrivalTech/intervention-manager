import pytest
from django.core.exceptions import ValidationError

from apps.clients.models import Client
from apps.interventions.models import Intervention


@pytest.mark.django_db
def test_intervention_can_be_created_for_active_client():
    client = Client.objects.create(
        name="Entreprise Test",
    )
    intervention = Intervention.objects.create(
        client=client,
        title="Maintenance du poste de travail",
    )

    assert intervention.client == client
    assert intervention.title == "Maintenance du poste de travail"


@pytest.mark.django_db
def test_intervention_is_planned_by_default():
    client = Client.objects.create(
        name="Entreprise Test",
    )
    intervention = Intervention.objects.create(
        client=client,
        title="Maintenance du poste de travail",
    )

    assert intervention.status == intervention.Status.PLANNED


@pytest.mark.django_db
def test_intervention_can_be_created_without_scheduled():
    client = Client.objects.create(
        name="Entreprise Test",
    )
    intervention = Intervention.objects.create(
        client=client,
        title="Maintenance du poste de travail",
        description="Vérifier le poste utilisateur.",
    )

    assert intervention.description == "Vérifier le poste utilisateur."
    assert intervention.scheduled_at is None
    assert intervention.created_at is not None
    assert intervention.updated_at is not None


@pytest.mark.django_db
def test_intervention_title_is_required():
    client = Client.objects.create(
        name="Entreprise Test",
    )
    intervention = Intervention.objects.create(
        client=client,
        title="",
    )

    with pytest.raises(ValidationError):
        intervention.full_clean()


@pytest.mark.django_db
def test_intervention_client_is_required():
    intervention = Intervention(
        title="Maintenance du poste de travail",
    )

    with pytest.raises(ValidationError):
        intervention.full_clean()


@pytest.mark.django_db
def test_intervention_cannot_be_created_for_archived_client():
    client = Client.objects.create(
        name="Entreprise Test",
        is_active=False,
    )
    intervention = Intervention.objects.create(
        client=client,
        title="Maintenance du poste de travail",
    )

    with pytest.raises(ValidationError):
        intervention.full_clean()


@pytest.mark.django_db
def test_intervention_string_representation_is_title():
    client = Client.objects.create(
        name="Entreprise Test",
    )
    intervention = Intervention.objects.create(
        client=client,
        title="Maintenance du poste de travail",
    )

    assert str(intervention) == "Maintenance du poste de travail"


@pytest.mark.django_db
def test_intervention_status_must_be_valid():
    client = Client.objects.create(
        name="Entreprise Test",
    )
    intervention = Intervention.objects.create(
        client=client,
        title="Maintenance du poste de travail",
        status="INVALID",
    )

    with pytest.raises(ValidationError):
        intervention.full_clean()


@pytest.mark.parametrize(
    "status",
    [
        Intervention.Status.PLANNED,
        Intervention.Status.IN_PROGRESS,
        Intervention.Status.COMPLETED,
        Intervention.Status.CANCELLED,
    ],
)
@pytest.mark.django_db
def test_intervention_accepts_valid_satus(status):
    client = Client.objects.create(
        name="Entreprise Test",
    )
    intervention = Intervention.objects.create(
        client=client,
        title="Maintenance du poste de travail",
        status=status,
    )

    intervention.full_clean()
