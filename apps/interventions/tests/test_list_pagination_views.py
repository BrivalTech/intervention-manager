import pytest
from django.urls import reverse

from apps.clients.models import Client
from apps.interventions.models import Intervention


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
