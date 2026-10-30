import uuid

import pytest
from django.urls import reverse

from apps.accounts.models import User
from apps.clients.models import Client


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("role", "expected_status"),
    [
        (User.Role.ADMIN, 200),
        (User.Role.MANAGER, 200),
        (User.Role.TECHNICIAN, 403),
    ],
)
def test_client_detail_access_by_role(
    client,
    django_user_model,
    role,
    expected_status,
):
    user = django_user_model.objects.create_user(
        username=f"user_{role.lower()}",
        password="TestPassword123!",
        role=role,
    )

    client.force_login(user)
    client_obj = Client.objects.create(name="Entreprise Allibi")
    response = client.get(reverse("clients:detail", args=[client_obj.public_id]))

    assert response.status_code == expected_status


@pytest.mark.django_db
def test_client_detail_requires_authentication(client):
    client_obj = Client.objects.create(name="Entreprise Alpha")
    response = client.get(reverse("clients:detail", args=[client_obj.public_id]))

    assert response.status_code == 302
    assert response.url.startswith(reverse("accounts:login"))


@pytest.mark.django_db
def test_client_detail_displays_information(client, django_user_model):
    user = django_user_model.objects.create_user(
        username="manager",
        password="TestPassword123!",
        role=User.Role.MANAGER,
    )

    client.force_login(user)
    client_obj = Client.objects.create(
        name="Entreprise Allibi",
        contact_name="Marie Durand",
        email="contact@allibi.fr",
        phone="0102030405",
        city="Paris",
    )

    response = client.get(reverse("clients:detail", args=[client_obj.public_id]))

    assert response.status_code == 200
    assert response.context["client_obj"] == client_obj
    assert "Entreprise Allibi" in response.content.decode()
    assert "Marie Durand" in response.content.decode()
    assert "contact@allibi.fr" in response.content.decode()
    assert "0102030405" in response.content.decode()
    assert "Paris" in response.content.decode()


@pytest.mark.django_db
def test_client_detail_displays_archived_client(client, django_user_model):
    user = django_user_model.objects.create_user(
        username="manager",
        password="TestPassword123!",
        role=User.Role.MANAGER,
    )

    client.force_login(user)
    client_obj = Client.objects.create(
        name="Ancien Client",
        is_active=False,
    )

    response = client.get(reverse("clients:detail", args=[client_obj.public_id]))

    assert response.status_code == 200
    assert "Client archivé" in response.content.decode()


@pytest.mark.django_db
def test_client_detail_returns_404_for_unknown_client(
    client,
    django_user_model,
):
    user = django_user_model.objects.create_user(
        username="manager",
        password="TestPassword123!",
        role=User.Role.MANAGER,
    )

    client.force_login(user)
    unknown_public_id = uuid.uuid4()
    url = reverse("clients:detail", args=[unknown_public_id])
    response = client.get(url)

    assert response.status_code == 404


@pytest.mark.django_db
def test_client_detail_displays_complete_information(
    client,
    django_user_model,
):
    user = django_user_model.objects.create_user(
        username="manager",
        password="TestPassword123!",
        role=User.Role.MANAGER,
    )
    client.force_login(user)

    client_obj = Client.objects.create(
        name="Entreprise Allibi",
        contact_name="Marie Durand",
        email="contact@allibi.fr",
        phone="0102030405",
        address="10 rue des Lilas",
        postal_code="75001",
        city="Paris",
        notes="Accès par la cour intérieure.",
    )

    response = client.get(reverse("clients:detail", args=[client_obj.public_id]))

    assert response.status_code == 200

    assert "Entreprise Allibi" in response.content.decode()
    assert "Marie Durand" in response.content.decode()
    assert "contact@allibi.fr" in response.content.decode()
    assert "0102030405" in response.content.decode()
    assert "10 rue des Lilas" in response.content.decode()
    assert "75001" in response.content.decode()
    assert "Paris" in response.content.decode()
    assert "Accès par la cour intérieure." in response.content.decode()


@pytest.mark.django_db
def test_client_detail_displays_empty_optional_fields(
    client,
    django_user_model,
):
    user = django_user_model.objects.create_user(
        username="manager",
        password="TestPassword123!",
        role=User.Role.MANAGER,
    )

    client.force_login(user)
    client_obj = Client.objects.create(name="Entreprise Allibi")
    response = client.get(reverse("clients:detail", args=[client_obj.public_id]))

    assert response.status_code == 200
    assert "Non renseigné" in response.content.decode()
    assert "Non renseignée" in response.content.decode()
    assert "Aucune note renseignée." in response.content.decode()


@pytest.mark.django_db
def test_client_detail_displays_accessible_links(
    client,
    django_user_model,
):
    user = django_user_model.objects.create_user(
        username="manager",
        password="TestPassword123!",
        role=User.Role.MANAGER,
    )

    client.force_login(user)
    client_obj = Client.objects.create(
        name="Entreprise Allibi",
        email="contact@allibi.fr",
        phone="0102030405",
    )

    response = client.get(reverse("clients:detail", args=[client_obj.public_id]))

    assert response.status_code == 200
    assert 'href="mailto:contact@allibi.fr"' in response.content.decode()
    assert 'href="tel:0102030405"' in response.content.decode()
    assert f'href="{reverse("clients:list")}"' in response.content.decode()
    assert 'id="client-detail-title"' in response.content.decode()


@pytest.mark.django_db
def test_client_detail_navigation_displays_selected_client(
    client,
    django_user_model,
):
    user = django_user_model.objects.create_user(
        username="manager",
        password="TestPassword123!",
        role=User.Role.MANAGER,
    )

    client.force_login(user)
    client_allibi = Client.objects.create(name="Entreprise Allibi")
    Client.objects.create(name="Entreprise Bon Pain")

    response = client.get(reverse("clients:detail", args=[client_allibi.public_id]))

    assert response.status_code == 200
    assert response.context["client_obj"] == client_allibi
    assert "Entreprise Allibi" in response.content.decode()


@pytest.mark.django_db
def test_client_detail_has_back_link(client, django_user_model):
    user = django_user_model.objects.create_user(
        username="manager",
        password="TestPassword123!",
        role=User.Role.MANAGER,
    )

    client.force_login(user)
    client_obj = Client.objects.create(name="Entreprise Allibi")

    response = client.get(reverse("clients:detail", args=[client_obj.public_id]))

    assert response.status_code == 200
    assert f'href="{reverse("clients:list")}"' in response.content.decode()
    assert "Retour aux clients" in response.content.decode()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "role",
    [
        User.Role.ADMIN,
        User.Role.MANAGER,
    ],
)
def test_client_detail_displays_edit_link(
    client,
    django_user_model,
    role,
):
    user = django_user_model.objects.create_user(
        username=f"user_{role.lower()}",
        password="TestPassword123!",
        role=role,
    )

    client.force_login(user)
    client_obj = Client.objects.create(name="Entreprise Allibi")
    response = client.get(reverse("clients:detail", args=[client_obj.public_id]))

    assert response.status_code == 200
    assert response.context["can_edit_client"] is True

    edit_url = reverse(
        "clients:update",
        args=[client_obj.public_id],
    )

    assert f'href="{edit_url}"' in response.content.decode()
    assert "Modifier le client" in response.content.decode()
