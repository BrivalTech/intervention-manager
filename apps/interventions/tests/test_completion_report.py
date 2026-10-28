import pytest
from django.core.exceptions import ValidationError

from apps.accounts.models import User
from apps.clients.models import Client
from apps.interventions.models import Intervention
from apps.interventions.services import update_intervention_status


@pytest.fixture
def intervention_in_progress(intervention_author):
    client = Client.objects.create(name="Client compte rendu")

    return Intervention.objects.create(
        client=client,
        created_by=intervention_author,
        title="Maintenance informatique",
        status=Intervention.Status.IN_PROGRESS,
    )


@pytest.mark.django_db
def test_complete_intervention_with_report(intervention_in_progress):
    intervention_in_progress.complete(
        "Maintenance effectuée. Tests de fonctionnement réussis."
    )

    intervention_in_progress.refresh_from_db()

    assert intervention_in_progress.status == Intervention.Status.COMPLETED
    assert (
        intervention_in_progress.report
        == "Maintenance effectuée. Tests de fonctionnement réussis."
    )


@pytest.mark.django_db
@pytest.mark.parametrize("report", ["", "   ", "\n\t", None])
def test_cannot_complete_without_report(intervention_in_progress, report):
    with pytest.raises(ValidationError):
        intervention_in_progress.complete(report)

    intervention_in_progress.refresh_from_db()

    assert intervention_in_progress.status == Intervention.Status.IN_PROGRESS
    assert intervention_in_progress.report == ""


@pytest.mark.django_db
def test_cannot_complete_planned_intervention(intervention_in_progress):
    intervention_in_progress.status = Intervention.Status.PLANNED

    with pytest.raises(ValidationError):
        intervention_in_progress.complete("Travaux effectués")

    assert intervention_in_progress.status == Intervention.Status.PLANNED


@pytest.mark.django_db
def test_completed_intervention_requires_report_in_model_validation(
    intervention_in_progress,
):
    intervention_in_progress.status = Intervention.Status.COMPLETED

    with pytest.raises(ValidationError) as exc_info:
        intervention_in_progress.full_clean()

    assert "report" in exc_info.value.message_dict


@pytest.mark.django_db
def test_service_completes_intervention_with_report(
    intervention_author,
    intervention_in_progress,
):
    update_intervention_status(
        user=intervention_author,
        intervention=intervention_in_progress,
        action="complete",
        report="Intervention terminée avec succès.",
    )

    intervention_in_progress.refresh_from_db()

    assert intervention_in_progress.status == Intervention.Status.COMPLETED
    assert intervention_in_progress.report == "Intervention terminée avec succès."


@pytest.mark.django_db
def test_unassigned_technician_cannot_complete_intervention(
    intervention_in_progress,
):
    technician = User.objects.create_user(
        username="technician_report",
        role=User.Role.TECHNICIAN,
    )

    with pytest.raises(PermissionError):
        update_intervention_status(
            user=technician,
            intervention=intervention_in_progress,
            action="complete",
            report="Intervention terminée.",
        )

    intervention_in_progress.refresh_from_db()

    assert intervention_in_progress.status == Intervention.Status.IN_PROGRESS
    assert intervention_in_progress.report == ""
