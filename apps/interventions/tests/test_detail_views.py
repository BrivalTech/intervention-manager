import pytest
from django.urls import reverse

from apps.accounts.models import User
from apps.clients.models import Client
from apps.interventions.models import Intervention


@pytest.fixture
def intervention(db, intervention_author):
    customer = Client.objects.create(name="Client détail")

    return Intervention.objects.create(
        created_by=intervention_author,
        client=customer,
        title="Maintenance serveur",
    )


@pytest.mark.django_db
def test_intervention_detail_requires_authentication(client, intervention):
    response = client.get(reverse("interventions:detail", args=[intervention.pk]))

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
    response = client.get(reverse("interventions:detail", args=[intervention.pk]))

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
    response = client.get(reverse("interventions:detail", args=[intervention.pk]))

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
    response = client.get(reverse("interventions:detail", args=[intervention.pk]))

    assert response.status_code == 404


@pytest.mark.django_db
def test_unknown_intervention_returns_404(client, intervention_author):
    client.force_login(intervention_author)
    response = client.get(reverse("interventions:detail", args=[999999]))

    assert response.status_code == 404


@pytest.mark.django_db
def test_intervention_detail_displays_information(
    client,
    intervention_author,
    intervention,
):
    client.force_login(intervention_author)
    response = client.get(reverse("interventions:detail", args=[intervention.pk]))

    assert response.status_code == 200
    assert "Maintenance serveur" in response.content.decode()
    assert "Client détail" in response.content.decode()
    assert "Intervention non planifiée." in response.content.decode()


@pytest.mark.django_db
def test_intervention_detail_displays_additional_information(
    client,
    intervention_author,
    intervention,
):
    intervention.description = "Vérification du serveur\nRedémarrage effectué"
    intervention.address = "12 rue des Lilas"
    intervention.postal_code = "75008"
    intervention.city = "Paris"
    intervention.save(
        update_fields=[
            "description",
            "address",
            "postal_code",
            "city",
        ]
    )

    client.force_login(intervention_author)
    response = client.get(reverse("interventions:detail", args=[intervention.pk]))

    assert response.status_code == 200
    assert "12 rue des Lilas" in response.content.decode()
    assert "75008" in response.content.decode()
    assert "Paris" in response.content.decode()
    assert "Vérification du serveur" in response.content.decode()
    assert "Redémarrage effectué" in response.content.decode()
    assert "Créée par" in response.content.decode()
    assert "Dernière modification" in response.content.decode()


@pytest.mark.django_db
def test_intervention_detail_displays_missing_information(
    client,
    intervention_author,
    intervention,
):
    client.force_login(intervention_author)
    response = client.get(reverse("interventions:detail", args=[intervention.pk]))

    assert response.status_code == 200
    assert b"Adresse non renseign" in response.content
    assert b"Aucune description renseign" in response.content


@pytest.mark.django_db
def test_completed_intervention_displays_report(
    client,
    intervention_author,
    intervention,
):
    intervention.start()
    intervention.complete("Maintenance effectuée.\nTests de fonctionnement réussis.")

    client.force_login(intervention_author)
    response = client.get(reverse("interventions:detail", args=[intervention.pk]))

    assert response.status_code == 200

    content = response.content.decode()

    assert "Compte rendu d'intervention" in content
    assert "Maintenance effectuée." in content
    assert "Tests de fonctionnement réussis." in content


@pytest.mark.django_db
def test_planned_intervention_does_not_display_report(
    client,
    intervention_author,
    intervention,
):
    client.force_login(intervention_author)

    response = client.get(reverse("interventions:detail", args=[intervention.pk]))

    assert response.status_code == 200
    assert "Compte rendu d'intervention" not in response.content.decode()


@pytest.mark.django_db
def test_intervention_list_links_to_detail(
    client,
    intervention_author,
    intervention,
):
    client.force_login(intervention_author)
    response = client.get(reverse("interventions:list"))
    detail_url = reverse("interventions:detail", args=[intervention.pk])

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
        reverse("interventions:detail", args=[intervention.pk]),
        {
            "q": "maintenance serveur",
            "status": Intervention.Status.PLANNED,
            "page": "2",
        },
    )

    assert response.status_code == 200

    expected_query = "q=maintenance+serveur&amp;status=PLANNED&amp;page=2"

    assert expected_query in response.content.decode()
    assert reverse("interventions:list") in response.content.decode()


@pytest.mark.django_db
def test_intervention_detail_has_return_link_without_filters(
    client,
    intervention_author,
    intervention,
):
    client.force_login(intervention_author)
    response = client.get(reverse("interventions:detail", args=[intervention.pk]))

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
            "q": "Maintenance",
            "status": Intervention.Status.PLANNED,
        },
    )

    assert response.status_code == 200

    expected_url = reverse(
        "interventions:detail",
        args=[intervention.pk],
    )
    assert (
        f"{expected_url}?q=Maintenance&amp;status=PLANNED" in response.content.decode()
    )
