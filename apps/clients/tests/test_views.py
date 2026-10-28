import pytest
from django.contrib.messages import get_messages
from django.urls import reverse

from apps.accounts.models import User
from apps.clients.models import Client
from apps.interventions.models import Intervention


def test_client_list_requires_authentication(client):
    response = client.get(reverse("clients:list"))

    assert response.status_code == 302
    assert response.url.startswith(reverse("accounts:login"))


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("role", "expected_status"),
    [
        (User.Role.ADMIN, 200),
        (User.Role.MANAGER, 200),
        (User.Role.TECHNICIAN, 403),
    ],
)
def test_client_list_acces_by_role(
    client,
    django_user_model,
    role,
    expected_status,
):
    user = django_user_model.objects.create_user(
        username=f"user-{role.lower()}",
        password="TestPassword123",
        role=role,
    )

    client.force_login(user)
    response = client.get(reverse("clients:list"))

    assert response.status_code == expected_status

    if expected_status == 200:
        assert "Clients" in response.content.decode()


@pytest.mark.django_db
def test_inactive_user_cannot_access_client_list(client, django_user_model):
    user = django_user_model.objects.create_user(
        username="inactive-user",
        password="TestPassword123",
        role=User.Role.ADMIN,
        is_active=False,
    )

    client.force_login(user)

    response = client.get(reverse("clients:list"))

    assert response.status_code == 302
    assert response.url.startswith(reverse("accounts:login"))


@pytest.mark.django_db
def test_client_list_displays_active_clients(client, django_user_model):
    user = django_user_model.objects.create_user(
        username="manager",
        password="TestPassword123!",
        role=User.Role.MANAGER,
    )

    client.force_login(user)

    Client.objects.create(
        name="Entreprise Durand",
        contact_name="Marie Dupont",
        city="Paris",
    )
    Client.objects.create(
        name="Entreprise Dupont",
        is_active=False,
    )

    response = client.get(reverse("clients:list"))

    assert response.status_code == 200
    assert b"Entreprise Durand" in response.content
    assert b"Entreprise Beta" not in response.content
    assert b"Marie Dupont" in response.content


@pytest.mark.django_db
def test_client_list_is_ordered_by_name(client, django_user_model):
    user = django_user_model.objects.create_user(
        username="manager",
        password="TestPassword123!",
        role=User.Role.MANAGER,
    )

    client.force_login(user)

    Client.objects.create(name="Zephir")
    Client.objects.create(name="Abracadabra")
    Client.objects.create(name="Banco")

    response = client.get(reverse("clients:list"))

    names = [client.name for client in response.context["clients"]]

    assert names == ["Abracadabra", "Banco", "Zephir"]


@pytest.mark.django_db
def test_client_list_displays_empty_state(client, django_user_model):
    user = django_user_model.objects.create_user(
        username="manager",
        password="TestPassword123!",
        role=User.Role.MANAGER,
    )

    client.force_login(user)

    response = client.get(reverse("clients:list"))

    assert response.status_code == 200
    assert "Aucun client actif" in response.content.decode()


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("status", "expected_names"),
    [
        ("active", ["Client Actif"]),
        ("archived", ["Client Archivé"]),
        ("all", ["Client Actif", "Client Archivé"]),
    ],
)
def test_client_list_filters_by_status(
    client,
    django_user_model,
    status,
    expected_names,
):
    user = django_user_model.objects.create_user(
        username="manager",
        password="TestPassword123!",
        role=User.Role.MANAGER,
    )

    client.force_login(user)

    Client.objects.create(name="Client Actif")
    Client.objects.create(
        name="Client Archivé",
        is_active=False,
    )

    response = client.get(
        reverse("clients:list"),
        {"status": status},
    )

    names = [client.name for client in response.context["clients"]]

    assert response.status_code == 200
    assert names == expected_names


@pytest.mark.django_db
@pytest.mark.parametrize(
    "search_term",
    [
        "ALLIBI",
        "marie",
        "contact@example.com",
        "paris",
    ],
)
def test_client_list_searches_multiple_fields(
    client,
    django_user_model,
    search_term,
):
    user = django_user_model.objects.create_user(
        username="manager",
        password="TestPassword123!",
        role=User.Role.MANAGER,
    )

    client.force_login(user)

    Client.objects.create(
        name="Entreprise Allibi",
        contact_name="Marie Dupont",
        email="contact@example.com",
        city="Paris",
    )
    Client.objects.create(
        name="Entreprise Betruc",
        city="Lyon",
    )

    response = client.get(
        reverse("clients:list"),
        {"q": search_term},
    )

    names = [client.name for client in response.context["clients"]]

    assert response.status_code == 200
    assert names == ["Entreprise Allibi"]


@pytest.mark.django_db
def test_client_list_combines_search_and_status(client, django_user_model):
    user = django_user_model.objects.create_user(
        username="manager",
        password="TestPassword123!",
        role=User.Role.MANAGER,
    )

    client.force_login(user)

    Client.objects.create(name="Allibi Active")
    Client.objects.create(
        name="Allibi Archivé",
        is_active=False,
    )
    Client.objects.create(
        name="Betruc Archivé",
        is_active=False,
    )

    response = client.get(
        reverse("clients:list"),
        {
            "q": "allibi",
            "status": "archived",
        },
    )

    names = [client.name for client in response.context["clients"]]

    assert names == ["Allibi Archivé"]


@pytest.mark.django_db
def test_client_list_defaults_to_active_for_invalid_status(
    client,
    django_user_model,
):
    user = django_user_model.objects.create_user(
        username="manager",
        password="TestPassword123!",
        role=User.Role.MANAGER,
    )

    client.force_login(user)

    Client.objects.create(name="Client Actif")
    Client.objects.create(
        name="Client Archivé",
        is_active=False,
    )

    response = client.get(
        reverse("clients:list"),
        {"status": "invalid"},
    )

    names = [client.name for client in response.context["clients"]]

    assert response.status_code == 200
    assert response.context["status"] == "active"
    assert names == ["Client Actif"]


@pytest.mark.django_db
def test_client_list_is_paginated(client, django_user_model):
    user = django_user_model.objects.create_user(
        username="manager",
        password="TestPassword123!",
        role=User.Role.MANAGER,
    )

    client.force_login(user)

    for index in range(15):
        Client.objects.create(name=f"Client {index:02d}")

    response = client.get(reverse("clients:list"))

    assert response.status_code == 200
    assert len(response.context["clients"]) == 10
    assert response.context["page_obj"].number == 1
    assert response.context["page_obj"].paginator.num_pages == 2

    response = client.get(
        reverse("clients:list"),
        {"page": "2"},
    )

    assert response.status_code == 200
    assert len(response.context["clients"]) == 5
    assert response.context["page_obj"].number == 2


@pytest.mark.django_db
@pytest.mark.parametrize("client_count", [0, 1, 10])
def test_client_list_has_single_page(
    client,
    django_user_model,
    client_count,
):
    user = django_user_model.objects.create_user(
        username="manager",
        password="TestPassword123!",
        role=User.Role.MANAGER,
    )

    client.force_login(user)

    for index in range(client_count):
        Client.objects.create(name=f"Client {index:02d}")

    response = client.get(reverse("clients:list"))

    assert response.status_code == 200
    assert len(response.context["clients"]) == client_count
    assert response.context["result_count"] == client_count
    assert response.context["page_obj"].paginator.num_pages == 1

    assert 'aria-label="Pagination des clients"' not in (response.content.decode())


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("requested_page", "expected_page"),
    [
        ("abc", 1),
        ("0", 2),
        ("-1", 2),
        ("999", 2),
    ],
)
def test_client_list_handles_invalid_page(
    client,
    django_user_model,
    requested_page,
    expected_page,
):
    user = django_user_model.objects.create_user(
        username="manager",
        password="TestPassword123!",
        role=User.Role.MANAGER,
    )

    client.force_login(user)

    for index in range(15):
        Client.objects.create(name=f"Client {index:02d}")

    response = client.get(
        reverse("clients:list"),
        {"page": requested_page},
    )

    assert response.status_code == 200
    assert response.context["page_obj"].number == expected_page


@pytest.mark.django_db
def test_client_list_pagination_navigation(client, django_user_model):
    user = django_user_model.objects.create_user(
        username="manager",
        password="TestPassword123!",
        role=User.Role.MANAGER,
    )

    client.force_login(user)

    for index in range(25):
        Client.objects.create(name=f"Client {index:02d}")

    url = reverse("clients:list")

    first_page = client.get(url)
    assert first_page.context["page_obj"].has_next()
    assert not first_page.context["page_obj"].has_previous()
    assert "Suivant" in first_page.content.decode()

    second_page = client.get(url, {"page": 2})
    assert second_page.context["page_obj"].has_next()
    assert second_page.context["page_obj"].has_previous()
    assert "Précédent" in second_page.content.decode()
    assert "Suivant" in second_page.content.decode()

    last_page = client.get(url, {"page": 3})
    assert last_page.context["page_obj"].has_previous()
    assert not last_page.context["page_obj"].has_next()
    assert "Précédent" in last_page.content.decode()


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
@pytest.mark.parametrize(
    "role",
    [
        User.Role.ADMIN,
        User.Role.MANAGER,
    ],
)
def test_client_list_displays_create_link(
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
    response = client.get(reverse("clients:list"))

    assert response.status_code == 200
    assert response.context["can_create_client"] is True

    assert f'href="{reverse("clients:create")}"'.encode() in response.content

    assert "Créer un client" in response.content.decode()


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
    response = client.get(reverse("clients:detail", args=[client_obj.pk]))

    assert response.status_code == expected_status


@pytest.mark.django_db
def test_client_detail_requires_authentication(client):
    client_obj = Client.objects.create(name="Entreprise Alpha")
    response = client.get(reverse("clients:detail", args=[client_obj.pk]))

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

    response = client.get(reverse("clients:detail", args=[client_obj.pk]))

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

    response = client.get(reverse("clients:detail", args=[client_obj.pk]))

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
    response = client.get(reverse("clients:detail", args=[999999]))

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

    response = client.get(reverse("clients:detail", args=[client_obj.pk]))

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
    response = client.get(reverse("clients:detail", args=[client_obj.pk]))

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

    response = client.get(reverse("clients:detail", args=[client_obj.pk]))

    assert response.status_code == 200
    assert 'href="mailto:contact@allibi.fr"' in response.content.decode()
    assert 'href="tel:0102030405"' in response.content.decode()
    assert f'href="{reverse("clients:list")}"' in response.content.decode()
    assert 'id="client-detail-title"' in response.content.decode()


@pytest.mark.django_db
def test_client_list_displays_detail_links(client, django_user_model):
    user = django_user_model.objects.create_user(
        username="manager",
        password="TestPassword123!",
        role=User.Role.MANAGER,
    )

    client.force_login(user)
    client_allibi = Client.objects.create(name="Entreprise Allibi")
    client_bonpain = Client.objects.create(name="Entreprise Bon Pain")
    response = client.get(reverse("clients:list"))

    assert response.status_code == 200
    assert (
        f'href="{reverse("clients:detail", args=[client_allibi.pk])}"'
        in response.content.decode()
    )
    assert (
        f'href="{reverse("clients:detail", args=[client_bonpain.pk])}"'
        in response.content.decode()
    )


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

    response = client.get(reverse("clients:detail", args=[client_allibi.pk]))

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

    response = client.get(reverse("clients:detail", args=[client_obj.pk]))

    assert response.status_code == 200
    assert f'href="{reverse("clients:list")}"' in response.content.decode()
    assert "Retour aux clients" in response.content.decode()


@pytest.mark.django_db
def test_client_list_detail_links_respect_pagination(
    client,
    django_user_model,
):
    user = django_user_model.objects.create_user(
        username="manager",
        password="TestPassword123!",
        role=User.Role.MANAGER,
    )

    client.force_login(user)
    clients = [Client.objects.create(name=f"Client {index:02d}") for index in range(15)]

    response = client.get(reverse("clients:list"), {"page": 1})

    assert response.status_code == 200
    for client_obj in clients[:10]:
        detail_url = reverse(
            "clients:detail",
            args=[client_obj.pk],
        )
        assert f'href="{detail_url}"' in response.content.decode()

    for client_obj in clients[10:]:
        detail_url = reverse(
            "clients:detail",
            args=[client_obj.pk],
        )
        assert f'href="{detail_url}"' not in response.content.decode()


# Update
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
    response = client.get(reverse("clients:update", args=[client_obj.pk]))

    assert response.status_code == expected_status


@pytest.mark.django_db
def test_client_update_requires_authentication(client):
    client_obj = Client.objects.create(
        name="Entreprise Allibi",
        is_active=True,
    )
    response = client.get(reverse("clients:update", args=[client_obj.pk]))

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

    response = client.get(reverse("clients:update", args=[client_obj.pk]))
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
        reverse("clients:update", args=[client_obj.pk]),
        {
            "name": "Entreprise Allibi Modifiée",
            "city": "Lyon",
        },
    )

    assert response.status_code == 302
    assert response.url == reverse(
        "clients:detail",
        args=[client_obj.pk],
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
        reverse("clients:update", args=[client_obj.pk]),
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
        reverse("clients:update", args=[client_obj.pk]),
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

    response = client.get(reverse("clients:update", args=[client_obj.pk]))

    assert response.status_code == 200
    assert response.context["is_edit"] is True
    assert "Modifier un client" in response.content.decode()
    assert "Enregistrer les modifications" in response.content.decode()
    assert (
        f'href="{reverse("clients:detail", args=[client_obj.pk])}"'
        in response.content.decode()
    )
    assert 'value="Entreprise Allibi"' in response.content.decode()
    assert 'value="contact@allibi.fr"' in response.content.decode()


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
    response = client.get(reverse("clients:detail", args=[client_obj.pk]))

    assert response.status_code == 200
    assert response.context["can_edit_client"] is True

    edit_url = reverse(
        "clients:update",
        args=[client_obj.pk],
    )

    assert f'href="{edit_url}"' in response.content.decode()
    assert "Modifier le client" in response.content.decode()


# Archive
@pytest.mark.django_db
@pytest.mark.parametrize(
    ("role", "expected_status"),
    [
        (User.Role.ADMIN, 200),
        (User.Role.MANAGER, 403),
        (User.Role.TECHNICIAN, 403),
    ],
)
def test_client_archive_access_by_role(
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
    response = client.get(reverse("clients:archive", args=[client_obj.pk]))

    assert response.status_code == expected_status


@pytest.mark.django_db
def test_client_archive_success(client, django_user_model):
    user = django_user_model.objects.create_user(
        username="admin",
        password="TestPassword123!",
        role=User.Role.ADMIN,
    )

    client.force_login(user)
    client_obj = Client.objects.create(name="Entreprise Allibi")
    response = client.post(reverse("clients:archive", args=[client_obj.pk]))

    assert response.status_code == 302
    assert response.url == reverse(
        "clients:detail",
        args=[client_obj.pk],
    )

    client_obj.refresh_from_db()

    assert client_obj.is_active is False
    assert Client.objects.filter(pk=client_obj.pk).exists()


@pytest.mark.django_db
def test_client_archive_already_archived(client, django_user_model):
    user = django_user_model.objects.create_user(
        username="admin",
        password="TestPassword123!",
        role=User.Role.ADMIN,
    )

    client.force_login(user)
    client_obj = Client.objects.create(
        name="Entreprise Allibi",
        is_active=False,
    )

    response = client.post(reverse("clients:archive", args=[client_obj.pk]))

    assert response.status_code == 302
    assert response.url == reverse(
        "clients:detail",
        args=[client_obj.pk],
    )

    client_obj.refresh_from_db()

    assert client_obj.is_active is False


@pytest.mark.django_db
def test_admin_can_see_archive_link(client, django_user_model):
    user = django_user_model.objects.create_user(
        username="admin",
        password="TestPassword123!",
        role=User.Role.ADMIN,
    )

    client.force_login(user)
    client_obj = Client.objects.create(name="Entreprise Allibi")
    response = client.get(reverse("clients:detail", args=[client_obj.pk]))

    assert response.status_code == 200
    assert response.context["can_archive_client"] is True

    archive_url = reverse(
        "clients:archive",
        args=[client_obj.pk],
    )

    assert f'href="{archive_url}"' in response.content.decode()
    assert "Archiver le client" in response.content.decode()


@pytest.mark.django_db
def test_manager_cannot_see_archive_link(client, django_user_model):
    user = django_user_model.objects.create_user(
        username="manager",
        password="TestPassword123!",
        role=User.Role.MANAGER,
    )

    client.force_login(user)
    client_obj = Client.objects.create(
        name="Entreprise Allibi",
    )
    response = client.get(reverse("clients:detail", args=[client_obj.pk]))

    assert response.status_code == 200
    assert response.context["can_archive_client"] is False

    archive_url = reverse(
        "clients:archive",
        args=[client_obj.pk],
    )

    assert f'href="{archive_url}"' not in response.content.decode()
    assert "Modifier le client" in response.content.decode()


@pytest.mark.django_db
def test_archived_client_has_no_archive_link(client, django_user_model):
    user = django_user_model.objects.create_user(
        username="admin",
        password="TestPassword123!",
        role=User.Role.ADMIN,
    )

    client.force_login(user)
    client_obj = Client.objects.create(
        name="Ancien Client",
        is_active=False,
    )

    response = client.get(reverse("clients:detail", args=[client_obj.pk]))

    assert response.status_code == 200
    assert response.context["can_archive_client"] is False

    archive_url = reverse(
        "clients:archive",
        args=[client_obj.pk],
    )

    assert f'href="{archive_url}"' not in response.content.decode()
    assert "Modifier le client" not in response.content.decode()


@pytest.mark.django_db
def test_client_archive_refused_with_active_intervention(
    client,
    django_user_model,
):
    admin = django_user_model.objects.create_user(
        username="archive_admin",
        password="TestPassword123!",
        role=User.Role.ADMIN,
    )
    client_obj = Client.objects.create(
        name="Client avec intervention en cours",
    )
    Intervention.objects.create(
        client=client_obj,
        created_by=admin,
        title="Intervention en cours",
        status=Intervention.Status.IN_PROGRESS,
    )

    client.force_login(admin)
    response = client.post(reverse("clients:archive", args=[client_obj.pk]))

    assert response.status_code == 302
    assert response.url == reverse(
        "clients:detail",
        args=[client_obj.pk],
    )

    client_obj.refresh_from_db()
    assert client_obj.is_active

    displayed_messages = [
        str(message) for message in get_messages(response.wsgi_request)
    ]

    assert any(
        "Impossible d'archiver ce client" in message for message in displayed_messages
    )


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
