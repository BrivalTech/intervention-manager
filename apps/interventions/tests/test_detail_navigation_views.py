import pytest
from django.urls import reverse

from apps.interventions.models import Intervention


@pytest.mark.django_db
def test_intervention_list_links_to_detail(
    client,
    intervention_author,
    intervention,
):
    client.force_login(intervention_author)
    response = client.get(reverse("interventions:list"))
    detail_url = reverse("interventions:detail", args=[intervention.public_id])

    assert response.status_code == 200
    assert detail_url in response.content.decode()


@pytest.mark.django_db
def test_intervention_detail_preserves_list_filters(
    client,
    intervention_author,
    intervention,
):
    client.force_login(intervention_author)
    response = client.get(
        reverse("interventions:detail", args=[intervention.public_id]),
        {
            "q": "maintenance serveur",
            "status": Intervention.Status.TO_PLAN,
            "page": "2",
        },
    )

    assert response.status_code == 200

    expected_query = "q=maintenance+serveur&amp;status=TO_PLAN&amp;page=2"

    assert expected_query in response.content.decode()
    assert reverse("interventions:list") in response.content.decode()


@pytest.mark.django_db
def test_intervention_detail_has_return_link_without_filters(
    client,
    intervention_author,
    intervention,
):
    client.force_login(intervention_author)
    response = client.get(
        reverse("interventions:detail", args=[intervention.public_id])
    )

    assert response.status_code == 200

    expected_url = reverse("interventions:list")
    assert f'href="{expected_url}"' in response.content.decode()


@pytest.mark.django_db
def test_intervention_list_preserves_filters_in_detail_link(
    client,
    intervention_author,
    intervention,
):
    client.force_login(intervention_author)
    response = client.get(
        reverse("interventions:list"),
        {
            "q": "Intervention",
            "status": Intervention.Status.TO_PLAN,
        },
    )

    assert response.status_code == 200

    expected_url = reverse(
        "interventions:detail",
        args=[intervention.public_id],
    )
    assert (
        f"{expected_url}?q=Intervention&amp;status=TO_PLAN" in response.content.decode()
    )
