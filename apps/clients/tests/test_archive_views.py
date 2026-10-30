import pytest
from django.contrib.messages import get_messages
from django.urls import reverse

from apps.accounts.models import User
from apps.clients.models import Client
from apps.interventions.models import Intervention


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
    response = client.get(reverse("clients:archive", args=[client_obj.public_id]))

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
    response = client.post(reverse("clients:archive", args=[client_obj.public_id]))

    assert response.status_code == 302
    assert response.url == reverse(
        "clients:detail",
        args=[client_obj.public_id],
    )

    client_obj.refresh_from_db()

    assert client_obj.is_active is False
    assert Client.objects.filter(public_id=client_obj.public_id).exists()


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

    response = client.post(reverse("clients:archive", args=[client_obj.public_id]))

    assert response.status_code == 302
    assert response.url == reverse(
        "clients:detail",
        args=[client_obj.public_id],
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
    response = client.get(reverse("clients:detail", args=[client_obj.public_id]))

    assert response.status_code == 200
    assert response.context["can_archive_client"] is True

    archive_url = reverse(
        "clients:archive",
        args=[client_obj.public_id],
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
    response = client.get(reverse("clients:detail", args=[client_obj.public_id]))

    assert response.status_code == 200
    assert response.context["can_archive_client"] is False

    archive_url = reverse(
        "clients:archive",
        args=[client_obj.public_id],
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

    response = client.get(reverse("clients:detail", args=[client_obj.public_id]))

    assert response.status_code == 200
    assert response.context["can_archive_client"] is False

    archive_url = reverse(
        "clients:archive",
        args=[client_obj.public_id],
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
    response = client.post(reverse("clients:archive", args=[client_obj.public_id]))

    assert response.status_code == 302
    assert response.url == reverse(
        "clients:detail",
        args=[client_obj.public_id],
    )

    client_obj.refresh_from_db()
    assert client_obj.is_active

    displayed_messages = [
        str(message) for message in get_messages(response.wsgi_request)
    ]

    assert any(
        "Impossible d'archiver ce client" in message for message in displayed_messages
    )
