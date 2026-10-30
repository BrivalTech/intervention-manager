import pytest
from django.urls import NoReverseMatch, reverse


@pytest.mark.parametrize(
    "route",
    [
        "clients:detail",
        "clients:update",
        "clients:archive",
        "clients:restore",
        "interventions:detail",
        "interventions:edit",
        "interventions:complete",
        "accounts:technician_update",
        "accounts:technician_deactivate",
        "accounts:technician_reactivate",
        "accounts:technician_resend_invitation",
        "accounts:manager_update",
        "accounts:manager_deactivate",
        "accounts:manager_reactivate",
        "accounts:manager_resend_invitation",
    ],
)
def test_public_urls_reject_numeric_identifiers(route):
    with pytest.raises(NoReverseMatch):
        reverse(route, kwargs={"public_id": 123})


def test_intervention_status_url_rejects_numeric_identifier():
    with pytest.raises(NoReverseMatch):
        reverse(
            "interventions:status_update",
            kwargs={"public_id": 123, "action": "start"},
        )
