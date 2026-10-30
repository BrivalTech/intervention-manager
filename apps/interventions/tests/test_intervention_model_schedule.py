from datetime import datetime
from zoneinfo import ZoneInfo

import pytest
from django.core.exceptions import ValidationError

from apps.clients.models import Client
from apps.interventions.models import Intervention


@pytest.mark.parametrize(
    ("starts_at", "ends_at", "is_valid"),
    [
        (None, None, True),
        (
            datetime(2026, 11, 10, 9, tzinfo=ZoneInfo("Europe/Paris")),
            datetime(2026, 11, 10, 11, tzinfo=ZoneInfo("Europe/Paris")),
            True,
        ),
        (
            datetime(2026, 11, 10, 9, tzinfo=ZoneInfo("Europe/Paris")),
            None,
            False,
        ),
        (
            None,
            datetime(2026, 11, 10, 11, tzinfo=ZoneInfo("Europe/Paris")),
            False,
        ),
        (
            datetime(2026, 11, 10, 9, tzinfo=ZoneInfo("Europe/Paris")),
            datetime(2026, 11, 10, 9, tzinfo=ZoneInfo("Europe/Paris")),
            False,
        ),
        (
            datetime(2026, 11, 10, 11, tzinfo=ZoneInfo("Europe/Paris")),
            datetime(2026, 11, 10, 9, tzinfo=ZoneInfo("Europe/Paris")),
            False,
        ),
    ],
)
@pytest.mark.django_db
def test_intervention_schedule_validation(
    starts_at,
    ends_at,
    is_valid,
    intervention_author,
):
    client = Client.objects.create(
        name="Entreprise Test",
    )

    intervention = Intervention(
        created_by=intervention_author,
        client=client,
        title="Maintenance du poste de travail",
        starts_at=starts_at,
        ends_at=ends_at,
    )

    if is_valid:
        intervention.full_clean()
    else:
        with pytest.raises(ValidationError) as exc_info:
            intervention.full_clean()

        assert "ends_at" in exc_info.value.message_dict
