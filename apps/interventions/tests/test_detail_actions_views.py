import pytest
from django.urls import reverse

from apps.accounts.models import User
from apps.interventions.models import Intervention


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("role", "expected"),
    [
        (User.Role.ADMIN, True),
        (User.Role.MANAGER, True),
        (User.Role.TECHNICIAN, False),
    ],
)
def test_edit_link_visibility_by_role(
    client,
    django_user_model,
    intervention,
    role,
    expected,
):
    user = django_user_model.objects.create_user(
        username=f"detail-edit-{role.lower()}",
        role=role,
    )

    if role == User.Role.TECHNICIAN:
        intervention.assign_technician(user)

    client.force_login(user)
    response = client.get(
        reverse("interventions:detail", args=[intervention.public_id])
    )

    assert response.status_code == 200

    edit_url = reverse(
        "interventions:edit",
        args=[intervention.public_id],
    )

    if expected:
        assert edit_url in response.content.decode()
    else:
        assert edit_url not in response.content.decode()


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("status", "expected"),
    [
        (Intervention.Status.TO_PLAN, True),
        (Intervention.Status.PLANNED, True),
        (Intervention.Status.IN_PROGRESS, False),
        (Intervention.Status.COMPLETED, False),
        (Intervention.Status.CANCELLED, False),
    ],
)
def test_edit_link_visibility_by_status(
    client,
    intervention_author,
    intervention,
    status,
    expected,
):
    intervention.status = status
    intervention.save(update_fields=["status"])
    client.force_login(intervention_author)
    response = client.get(
        reverse("interventions:detail", args=[intervention.public_id])
    )

    assert response.status_code == 200

    edit_url = reverse(
        "interventions:edit",
        args=[intervention.public_id],
    )

    if expected:
        assert edit_url in response.content.decode()
    else:
        assert edit_url not in response.content.decode()


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("status", "start_visible", "cancel_visible"),
    [
        (Intervention.Status.TO_PLAN, False, True),
        (Intervention.Status.PLANNED, True, True),
        (Intervention.Status.IN_PROGRESS, False, True),
        (Intervention.Status.COMPLETED, False, False),
        (Intervention.Status.CANCELLED, False, False),
    ],
)
def test_status_actions_visibility_by_status(
    client,
    intervention_author,
    intervention,
    status,
    start_visible,
    cancel_visible,
):
    intervention.status = status
    intervention.save(update_fields=["status"])
    client.force_login(intervention_author)
    response = client.get(
        reverse("interventions:detail", args=[intervention.public_id])
    )

    assert response.status_code == 200

    start_url = reverse(
        "interventions:status_update",
        args=[intervention.public_id, "start"],
    )
    cancel_url = reverse(
        "interventions:status_update",
        args=[intervention.public_id, "cancel"],
    )

    content = response.content.decode()

    assert (f'action="{start_url}"' in content) is start_visible
    assert (f'action="{cancel_url}"' in content) is cancel_visible


@pytest.mark.django_db
def test_assigned_technician_sees_start_but_not_cancel(
    client,
    django_user_model,
    intervention,
):
    technician = django_user_model.objects.create_user(
        username="technician-actions",
        role=User.Role.TECHNICIAN,
    )

    intervention.technician = technician
    intervention.status = Intervention.Status.PLANNED
    intervention.save(update_fields=["technician", "status"])
    client.force_login(technician)
    response = client.get(
        reverse("interventions:detail", args=[intervention.public_id])
    )

    assert response.status_code == 200

    start_url = reverse(
        "interventions:status_update",
        args=[intervention.public_id, "start"],
    )
    cancel_url = reverse(
        "interventions:status_update",
        args=[intervention.public_id, "cancel"],
    )

    content = response.content.decode()

    assert f'action="{start_url}"' in content
    assert f'action="{cancel_url}"' not in content
