import pytest
from django.urls import reverse

from apps.accounts.models import User
from apps.clients.models import Client
from apps.interventions.models import Intervention


@pytest.fixture
def in_progress_intervention(db, intervention_author):
    customer = Client.objects.create(name="Client clôture")

    return Intervention.objects.create(
        client=customer,
        created_by=intervention_author,
        title="Intervention à terminer",
        status=Intervention.Status.IN_PROGRESS,
    )


@pytest.mark.django_db
def test_completion_form_is_accessible(
    client,
    intervention_author,
    in_progress_intervention,
):
    client.force_login(intervention_author)
    response = client.get(
        reverse(
            "interventions:complete",
            args=[in_progress_intervention.pk],
        )
    )

    assert response.status_code == 200
    assert "form" in response.context


@pytest.mark.django_db
def test_completion_requires_report(
    client,
    intervention_author,
    in_progress_intervention,
):
    client.force_login(intervention_author)
    response = client.post(
        reverse(
            "interventions:complete",
            args=[in_progress_intervention.pk],
        ),
        {"report": "   "},
    )

    assert response.status_code == 200
    assert "report" in response.context["form"].errors

    in_progress_intervention.refresh_from_db()
    assert in_progress_intervention.status == Intervention.Status.IN_PROGRESS


@pytest.mark.django_db
def test_completion_with_report(
    client,
    intervention_author,
    in_progress_intervention,
):
    client.force_login(intervention_author)
    response = client.post(
        reverse(
            "interventions:complete",
            args=[in_progress_intervention.pk],
        ),
        {"report": "Intervention réalisée et contrôlée."},
    )

    assert response.status_code == 302

    in_progress_intervention.refresh_from_db()

    assert in_progress_intervention.status == Intervention.Status.COMPLETED
    assert in_progress_intervention.report == "Intervention réalisée et contrôlée."


@pytest.mark.django_db
def test_completed_intervention_cannot_be_completed_again(
    client,
    intervention_author,
    in_progress_intervention,
):
    in_progress_intervention.status = Intervention.Status.COMPLETED
    in_progress_intervention.report = "Compte rendu initial"
    in_progress_intervention.save(update_fields=["status", "report"])
    client.force_login(intervention_author)
    response = client.get(
        reverse(
            "interventions:complete",
            args=[in_progress_intervention.pk],
        )
    )

    assert response.status_code == 403


@pytest.mark.django_db
def test_assigned_technician_can_complete_intervention(
    client,
    django_user_model,
    in_progress_intervention,
):
    technician = django_user_model.objects.create_user(
        username="assigned-completion-tech",
        role=User.Role.TECHNICIAN,
    )

    in_progress_intervention.technician = technician
    in_progress_intervention.save(update_fields=["technician"])
    client.force_login(technician)
    response = client.post(
        reverse(
            "interventions:complete",
            args=[in_progress_intervention.pk],
        ),
        {"report": "Travaux effectués et vérifiés."},
    )

    assert response.status_code == 302

    in_progress_intervention.refresh_from_db()
    assert in_progress_intervention.status == Intervention.Status.COMPLETED


@pytest.mark.django_db
def test_unassigned_technician_cannot_complete_intervention(
    client,
    django_user_model,
    in_progress_intervention,
):
    technician = django_user_model.objects.create_user(
        username="unassigned-completion-tech",
        role=User.Role.TECHNICIAN,
    )

    client.force_login(technician)
    response = client.post(
        reverse(
            "interventions:complete",
            args=[in_progress_intervention.pk],
        ),
        {"report": "Tentative non autorisée."},
    )

    assert response.status_code == 403

    in_progress_intervention.refresh_from_db()
    assert in_progress_intervention.status == Intervention.Status.IN_PROGRESS


@pytest.mark.django_db
def test_anonymous_user_cannot_access_completion(
    client,
    in_progress_intervention,
):
    response = client.get(
        reverse(
            "interventions:complete",
            args=[in_progress_intervention.pk],
        )
    )

    assert response.status_code == 302
