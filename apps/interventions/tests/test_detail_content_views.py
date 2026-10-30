from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone

from apps.interventions.models import Intervention


@pytest.mark.django_db
def test_intervention_detail_displays_information(
    client,
    intervention_author,
    intervention,
):
    client.force_login(intervention_author)
    response = client.get(
        reverse("interventions:detail", args=[intervention.public_id])
    )

    assert response.status_code == 200
    assert "Intervention de test" in response.content.decode()
    assert "Client test" in response.content.decode()
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
    response = client.get(
        reverse("interventions:detail", args=[intervention.public_id])
    )

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
    response = client.get(
        reverse("interventions:detail", args=[intervention.public_id])
    )

    assert response.status_code == 200
    assert b"Adresse non renseign" in response.content
    assert b"Aucune description renseign" in response.content


@pytest.mark.django_db
def test_completed_intervention_displays_report(
    client,
    intervention_author,
    intervention,
):
    start = timezone.now() + timedelta(days=1)
    intervention.starts_at = start
    intervention.ends_at = start + timedelta(hours=2)
    intervention.status = Intervention.Status.PLANNED
    intervention.full_clean()
    intervention.save(update_fields=["starts_at", "ends_at", "status", "updated_at"])
    intervention.start()
    intervention.complete("Maintenance effectuée.\nTests de fonctionnement réussis.")

    client.force_login(intervention_author)
    response = client.get(
        reverse("interventions:detail", args=[intervention.public_id])
    )

    assert response.status_code == 200
    assert "Compte rendu d'intervention" in response.content.decode()
    assert "Maintenance effectuée." in response.content.decode()
    assert "Tests de fonctionnement réussis." in response.content.decode()


@pytest.mark.django_db
def test_planned_intervention_does_not_display_report(
    client,
    intervention_author,
    intervention,
):
    client.force_login(intervention_author)

    response = client.get(
        reverse("interventions:detail", args=[intervention.public_id])
    )

    assert response.status_code == 200
    assert "Compte rendu d'intervention" not in response.content.decode()
