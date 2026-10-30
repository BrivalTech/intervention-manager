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
def test_client_update_access_by_role(
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
    client_obj = Client.objects.create(name="Entreprise Allibi", is_active=True)
    response = client.get(reverse("clients:update", args=[client_obj.public_id]))

    assert response.status_code == expected_status


@pytest.mark.django_db
def test_client_update_requires_authentication(client):
    client_obj = Client.objects.create(
        name="Entreprise Allibi",
        is_active=True,
    )
    response = client.get(reverse("clients:update", args=[client_obj.public_id]))

    assert response.status_code == 302
    assert response.url.startswith(reverse("accounts:login"))


@pytest.mark.django_db
def test_client_update_form_is_prefilled(
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
        city="Paris",
        is_active=True,
    )

    response = client.get(reverse("clients:update", args=[client_obj.public_id]))
    assert response.status_code == 200

    form = response.context["form"]

    assert form.instance == client_obj
    assert form["name"].value() == "Entreprise Allibi"
    assert form["email"].value() == "contact@allibi.fr"
    assert form["city"].value() == "Paris"


@pytest.mark.django_db
def test_client_update_success(client, django_user_model):
    user = django_user_model.objects.create_user(
        username="manager",
        password="TestPassword123!",
        role=User.Role.MANAGER,
    )

    client.force_login(user)
    client_obj = Client.objects.create(
        name="Entreprise Allibi",
        city="Paris",
        is_active=True,
    )

    response = client.post(
        reverse("clients:update", args=[client_obj.public_id]),
        {
            "name": "Entreprise Allibi Modifiée",
            "city": "Lyon",
        },
    )

    assert response.status_code == 302
    assert response.url == reverse(
        "clients:detail",
        args=[client_obj.public_id],
    )

    client_obj.refresh_from_db()

    assert client_obj.name == "Entreprise Allibi Modifiée"
    assert client_obj.city == "Lyon"
    assert Client.objects.count() == 1


@pytest.mark.django_db
def test_client_update_invalid_data(client, django_user_model):
    user = django_user_model.objects.create_user(
        username="manager",
        password="TestPassword123!",
        role=User.Role.MANAGER,
    )

    client.force_login(user)
    client_obj = Client.objects.create(
        name="Entreprise Allibi",
        email="contact@allibi.fr",
        is_active=True,
    )

    response = client.post(
        reverse("clients:update", args=[client_obj.public_id]),
        {
            "name": "",
            "email": "adresse-invalide",
        },
    )

    assert response.status_code == 200
    assert "name" in response.context["form"].errors
    assert "email" in response.context["form"].errors

    client_obj.refresh_from_db()

    assert client_obj.name == "Entreprise Allibi"
    assert client_obj.email == "contact@allibi.fr"


@pytest.mark.django_db
def test_technician_cannot_update_client(client, django_user_model):
    user = django_user_model.objects.create_user(
        username="technician",
        password="TestPassword123!",
        role=User.Role.TECHNICIAN,
    )

    client.force_login(user)
    client_obj = Client.objects.create(
        name="Entreprise Allibi",
    )

    response = client.post(
        reverse("clients:update", args=[client_obj.public_id]),
        {"name": "Modification interdite"},
    )

    assert response.status_code == 403

    client_obj.refresh_from_db()
    assert client_obj.name == "Entreprise Allibi"


@pytest.mark.django_db
def test_client_update_displays_correct_form_labels(
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
        is_active=True,
    )

    response = client.get(reverse("clients:update", args=[client_obj.public_id]))

    assert response.status_code == 200
    assert response.context["is_edit"] is True
    assert "Modifier un client" in response.content.decode()
    assert "Enregistrer les modifications" in response.content.decode()
    assert (
        f'href="{reverse("clients:detail", args=[client_obj.public_id])}"'
        in response.content.decode()
    )
    assert 'value="Entreprise Allibi"' in response.content.decode()
    assert 'value="contact@allibi.fr"' in response.content.decode()
