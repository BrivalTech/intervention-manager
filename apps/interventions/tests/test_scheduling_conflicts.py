from datetime import datetime
from zoneinfo import ZoneInfo

import pytest
from django.core.exceptions import ValidationError

from apps.accounts.models import User
from apps.clients.models import Client
from apps.interventions.services import (
    assign_technician,
    create_intervention,
)

TZ = ZoneInfo("Europe/Paris")


def at(hour, minute=0):
    return datetime(2026, 11, 10, hour, minute, tzinfo=TZ)


@pytest.fixture
def client_account():
    return Client.objects.create(name="Client planning")


@pytest.fixture
def technician():
    return User.objects.create_user(
        username="technician_planning",
        role=User.Role.TECHNICIAN,
    )


@pytest.fixture
def other_technician():
    return User.objects.create_user(
        username="other_technician_planning",
        role=User.Role.TECHNICIAN,
    )


@pytest.fixture
def existing_intervention(
    client_account,
    technician,
    intervention_author,
):
    return create_intervention(
        client=client_account,
        created_by=intervention_author,
        title="Intervention existante",
        technician=technician,
        starts_at=at(9),
        ends_at=at(11),
    )


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("start", "end"),
    [
        (at(8), at(10)),
        (at(10), at(12)),
        (at(9, 30), at(10, 30)),
        (at(8), at(12)),
        (at(9), at(11)),
    ],
)
def test_overlapping_interventions_are_rejected(
    existing_intervention,
    client_account,
    technician,
    intervention_author,
    start,
    end,
):
    with pytest.raises(ValidationError) as exc_info:
        create_intervention(
            client=client_account,
            created_by=intervention_author,
            title="Intervention en conflit",
            technician=technician,
            starts_at=start,
            ends_at=end,
        )

    assert "technician" in exc_info.value.message_dict


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("start", "end"),
    [
        (at(7), at(9)),
        (at(11), at(13)),
    ],
)
def test_consecutive_interventions_are_allowed(
    existing_intervention,
    client_account,
    technician,
    intervention_author,
    start,
    end,
):
    intervention = create_intervention(
        client=client_account,
        created_by=intervention_author,
        title="Intervention consécutive",
        technician=technician,
        starts_at=start,
        ends_at=end,
    )

    assert intervention.pk is not None


@pytest.mark.django_db
def test_different_technicians_can_have_overlapping_interventions(
    existing_intervention,
    client_account,
    other_technician,
    intervention_author,
):
    intervention = create_intervention(
        client=client_account,
        created_by=intervention_author,
        title="Intervention autre technicien",
        technician=other_technician,
        starts_at=at(10),
        ends_at=at(12),
    )

    assert intervention.pk is not None


@pytest.mark.django_db
def test_cancelled_intervention_does_not_block_schedule(
    existing_intervention,
    client_account,
    technician,
    intervention_author,
):
    existing_intervention.cancel()

    intervention = create_intervention(
        client=client_account,
        created_by=intervention_author,
        title="Nouvelle intervention",
        technician=technician,
        starts_at=at(10),
        ends_at=at(12),
    )

    assert intervention.pk is not None


@pytest.mark.django_db
def test_intervention_does_not_conflict_with_itself(
    existing_intervention,
):
    existing_intervention.full_clean()


@pytest.mark.django_db
def test_unplanned_intervention_is_allowed(
    existing_intervention,
    client_account,
    technician,
    intervention_author,
):
    intervention = create_intervention(
        client=client_account,
        created_by=intervention_author,
        title="Intervention non planifiée",
        technician=technician,
    )

    assert intervention.pk is not None


@pytest.mark.django_db
def test_unassigned_intervention_is_allowed(
    existing_intervention,
    client_account,
    intervention_author,
):
    intervention = create_intervention(
        client=client_account,
        created_by=intervention_author,
        title="Intervention sans technicien",
        starts_at=at(10),
        ends_at=at(12),
    )

    assert intervention.pk is not None


@pytest.mark.django_db
def test_assignment_rejects_conflict_and_preserves_previous_technician(
    existing_intervention,
    client_account,
    technician,
    other_technician,
    intervention_author,
):
    intervention = create_intervention(
        client=client_account,
        created_by=intervention_author,
        title="Intervention à réaffecter",
        technician=other_technician,
        starts_at=at(10),
        ends_at=at(12),
    )

    with pytest.raises(ValidationError):
        assign_technician(
            user=intervention_author,
            intervention=intervention,
            technician=technician,
        )

    assert intervention.technician == other_technician

    intervention.refresh_from_db()
    assert intervention.technician == other_technician


@pytest.mark.django_db
def test_completed_intervention_blocks_schedule(
    existing_intervention,
    client_account,
    technician,
    intervention_author,
):
    existing_intervention.start()
    existing_intervention.complete("Intervention terminée et vérifiée.")

    with pytest.raises(ValidationError) as exc_info:
        create_intervention(
            client=client_account,
            created_by=intervention_author,
            title="Intervention en conflit",
            technician=technician,
            starts_at=at(10),
            ends_at=at(12),
        )

    assert "technician" in exc_info.value.message_dict
