import pytest
from django.urls import reverse

from apps.accounts.models import User
from apps.clients.models import Client
from apps.interventions.models import Intervention


@pytest.fixture
def status_intervention(db, intervention_author):
    customer = Client.objects.create(name="Client statut")

    return Intervention.objects.create(
        client=customer,
        created_by=intervention_author,
        title="Intervention statut",
        status=Intervention.Status.PLANNED,
    )


def status_url(intervention, action):
    return reverse(
        "interventions:status_update",
        args=[intervention.pk, action],
    )


@pytest.mark.django_db
def test_status_update_requires_authentication(client, status_intervention):
    response = client.post(status_url(status_intervention, "start"))

    assert response.status_code == 302

    status_intervention.refresh_from_db()
    assert status_intervention.status == Intervention.Status.PLANNED


@pytest.mark.django_db
def test_status_update_rejects_get(
    client,
    intervention_author,
    status_intervention,
):
    client.force_login(intervention_author)
    response = client.get(status_url(status_intervention, "start"))

    assert response.status_code == 405


@pytest.mark.django_db
def test_manager_can_start_intervention(
    client,
    intervention_author,
    status_intervention,
):
    client.force_login(intervention_author)
    response = client.post(status_url(status_intervention, "start"))

    assert response.status_code == 302
    assert response.url == reverse(
        "interventions:detail",
        args=[status_intervention.pk],
    )

    status_intervention.refresh_from_db()
    assert status_intervention.status == Intervention.Status.IN_PROGRESS


@pytest.mark.django_db
def test_manager_can_cancel_intervention(
    client,
    intervention_author,
    status_intervention,
):
    client.force_login(intervention_author)
    response = client.post(status_url(status_intervention, "cancel"))

    assert response.status_code == 302

    status_intervention.refresh_from_db()
    assert status_intervention.status == Intervention.Status.CANCELLED


@pytest.mark.django_db
def test_direct_completion_endpoint_is_forbidden(
    client,
    intervention_author,
    status_intervention,
):
    status_intervention.status = Intervention.Status.IN_PROGRESS
    status_intervention.save(update_fields=["status"])
    client.force_login(intervention_author)
    response = client.post(
        status_url(status_intervention, "complete"),
        {"report": "Compte rendu valide."},
    )

    assert response.status_code == 403

    status_intervention.refresh_from_db()
    assert status_intervention.status == Intervention.Status.IN_PROGRESS
    assert status_intervention.report == ""


@pytest.mark.django_db
def test_technician_cannot_cancel(
    client,
    django_user_model,
    status_intervention,
):
    technician = django_user_model.objects.create_user(
        username="status-technician",
        role=User.Role.TECHNICIAN,
    )

    status_intervention.technician = technician
    status_intervention.save(update_fields=["technician"])
    client.force_login(technician)
    response = client.post(status_url(status_intervention, "cancel"))

    assert response.status_code == 403

    status_intervention.refresh_from_db()
    assert status_intervention.status == Intervention.Status.PLANNED


@pytest.mark.django_db
def test_unknown_status_action_is_forbidden(
    client,
    intervention_author,
    status_intervention,
):
    client.force_login(intervention_author)
    response = client.post(status_url(status_intervention, "unknown"))

    assert response.status_code == 403

    status_intervention.refresh_from_db()
    assert status_intervention.status == Intervention.Status.PLANNED


@pytest.mark.django_db
def test_completed_intervention_cannot_be_restarted(
    client,
    intervention_author,
    status_intervention,
):
    status_intervention.status = Intervention.Status.COMPLETED
    status_intervention.report = "Intervention terminée."
    status_intervention.save(update_fields=["status", "report"])
    client.force_login(intervention_author)
    response = client.post(status_url(status_intervention, "start"))

    assert response.status_code == 403

    status_intervention.refresh_from_db()
    assert status_intervention.status == Intervention.Status.COMPLETED
