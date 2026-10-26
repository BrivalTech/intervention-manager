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
def test_intervention_list_search_by_title(client, intervention_author):
    customer = Client.objects.create(name="Client Test")
    Intervention.objects.create(
        created_by=intervention_author,
        client=customer,
        title="Maintenance informatique",
    )
    Intervention.objects.create(
        created_by=intervention_author,
        client=customer,
        title="Installation réseau",
    )

    client.force_login(intervention_author)
    response = client.get(
        reverse("interventions:list"),
        {"q": "maintenance"},
    )

    assert response.status_code == 200
    assert len(response.context["interventions"]) == 1
    assert response.context["interventions"][0].title == "Maintenance informatique"


@pytest.mark.django_db
def test_intervention_list_filter_by_status(client, intervention_author):
    customer = Client.objects.create(name="Client Test")
    Intervention.objects.create(
        created_by=intervention_author,
        client=customer,
        title="Intervention planifiée",
    )
    Intervention.objects.create(
        created_by=intervention_author,
        client=customer,
        title="Intervention en cours",
        status=Intervention.Status.IN_PROGRESS,
    )

    client.force_login(intervention_author)
    response = client.get(
        reverse("interventions:list"),
        {"status": Intervention.Status.IN_PROGRESS},
    )

    assert response.status_code == 200
    assert len(response.context["interventions"]) == 1
    assert response.context["interventions"][0].title == "Intervention en cours"


@pytest.mark.django_db
def test_intervention_list_combines_search_and_status(
    client,
    intervention_author,
):
    customer = Client.objects.create(name="Client Test")
    Intervention.objects.create(
        created_by=intervention_author,
        client=customer,
        title="Maintenance planifiée",
    )
    Intervention.objects.create(
        created_by=intervention_author,
        client=customer,
        title="Maintenance en cours",
        status=Intervention.Status.IN_PROGRESS,
    )
    Intervention.objects.create(
        created_by=intervention_author,
        client=customer,
        title="Installation en cours",
        status=Intervention.Status.IN_PROGRESS,
    )

    client.force_login(intervention_author)
    response = client.get(
        reverse("interventions:list"),
        {
            "q": "maintenance",
            "status": Intervention.Status.IN_PROGRESS,
        },
    )

    assert response.status_code == 200
    assert len(response.context["interventions"]) == 1
    assert response.context["interventions"][0].title == "Maintenance en cours"


@pytest.mark.django_db
def test_intervention_list_invalid_status_is_ignored(
    client,
    intervention_author,
):
    customer = Client.objects.create(name="Client Test")
    Intervention.objects.create(
        created_by=intervention_author,
        client=customer,
        title="Intervention test",
    )

    client.force_login(intervention_author)
    response = client.get(
        reverse("interventions:list"),
        {"status": "INVALID"},
    )

    assert response.status_code == 200
    assert len(response.context["interventions"]) == 1
    assert response.context["status_filter"] == ""


@pytest.mark.django_db
def test_intervention_list_no_matching_results(client, intervention_author):
    client.force_login(intervention_author)
    response = client.get(
        reverse("interventions:list"),
        {"q": "introuvable"},
    )

    assert response.status_code == 200
    assert b"Aucune intervention ne correspond" in response.content


@pytest.mark.django_db
def test_intervention_list_is_paginated(client, intervention_author):
    customer = Client.objects.create(name="Client pagination")

    for index in range(15):
        Intervention.objects.create(
            created_by=intervention_author,
            client=customer,
            title=f"Intervention {index}",
        )

    client.force_login(intervention_author)
    response = client.get(reverse("interventions:list"))

    assert response.status_code == 200
    assert len(response.context["interventions"]) == 10
    assert response.context["page_obj"].number == 1
    assert response.context["page_obj"].paginator.num_pages == 2

    response = client.get(
        reverse("interventions:list"),
        {"page": 2},
    )

    assert response.status_code == 200
    assert len(response.context["interventions"]) == 5
    assert response.context["page_obj"].number == 2


@pytest.mark.django_db
def test_intervention_list_invalid_page(client, intervention_author):
    client.force_login(intervention_author)
    response = client.get(
        reverse("interventions:list"),
        {"page": "invalid"},
    )

    assert response.status_code == 200
    assert response.context["page_obj"].number == 1


@pytest.mark.django_db
def test_intervention_pagination_preserves_filters(client, intervention_author):
    customer = Client.objects.create(name="Client pagination")

    for index in range(12):
        Intervention.objects.create(
            created_by=intervention_author,
            client=customer,
            title=f"Maintenance {index}",
            status=Intervention.Status.PLANNED,
        )

    Intervention.objects.create(
        created_by=intervention_author,
        client=customer,
        title="Installation réseau",
    )

    client.force_login(intervention_author)
    response = client.get(
        reverse("interventions:list"),
        {
            "q": "Maintenance",
            "status": Intervention.Status.PLANNED,
            "page": 2,
        },
    )

    assert response.status_code == 200
    assert response.context["page_obj"].number == 2
    assert len(response.context["interventions"]) == 2
    assert response.context["search_query"] == "Maintenance"
    assert response.context["status_filter"] == Intervention.Status.PLANNED
    assert b"q=Maintenance" in response.content
    assert b"status=PLANNED" in response.content
