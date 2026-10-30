from smtplib import SMTPException
from unittest.mock import patch

import pytest
from django.contrib.messages import WARNING, get_messages
from django.core import mail
from django.test import override_settings
from django.urls import reverse

from apps.accounts.models import User


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("role", "expected_status"),
    [
        (User.Role.ADMIN, 200),
        (User.Role.MANAGER, 403),
        (User.Role.TECHNICIAN, 403),
    ],
)
def test_technician_create_permissions(
    client,
    django_user_model,
    role,
    expected_status,
):
    user = django_user_model.objects.create_user(
        username=f"user_{role.lower()}",
        role=role,
    )

    client.force_login(user)
    response = client.get(reverse("accounts:technician_create"))

    assert response.status_code == expected_status


@pytest.mark.django_db
def test_technician_create_success(client, django_user_model):
    admin = django_user_model.objects.create_user(
        username="admin",
        role=User.Role.ADMIN,
    )

    client.force_login(admin)
    response = client.post(
        reverse("accounts:technician_create"),
        {
            "first_name": "Alice",
            "last_name": "Martin",
            "username": "alice.martin",
            "email": "alice@example.com",
        },
    )

    assert response.status_code == 302
    assert response.url == reverse("accounts:technician_list")

    technician = django_user_model.objects.get(username="alice.martin")

    assert technician.role == User.Role.TECHNICIAN
    assert technician.has_usable_password() is False


@pytest.mark.django_db
def test_technician_create_invalid_form(client, django_user_model):
    admin = django_user_model.objects.create_user(
        username="admin",
        role=User.Role.ADMIN,
    )
    client.force_login(admin)

    response = client.post(
        reverse("accounts:technician_create"),
        {
            "first_name": "Alice",
            "last_name": "Martin",
            "username": "alice.martin",
            "email": "",
        },
    )

    assert response.status_code == 200
    assert not django_user_model.objects.filter(username="alice.martin").exists()
    assert "email" in response.context["form"].errors


@pytest.mark.django_db
@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    DEFAULT_FROM_EMAIL="no-reply@example.com",
)
def test_technician_create_sends_invitation(client, django_user_model):
    admin = django_user_model.objects.create_user(
        username="admin_invitation",
        role=User.Role.ADMIN,
    )

    client.force_login(admin)
    response = client.post(
        reverse("accounts:technician_create"),
        {
            "first_name": "Alice",
            "last_name": "Martin",
            "username": "alice.martin",
            "email": "alice@example.com",
        },
    )

    assert response.status_code == 302
    assert response.url == reverse("accounts:technician_list")

    technician = django_user_model.objects.get(username="alice.martin")

    assert technician.role == User.Role.TECHNICIAN
    assert technician.has_usable_password() is False
    assert len(mail.outbox) == 1
    assert mail.outbox[0].to == ["alice@example.com"]
    assert "/accounts/invitation/" in mail.outbox[0].body

    messages = [str(message) for message in get_messages(response.wsgi_request)]

    assert any("l'invitation a été envoyée" in message for message in messages)


@pytest.mark.django_db
def test_technician_create_keeps_account_when_email_fails(
    client,
    django_user_model,
):
    admin = django_user_model.objects.create_user(
        username="admin_email_failure",
        role=User.Role.ADMIN,
    )

    client.force_login(admin)

    with patch(
        "apps.accounts.account_views.send_account_invitation",
        side_effect=SMTPException("SMTP unavailable"),
    ):
        response = client.post(
            reverse("accounts:technician_create"),
            {
                "first_name": "Alice",
                "last_name": "Martin",
                "username": "alice.martin",
                "email": "alice@example.com",
            },
        )

    assert response.status_code == 302

    technician = django_user_model.objects.get(username="alice.martin")

    assert technician.role == User.Role.TECHNICIAN
    assert technician.has_usable_password() is False

    messages_list = list(get_messages(response.wsgi_request))

    assert any(
        message.level == WARNING
        and (
            "Le compte technicien a été créé, mais "
            "l'invitation n'a pas pu être envoyée."
        )
        in str(message)
        for message in messages_list
    )


@pytest.mark.django_db
def test_invalid_technician_form_does_not_send_invitation(
    client,
    django_user_model,
):
    admin = django_user_model.objects.create_user(
        username="admin_invalid_form",
        role=User.Role.ADMIN,
    )

    client.force_login(admin)

    with patch("apps.accounts.services.send_technician_invitation") as send_invitation:
        response = client.post(
            reverse("accounts:technician_create"),
            {
                "first_name": "Alice",
                "last_name": "Martin",
                "username": "alice.martin",
                "email": "",
            },
        )

    assert response.status_code == 200
    assert "email" in response.context["form"].errors
    assert not django_user_model.objects.filter(username="alice.martin").exists()

    send_invitation.assert_not_called()
