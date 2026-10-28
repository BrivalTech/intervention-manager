import pytest
from django.core.exceptions import ValidationError
from django.urls import reverse

from apps.accounts.models import User
from apps.clients.models import Client
from apps.interventions.models import Intervention


@pytest.fixture
def editable_intervention(db, intervention_author):
    customer = Client.objects.create(name="Client modification")

    return Intervention.objects.create(
        client=customer,
        created_by=intervention_author,
        title="Intervention initiale",
    )


@pytest.mark.django_db
def test_edit_requires_authentication(client, editable_intervention):
    response = client.get(
        reverse("interventions:edit", args=[editable_intervention.pk])
    )

    assert response.status_code == 302


@pytest.mark.django_db
@pytest.mark.parametrize(
    "role",
    [User.Role.ADMIN, User.Role.MANAGER],
)
def test_authorized_user_can_access_edit_form(
    client,
    django_user_model,
    editable_intervention,
    role,
):
    user = django_user_model.objects.create_user(
        username=f"edit-view-{role.lower()}",
        role=role,
    )

    client.force_login(user)
    response = client.get(
        reverse("interventions:edit", args=[editable_intervention.pk])
    )

    assert response.status_code == 200
    assert response.context["form"].instance == editable_intervention
    assert response.context["is_edit"] is True


@pytest.mark.django_db
def test_technician_cannot_edit_intervention(
    client,
    django_user_model,
    editable_intervention,
):
    technician = django_user_model.objects.create_user(
        username="technician-edit-view",
        role=User.Role.TECHNICIAN,
    )

    client.force_login(technician)
    response = client.get(
        reverse("interventions:edit", args=[editable_intervention.pk])
    )

    assert response.status_code == 403


@pytest.mark.django_db
def test_authorized_user_can_update_intervention(
    client,
    intervention_author,
    editable_intervention,
):
    client.force_login(intervention_author)
    response = client.post(
        reverse("interventions:edit", args=[editable_intervention.pk]),
        {
            "client": editable_intervention.client_id,
            "title": "Intervention modifiée",
            "description": "Nouvelle description",
        },
    )

    assert response.status_code == 302
    assert response.url == reverse(
        "interventions:detail",
        args=[editable_intervention.pk],
    )

    editable_intervention.refresh_from_db()

    assert editable_intervention.title == "Intervention modifiée"
    assert editable_intervention.description == "Nouvelle description"
    assert editable_intervention.status == Intervention.Status.TO_PLAN


@pytest.mark.django_db
def test_invalid_edit_does_not_change_intervention(
    client,
    intervention_author,
    editable_intervention,
):
    client.force_login(intervention_author)
    response = client.post(
        reverse("interventions:edit", args=[editable_intervention.pk]),
        {
            "client": editable_intervention.client_id,
            "title": "",
        },
    )

    assert response.status_code == 200
    assert "title" in response.context["form"].errors

    editable_intervention.refresh_from_db()
    assert editable_intervention.title == "Intervention initiale"


@pytest.mark.django_db
def test_unknown_intervention_edit_returns_404(client, intervention_author):
    client.force_login(intervention_author)
    response = client.get(reverse("interventions:edit", args=[999999]))

    assert response.status_code == 404


@pytest.mark.django_db
def test_intervention_remains_editable_when_client_archiving_is_refused(
    client,
    intervention_author,
    editable_intervention,
):
    customer = editable_intervention.client

    with pytest.raises(
        ValidationError,
        match="Impossible d'archiver ce client",
    ):
        customer.archive()

    customer.refresh_from_db()
    assert customer.is_active

    client.force_login(intervention_author)
    response = client.get(
        reverse(
            "interventions:edit",
            args=[editable_intervention.pk],
        )
    )

    assert response.status_code == 200
    assert response.context["form"].instance == editable_intervention
    assert customer in response.context["form"].fields["client"].queryset
