import pytest
from django.urls import reverse

from apps.clients.models import Client
from apps.interventions.models import Intervention


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
