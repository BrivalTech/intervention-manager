from unittest.mock import patch

import pytest
from django.core import mail
from django.test import override_settings
from django.urls import reverse

from apps.accounts.models import User


@pytest.fixture
def admin(django_user_model):
    return django_user_model.objects.create_user(
        username="admin_invites",
        role=User.Role.ADMIN,
    )


@pytest.fixture
def technician(django_user_model):
    user = django_user_model.objects.create_user(
        username="technician_invites",
        first_name="Alice",
        email="alice@example.com",
        role=User.Role.TECHNICIAN,
    )
    user.set_unusable_password()
    user.save(update_fields=["password"])
    return user


@pytest.mark.django_db
@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    DEFAULT_FROM_EMAIL="no-reply@example.com",
)
def test_admin_can_resend_invitation(client, admin, technician):
    client.force_login(admin)

    response = client.post(
        reverse(
            "accounts:technician_resend_invitation",
            args=[technician.public_id],
        )
    )

    assert response.status_code == 302
    assert response.url == reverse("accounts:technician_list")
    assert len(mail.outbox) == 1
    assert mail.outbox[0].to == ["alice@example.com"]


@pytest.mark.django_db
def test_resend_invitation_requires_post(client, admin, technician):
    client.force_login(admin)

    response = client.get(
        reverse(
            "accounts:technician_resend_invitation",
            args=[technician.public_id],
        )
    )

    assert response.status_code == 405


@pytest.mark.django_db
@pytest.mark.parametrize(
    "role",
    [User.Role.MANAGER, User.Role.TECHNICIAN],
)
def test_non_admin_cannot_resend_invitation(
    client,
    django_user_model,
    technician,
    role,
):
    user = django_user_model.objects.create_user(
        username=f"other_{role.lower()}",
        role=role,
    )

    client.force_login(user)
    response = client.post(
        reverse(
            "accounts:technician_resend_invitation",
            args=[technician.public_id],
        )
    )

    assert response.status_code == 403


@pytest.mark.django_db
def test_cannot_invite_activated_technician(client, admin, technician):
    technician.set_password("SecureTestPassword123!")
    technician.save(update_fields=["password"])

    client.force_login(admin)

    with patch("apps.accounts.services.send_technician_invitation") as send_invitation:
        response = client.post(
            reverse(
                "accounts:technician_resend_invitation",
                args=[technician.public_id],
            )
        )

    assert response.status_code == 302
    send_invitation.assert_not_called()


@pytest.mark.django_db
def test_cannot_invite_inactive_technician(client, admin, technician):
    technician.is_active = False
    technician.save(update_fields=["is_active"])

    client.force_login(admin)

    with patch("apps.accounts.services.send_technician_invitation") as send_invitation:
        response = client.post(
            reverse(
                "accounts:technician_resend_invitation",
                args=[technician.public_id],
            )
        )

    assert response.status_code == 302
    send_invitation.assert_not_called()
