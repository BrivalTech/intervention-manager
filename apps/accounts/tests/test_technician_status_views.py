import pytest
from django.urls import reverse

from apps.accounts.models import User


@pytest.fixture
def admin(django_user_model):
    return django_user_model.objects.create_user(
        username="admin_status",
        role=User.Role.ADMIN,
    )


@pytest.fixture
def technician(django_user_model):
    return django_user_model.objects.create_user(
        username="tech_status",
        password="SecurePassword123!",
        role=User.Role.TECHNICIAN,
    )


@pytest.mark.django_db
def test_admin_can_deactivate_technician(client, admin, technician):
    client.force_login(admin)

    response = client.post(
        reverse("accounts:technician_deactivate", args=[technician.public_id])
    )

    assert response.status_code == 302
    assert response.url == reverse("accounts:technician_list")

    technician.refresh_from_db()
    assert technician.is_active is False


@pytest.mark.django_db
def test_admin_can_reactivate_technician(client, admin, technician):
    technician.is_active = False
    technician.save(update_fields=["is_active"])
    client.force_login(admin)
    response = client.post(
        reverse("accounts:technician_reactivate", args=[technician.public_id])
    )

    assert response.status_code == 302

    technician.refresh_from_db()
    assert technician.is_active is True


@pytest.mark.django_db
@pytest.mark.parametrize(
    "action",
    ["technician_deactivate", "technician_reactivate"],
)
def test_status_change_requires_post(client, admin, technician, action):
    client.force_login(admin)
    response = client.get(reverse(f"accounts:{action}", args=[technician.public_id]))

    assert response.status_code == 405


@pytest.mark.django_db
@pytest.mark.parametrize(
    "role",
    [User.Role.MANAGER, User.Role.TECHNICIAN],
)
@pytest.mark.parametrize(
    "action",
    ["technician_deactivate", "technician_reactivate"],
)
def test_non_admin_cannot_change_technician_status(
    client,
    django_user_model,
    technician,
    role,
    action,
):
    user = django_user_model.objects.create_user(
        username=f"user_{role.lower()}",
        role=role,
    )

    client.force_login(user)
    original_status = technician.is_active
    response = client.post(reverse(f"accounts:{action}", args=[technician.public_id]))

    assert response.status_code == 403

    technician.refresh_from_db()
    assert technician.is_active == original_status


@pytest.mark.django_db
@pytest.mark.parametrize(
    "action",
    ["technician_deactivate", "technician_reactivate"],
)
def test_cannot_change_non_technician_status(client, admin, action):
    client.force_login(admin)
    response = client.post(reverse(f"accounts:{action}", args=[admin.public_id]))

    assert response.status_code == 404

    admin.refresh_from_db()
    assert admin.is_active is True


@pytest.mark.django_db
def test_inactive_technician_cannot_log_in(client, technician):
    technician.is_active = False
    technician.save(update_fields=["is_active"])
    logged_in = client.login(
        username="tech_status",
        password="SecurePassword123!",
    )

    assert logged_in is False


@pytest.mark.django_db
def test_deactivated_technician_loses_access(client, technician):
    technician_client = client
    technician_client.force_login(technician)
    response = technician_client.get(reverse("accounts:login"))

    assert response.wsgi_request.user.is_authenticated

    technician.is_active = False
    technician.save(update_fields=["is_active"])
    response = technician_client.get(reverse("accounts:login"))

    assert not response.wsgi_request.user.is_authenticated
