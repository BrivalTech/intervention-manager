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
def test_client_create_access_by_role(
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

    response = client.get(reverse("clients:create"))

    assert response.status_code == expected_status


def test_client_create_requires_authentication(client):
    response = client.get(reverse("clients:create"))

    assert response.status_code == 302
    assert response.url.startswith(reverse("accounts:login"))


@pytest.mark.django_db
def test_client_create_success(client, django_user_model):
    user = django_user_model.objects.create_user(
        username="manager",
        password="TestPassword123!",
        role=User.Role.MANAGER,
    )

    client.force_login(user)

    response = client.post(
        reverse("clients:create"),
        {
            "name": "Entreprise Durand",
            "contact_name": "Marie Durand",
            "email": "contact@durand.fr",
            "city": "Paris",
        },
    )

    assert response.status_code == 302
    assert response.url == reverse("clients:list")

    created_client = Client.objects.get(name="Entreprise Durand")
    assert created_client.contact_name == "Marie Durand"
    assert created_client.is_active is True


@pytest.mark.django_db
def test_client_create_invalid_data(client, django_user_model):
    user = django_user_model.objects.create_user(
        username="manager",
        password="TestPassword123!",
        role=User.Role.MANAGER,
    )

    client.force_login(user)

    response = client.post(
        reverse("clients:create"),
        {
            "name": "",
            "email": "adresse-invalide",
        },
    )

    assert response.status_code == 200
    assert "name" in response.context["form"].errors
    assert "email" in response.context["form"].errors
    assert Client.objects.count() == 0


@pytest.mark.django_db
def test_technician_cannot_create_client(
    client,
    django_user_model,
):
    user = django_user_model.objects.create_user(
        username="technician",
        password="TestPassword123!",
        role=User.Role.TECHNICIAN,
    )

    client.force_login(user)

    response = client.post(
        reverse("clients:create"),
        {"name": "Client interdit"},
    )

    assert response.status_code == 403
    assert not Client.objects.filter(name="Client interdit").exists()


@pytest.mark.django_db
def test_client_create_form_displays_accessible_errors(
    client,
    django_user_model,
):
    user = django_user_model.objects.create_user(
        username="manager",
        password="TestPassword123!",
        role=User.Role.MANAGER,
    )

    client.force_login(user)
    response = client.post(
        reverse("clients:create"),
        {
            "name": "Entreprise Allibi",
            "email": "adresse-invalide",
        },
    )

    assert response.status_code == 200
    assert 'role="alert"' in response.content.decode()
    assert 'aria-invalid="true"' in response.content.decode()
    assert 'aria-describedby="id_email_error"' in response.content.decode()
    assert 'id="id_email_error"' in response.content.decode()
    assert "adresse-invalide" in response.content.decode()


@pytest.mark.django_db
def test_client_create_link_opens_form(client, django_user_model):
    user = django_user_model.objects.create_user(
        username="manager",
        password="TestPassword123!",
        role=User.Role.MANAGER,
    )

    client.force_login(user)
    response = client.get(reverse("clients:create"))

    assert response.status_code == 200
    assert "form" in response.context
    assert b"Enregistrer le client" in response.content


@pytest.mark.django_db
def test_client_creation_success_message_is_visible(
    client,
    django_user_model,
):
    user = django_user_model.objects.create_user(
        username="message-test-admin",
        password="TestPassword123!",
        role=User.Role.ADMIN,
    )
    client.force_login(user)
    response = client.post(
        reverse("clients:create"),
        {"name": "Client notification"},
        follow=True,
    )

    assert response.status_code == 200
    assert b"Le client a" in response.content
    assert "message--success" in response.content.decode()
    assert "Client notification" in response.content.decode()
