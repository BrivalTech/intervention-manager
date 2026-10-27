import pytest
from django.urls import reverse

from apps.accounts.models import User
from apps.clients.models import Client
from apps.interventions.models import Intervention


@pytest.fixture
def creation_data(db):
    customer = Client.objects.create(name="Client création")
    return {
        "client": customer.pk,
        "title": "Maintenance réseau",
        "description": "Vérification des équipements",
    }


@pytest.mark.django_db
def test_create_requires_authentication(client):
    response = client.get(reverse("interventions:create"))

    assert response.status_code == 302


@pytest.mark.django_db
@pytest.mark.parametrize(
    "role",
    [User.Role.ADMIN, User.Role.MANAGER],
)
def test_authorized_user_can_access_creation_form(
    client,
    django_user_model,
    role,
):
    user = django_user_model.objects.create_user(
        username=f"creator-{role.lower()}",
        role=role,
    )

    client.force_login(user)
    response = client.get(reverse("interventions:create"))

    assert response.status_code == 200
    assert "form" in response.context


@pytest.mark.django_db
def test_technician_cannot_access_creation_form(client, django_user_model):
    technician = django_user_model.objects.create_user(
        username="technician-create",
        role=User.Role.TECHNICIAN,
    )

    client.force_login(technician)
    response = client.get(reverse("interventions:create"))

    assert response.status_code == 403


@pytest.mark.django_db
def test_authorized_user_can_create_intervention(
    client,
    intervention_author,
    creation_data,
):
    client.force_login(intervention_author)
    response = client.post(reverse("interventions:create"), creation_data)
    intervention = Intervention.objects.get(title="Maintenance réseau")

    assert response.status_code == 302
    assert response.url == reverse(
        "interventions:detail",
        args=[intervention.pk],
    )
    assert intervention.created_by == intervention_author
    assert intervention.status == Intervention.Status.TO_PLAN


@pytest.mark.django_db
def test_invalid_creation_does_not_save_intervention(
    client,
    intervention_author,
    creation_data,
):
    client.force_login(intervention_author)
    creation_data["title"] = ""
    response = client.post(reverse("interventions:create"), creation_data)

    assert response.status_code == 200
    assert "title" in response.context["form"].errors
    assert not Intervention.objects.filter(
        client_id=creation_data["client"],
    ).exists()


@pytest.mark.django_db
def test_technician_cannot_submit_creation_form(
    client,
    django_user_model,
    creation_data,
):
    technician = django_user_model.objects.create_user(
        username="technician-create-post",
        role=User.Role.TECHNICIAN,
    )

    client.force_login(technician)
    response = client.post(reverse("interventions:create"), creation_data)

    assert response.status_code == 403
    assert Intervention.objects.count() == 0
