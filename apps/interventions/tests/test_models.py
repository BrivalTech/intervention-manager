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


@pytest.mark.django_db
def test_planned_intervention_can_be_started():
    client = Client.objects.create(
        name="Entreprise Test",
    )
    intervention = Intervention.objects.create(
        client=client,
        title="Maintenance du poste de travail",
    )

    intervention.start()
    intervention.refresh_from_db()

    assert intervention.status == Intervention.Status.IN_PROGRESS


@pytest.mark.django_db
def test_in_progress_intervention_can_be_completed():
    client = Client.objects.create(
        name="Entreprise Test",
    )
    intervention = Intervention.objects.create(
        client=client,
        title="Maintenance du poste de travail",
        status=Intervention.Status.IN_PROGRESS,
    )

    intervention.complete()
    intervention.refresh_from_db()

    assert intervention.status == Intervention.Status.COMPLETED


@pytest.mark.parametrize(
    "status",
    [
        Intervention.Status.PLANNED,
        Intervention.Status.IN_PROGRESS,
    ],
)
@pytest.mark.django_db
def test_intervention_can_be_cancelled(status):
    client = Client.objects.create(
        name="Entreprise Test",
    )
    intervention = Intervention.objects.create(
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
        Intervention.Status.IN_PROGRESS,
        Intervention.Status.COMPLETED,
        Intervention.Status.CANCELLED,
    ],
)
@pytest.mark.django_db
def test_only_planned_intervention_can_be_started(status):
    client = Client.objects.create(
        name="Entreprise Test",
    )
    intervention = Intervention.objects.create(
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
def test_only_in_progress_intervention_can_be_completed(status):
    client = Client.objects.create(
        name="Entreprise Test",
    )
    intervention = Intervention.objects.create(
        client=client,
        title="Maintenance du poste de travail",
        status=status,
    )

    with pytest.raises(ValidationError):
        intervention.complete()


@pytest.mark.parametrize(
    "initial_status",
    [
        Intervention.Status.COMPLETED,
        Intervention.Status.CANCELLED,
    ],
)
@pytest.mark.django_db
def test_completed_or_cancelled_intervention_cannot_be_cancelled(initial_status):
    client = Client.objects.create(
        name="Entreprise Test",
    )
    intervention = Intervention.objects.create(
        client=client,
        title="Maintenance du poste de travail",
        status=initial_status,
    )

    with pytest.raises(ValidationError):
        intervention.cancel()
