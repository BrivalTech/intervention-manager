from smtplib import SMTPException
from unittest.mock import patch

import pytest
from django.contrib.messages import WARNING, get_messages
from django.urls import reverse

from apps.accounts.models import User


@pytest.fixture
def admin_client(client, django_user_model):
    admin = django_user_model.objects.create_user(
        username="admin_manager_operations",
        password="TestPassword123!",
        role=User.Role.ADMIN,
    )
    client.force_login(admin)
    return client


@pytest.fixture
def manager(django_user_model):
    return django_user_model.objects.create_user(
        username="manager_operations",
        first_name="Alice",
        last_name="Martin",
        email="alice@example.com",
        password="TestPassword123!",
        role=User.Role.MANAGER,
    )


@pytest.mark.django_db
def test_manager_creation(admin_client, django_user_model):
    with patch(
        "apps.accounts.account_views.send_account_invitation",
        return_value=1,
    ) as mock_send:
        response = admin_client.post(
            reverse("accounts:manager_create"),
            {
                "first_name": "Sophie",
                "last_name": "Durand",
                "username": "sophie.durand",
                "email": "sophie@example.com",
            },
        )

    assert response.status_code == 302

    account = django_user_model.objects.get(username="sophie.durand")
    assert account.role == User.Role.MANAGER
    assert not account.has_usable_password()

    mock_send.assert_called_once()


@pytest.mark.django_db
def test_manager_creation_keeps_account_when_email_fails(
    admin_client,
    django_user_model,
):
    with patch(
        "apps.accounts.account_views.send_account_invitation",
        side_effect=SMTPException("SMTP unavailable"),
    ):
        response = admin_client.post(
            reverse("accounts:manager_create"),
            {
                "first_name": "Sophie",
                "last_name": "Durand",
                "username": "sophie.durand",
                "email": "sophie@example.com",
            },
        )

    assert response.status_code == 302

    account = django_user_model.objects.get(username="sophie.durand")
    assert account.role == User.Role.MANAGER
    assert not account.has_usable_password()

    messages_list = list(get_messages(response.wsgi_request))
    assert any(
        message.level == WARNING
        and "l'invitation n'a pas pu être envoyée" in str(message)
        for message in messages_list
    )


@pytest.mark.django_db
def test_manager_update_preserves_role_and_password(admin_client, manager):
    original_password = manager.password

    response = admin_client.post(
        reverse("accounts:manager_update", args=[manager.public_id]),
        {
            "first_name": "Alice",
            "last_name": "Dupont",
            "username": "manager_operations",
            "email": "alice@example.com",
        },
    )

    assert response.status_code == 302

    manager.refresh_from_db()
    assert manager.last_name == "Dupont"
    assert manager.role == User.Role.MANAGER
    assert manager.password == original_password


@pytest.mark.django_db
def test_manager_deactivation_and_reactivation(admin_client, manager):
    deactivate_url = reverse(
        "accounts:manager_deactivate",
        args=[manager.public_id],
    )
    reactivate_url = reverse(
        "accounts:manager_reactivate",
        args=[manager.public_id],
    )

    assert admin_client.get(deactivate_url).status_code == 405

    response = admin_client.post(deactivate_url)
    assert response.status_code == 302

    manager.refresh_from_db()
    assert not manager.is_active

    assert admin_client.get(reactivate_url).status_code == 405

    response = admin_client.post(reactivate_url)
    assert response.status_code == 302

    manager.refresh_from_db()
    assert manager.is_active


@pytest.mark.django_db
def test_manager_resend_invitation(admin_client, manager):
    manager.set_unusable_password()
    manager.save(update_fields=["password"])

    with patch(
        "apps.accounts.account_views.send_account_invitation",
        return_value=1,
    ) as mock_send:
        response = admin_client.post(
            reverse(
                "accounts:manager_resend_invitation",
                args=[manager.public_id],
            )
        )

    assert response.status_code == 302
    mock_send.assert_called_once()


@pytest.mark.django_db
def test_manager_with_password_cannot_receive_invitation(admin_client, manager):
    with patch(
        "apps.accounts.account_views.send_account_invitation",
    ) as mock_send:
        response = admin_client.post(
            reverse(
                "accounts:manager_resend_invitation",
                args=[manager.public_id],
            )
        )

    assert response.status_code == 302
    mock_send.assert_not_called()


@pytest.mark.django_db
@pytest.mark.parametrize("role", [User.Role.MANAGER, User.Role.TECHNICIAN])
def test_non_admin_cannot_create_manager(client, django_user_model, role):
    user = django_user_model.objects.create_user(
        username=f"restricted_{role}",
        password="TestPassword123!",
        role=role,
    )

    client.force_login(user)
    response = client.post(
        reverse("accounts:manager_create"),
        {
            "first_name": "Sophie",
            "last_name": "Durand",
            "username": "sophie.restricted",
            "email": "sophie.restricted@example.com",
        },
    )

    assert response.status_code == 403
    assert not django_user_model.objects.filter(username="sophie.restricted").exists()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "url_name",
    [
        "manager_update",
        "manager_deactivate",
        "manager_reactivate",
        "manager_resend_invitation",
    ],
)
def test_manager_actions_reject_technician(admin_client, django_user_model, url_name):
    technician = django_user_model.objects.create_user(
        username="technician_isolation",
        password="TestPassword123!",
        role=User.Role.TECHNICIAN,
    )

    response = admin_client.post(
        reverse(f"accounts:{url_name}", args=[technician.public_id])
    )

    assert response.status_code == 404

    technician.refresh_from_db()
    assert technician.role == User.Role.TECHNICIAN
    assert technician.is_active


@pytest.mark.django_db
@pytest.mark.parametrize(
    "url_name",
    [
        "manager_deactivate",
        "manager_reactivate",
        "manager_resend_invitation",
    ],
)
def test_manager_actions_require_post(admin_client, manager, url_name):
    response = admin_client.get(
        reverse(f"accounts:{url_name}", args=[manager.public_id])
    )

    assert response.status_code == 405
