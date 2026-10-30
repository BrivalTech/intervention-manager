import pytest
from django.urls import reverse

from apps.accounts.models import User
from apps.clients.models import Client
from apps.interventions.models import Intervention


def test_intervention_list_requires_authentication(client):
    response = client.get(reverse("interventions:list"))

    assert response.status_code == 302
    assert response.url.startswith(reverse("accounts:login"))


@pytest.mark.django_db
@pytest.mark.parametrize(
    "role",
    [
        User.Role.ADMIN,
        User.Role.MANAGER,
        User.Role.TECHNICIAN,
    ],
)
def test_intervention_list_access_by_role(client, django_user_model, role):
    user = django_user_model.objects.create_user(
        username=f"user-{role.lower()}",
        role=role,
    )

    client.force_login(user)
    response = client.get(reverse("interventions:list"))

    assert response.status_code == 200


@pytest.mark.django_db
def test_manager_can_view_all_interventions(
    client,
    intervention_author,
    django_user_model,
):
    manager = django_user_model.objects.create_user(
        username="manager-list",
        role=User.Role.MANAGER,
    )
    customer = Client.objects.create(name="Client Test")
    Intervention.objects.create(
        created_by=intervention_author,
        client=customer,
        title="Intervention A",
    )
    Intervention.objects.create(
        created_by=intervention_author,
        client=customer,
        title="Intervention B",
    )

    client.force_login(manager)
    response = client.get(reverse("interventions:list"))

    assert response.status_code == 200
    assert len(response.context["interventions"]) == 2


@pytest.mark.django_db
def test_technician_only_sees_assigned_interventions(
    client,
    intervention_author,
    django_user_model,
):
    technician = django_user_model.objects.create_user(
        username="technician-list",
        role=User.Role.TECHNICIAN,
    )
    customer = Client.objects.create(name="Client Test")
    Intervention.objects.create(
        created_by=intervention_author,
        client=customer,
        title="Mon intervention",
        technician=technician,
    )
    Intervention.objects.create(
        created_by=intervention_author,
        client=customer,
        title="Autre intervention",
    )

    client.force_login(technician)
    response = client.get(reverse("interventions:list"))

    assert response.status_code == 200
    assert "Mon intervention" in response.content.decode()
    assert "Autre intervention" not in response.content.decode()


@pytest.mark.django_db
def test_intervention_list_displays_empty_state(client, intervention_author):
    client.force_login(intervention_author)
    response = client.get(reverse("interventions:list"))

    assert response.status_code == 200
    assert "Aucune intervention enregistrée." in response.content.decode()


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("role", "expected"),
    [
        (User.Role.ADMIN, True),
        (User.Role.MANAGER, True),
        (User.Role.TECHNICIAN, False),
    ],
)
def test_create_intervention_link_visibility(
    client,
    django_user_model,
    role,
    expected,
):
    user = django_user_model.objects.create_user(
        username=f"list-create-{role.lower()}",
        role=role,
    )

    client.force_login(user)
    response = client.get(reverse("interventions:list"))

    assert response.status_code == 200

    create_url = reverse("interventions:create")

    if expected:
        assert create_url in response.content.decode()
    else:
        assert create_url not in response.content.decode()
