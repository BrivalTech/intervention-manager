import pytest
from django.urls import reverse

from apps.accounts.models import User
from apps.clients.models import Client


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
        f'href="{reverse("clients:detail", args=[client_allibi.public_id])}"'
        in response.content.decode()
    )
    assert (
        f'href="{reverse("clients:detail", args=[client_bonpain.public_id])}"'
        in response.content.decode()
    )


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
            args=[client_obj.public_id],
        )
        assert f'href="{detail_url}"' in response.content.decode()

    for client_obj in clients[10:]:
        detail_url = reverse(
            "clients:detail",
            args=[client_obj.public_id],
        )
        assert f'href="{detail_url}"' not in response.content.decode()
