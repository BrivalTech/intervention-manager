import pytest
from django.urls import reverse

from apps.accounts.models import User


@pytest.fixture
def technician(django_user_model):
    return django_user_model.objects.create_user(
        username="alice",
        password="SecurePassword123!",
        first_name="Alice",
        last_name="Martin",
        email="alice@example.com",
        role=User.Role.TECHNICIAN,
    )


@pytest.mark.django_db
def test_admin_can_access_technician_update(
    client,
    django_user_model,
    technician,
):
    admin = django_user_model.objects.create_user(
        username="admin_update",
        role=User.Role.ADMIN,
    )

    client.force_login(admin)
    response = client.get(
        reverse("accounts:technician_update", args=[technician.public_id])
    )

    assert response.status_code == 200
    assert response.context["form"].instance == technician
    assert response.context["is_edit"] is True
    assert b"form-control" in response.content


@pytest.mark.django_db
@pytest.mark.parametrize(
    "role",
    [User.Role.MANAGER, User.Role.TECHNICIAN],
)
def test_non_admin_cannot_update_technician(
    client,
    django_user_model,
    technician,
    role,
):
    user = django_user_model.objects.create_user(
        username=f"user_{role.lower()}",
        role=role,
    )

    client.force_login(user)
    url = reverse("accounts:technician_update", args=[technician.public_id])
    response = client.get(url)

    assert response.status_code == 403

    response = client.post(
        url,
        {
            "first_name": "Modified",
            "last_name": "Martin",
            "username": "alice",
            "email": "alice@example.com",
        },
    )
    assert response.status_code == 403

    technician.refresh_from_db()
    assert technician.first_name == "Alice"


@pytest.mark.django_db
def test_admin_updates_technician_without_changing_password(
    client,
    django_user_model,
    technician,
):
    admin = django_user_model.objects.create_user(
        username="admin_update",
        role=User.Role.ADMIN,
    )

    client.force_login(admin)
    original_password = technician.password
    response = client.post(
        reverse("accounts:technician_update", args=[technician.public_id]),
        {
            "first_name": "Alicia",
            "last_name": "Martin",
            "username": "alicia",
            "email": "alicia@example.com",
        },
    )

    assert response.status_code == 302
    assert response.url == reverse("accounts:technician_list")

    technician.refresh_from_db()

    assert technician.first_name == "Alicia"
    assert technician.email == "alicia@example.com"
    assert technician.role == User.Role.TECHNICIAN
    assert technician.password == original_password
    assert technician.is_active is True


@pytest.mark.django_db
def test_invalid_update_does_not_save(
    client,
    django_user_model,
    technician,
):
    admin = django_user_model.objects.create_user(
        username="admin_update",
        role=User.Role.ADMIN,
    )

    client.force_login(admin)
    response = client.post(
        reverse("accounts:technician_update", args=[technician.public_id]),
        {
            "first_name": "Alicia",
            "last_name": "Martin",
            "username": "alicia",
            "email": "",
        },
    )

    assert response.status_code == 200
    assert "email" in response.context["form"].errors

    technician.refresh_from_db()
    assert technician.first_name == "Alice"


@pytest.mark.django_db
def test_technician_update_requires_authentication(client, technician):
    response = client.get(
        reverse(
            "accounts:technician_update",
            args=[technician.public_id],
        )
    )

    assert response.status_code == 302


@pytest.mark.django_db
def test_cannot_update_non_technician(client, django_user_model):
    admin = django_user_model.objects.create_user(
        username="admin_update",
        role=User.Role.ADMIN,
    )

    client.force_login(admin)
    response = client.get(reverse("accounts:technician_update", args=[admin.public_id]))

    assert response.status_code == 404
