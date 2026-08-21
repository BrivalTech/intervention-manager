import pytest
from django.core.exceptions import ValidationError

from apps.clients.models import Client


@pytest.mark.django_db
def test_client_can_be_created():
    client = Client.objects.create(name="Entreprise Test")

    assert client.name == "Entreprise Test"
    assert client.is_active


@pytest.mark.django_db
def test_client_name_is_required():
    client = Client(name="")
    with pytest.raises(ValidationError):
        client.full_clean()


@pytest.mark.django_db
def test_client_can_be_archived():
    client = Client.objects.create(name="Entreprise Test")
    client.archive()
    client.refresh_from_db()

    assert not client.is_active


@pytest.mark.django_db
def test_client_can_be_restored():
    client = Client.objects.create(
        name="Entreprise Test",
        is_active=False,
    )
    client.restore()
    client.refresh_from_db()

    assert client.is_active


@pytest.mark.django_db
def test_already_archived_client_can_be_archived_again():
    client = Client.objects.create(
        name="Entreprise Test",
        is_active=False,
    )
    client.archive()
    client.refresh_from_db()

    assert not client.is_active


@pytest.mark.django_db
def test_active_client_can_be_restored_again():
    client = Client.objects.create(
        name="Entreprise Test",
    )
    client.restore()
    client.refresh_from_db()

    assert client.is_active


@pytest.mark.django_db
def test_client_email_must_be_valid():
    client = Client.objects.create(
        name="Entreprise Test",
        email="not-an-email",
    )

    with pytest.raises(ValidationError):
        client.full_clean()


@pytest.mark.django_db
def test_client_accepts_valid_email():
    client = Client.objects.create(
        name="Entreprise Test",
        email="contact@test.com",
    )

    client.full_clean()


@pytest.mark.django_db
def test_client_string_representation():
    client = Client.objects.create(name="Entreprise Test")

    assert str(client) == "Entreprise Test"


@pytest.mark.django_db
def test_active_client_can_receive_intervention():
    client = Client.objects.create(
        name="Entreprise Test",
    )

    assert client.can_receive_intervention


@pytest.mark.django_db
def test_archived_client_cannot_receive_intervention():
    client = Client.objects.create(
        name="Entreprise Test",
        is_active=False,
    )

    assert not client.can_receive_intervention
