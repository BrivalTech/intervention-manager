import pytest
from django.core.exceptions import ValidationError

from apps.accounts.models import User
from apps.clients.models import Client
from apps.interventions.services import create_intervention


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
