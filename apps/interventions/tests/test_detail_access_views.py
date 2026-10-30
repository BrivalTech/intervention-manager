import uuid

import pytest
from django.urls import reverse

from apps.accounts.models import User


@pytest.mark.django_db
def test_intervention_detail_requires_authentication(client, intervention):
    response = client.get(
        reverse("interventions:detail", args=[intervention.public_id])
    )

    assert response.status_code == 302
    assert response.url.startswith(reverse("accounts:login"))


@pytest.mark.django_db
@pytest.mark.parametrize(
    "role",
    [User.Role.ADMIN, User.Role.MANAGER],
)
def test_admin_and_manager_can_view_intervention(
    client,
    django_user_model,
    intervention,
    role,
):
    user = django_user_model.objects.create_user(
        username=f"detail-{role.lower()}",
        role=role,
    )

    client.force_login(user)
    response = client.get(
        reverse("interventions:detail", args=[intervention.public_id])
    )

    assert response.status_code == 200
    assert response.context["intervention"] == intervention


@pytest.mark.django_db
def test_assigned_technician_can_view_intervention(
    client,
    django_user_model,
    intervention,
):
    technician = django_user_model.objects.create_user(
        username="assigned-detail",
        role=User.Role.TECHNICIAN,
    )

    intervention.assign_technician(technician)
    client.force_login(technician)
    response = client.get(
        reverse("interventions:detail", args=[intervention.public_id])
    )

    assert response.status_code == 200


@pytest.mark.django_db
def test_unassigned_technician_cannot_view_intervention(
    client,
    django_user_model,
    intervention,
):
    technician = django_user_model.objects.create_user(
        username="unassigned-detail",
        role=User.Role.TECHNICIAN,
    )

    client.force_login(technician)
    response = client.get(
        reverse("interventions:detail", args=[intervention.public_id])
    )

    assert response.status_code == 404


@pytest.mark.django_db
def test_unknown_intervention_returns_404(client, intervention_author):
    client.force_login(intervention_author)
    response = client.get(
        reverse(
            "interventions:detail",
            args=[uuid.uuid4()],
        )
    )

    assert response.status_code == 404
