import pytest
from django.core import mail
from django.test import override_settings
from django.test.client import RequestFactory

from apps.accounts.models import User
from apps.accounts.services import send_account_invitation


@pytest.fixture
def invitation_request():
    return RequestFactory().get("/")


@pytest.fixture
def invited_user(django_user_model):
    def create_user(role, username="invited_user"):
        user = django_user_model.objects.create_user(
            username=username,
            first_name="Alice",
            email="alice@example.com",
            role=role,
        )
        user.set_unusable_password()
        user.save(update_fields=["password"])
        return user

    return create_user


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("role", "role_label"),
    [
        (User.Role.TECHNICIAN, "technicien"),
        (User.Role.MANAGER, "gestionnaire"),
    ],
)
@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    DEFAULT_FROM_EMAIL="no-reply@example.com",
)
def test_send_account_invitation(
    invitation_request,
    invited_user,
    role,
    role_label,
):
    user = invited_user(role)

    sent_count = send_account_invitation(user, invitation_request)

    assert sent_count == 1
    assert len(mail.outbox) == 1
    assert mail.outbox[0].to == ["alice@example.com"]
    assert f"compte {role_label}" in mail.outbox[0].body
    assert "Ce lien est valable pendant 1 heure." in mail.outbox[0].body


@pytest.mark.django_db
def test_cannot_invite_account_with_password(invitation_request, invited_user):
    user = invited_user(User.Role.MANAGER)
    user.set_password("SecureTestPassword123!")
    user.save(update_fields=["password"])

    with pytest.raises(ValueError, match="déjà un mot de passe"):
        send_account_invitation(user, invitation_request)


@pytest.mark.django_db
def test_cannot_invite_inactive_account(invitation_request, invited_user):
    user = invited_user(User.Role.MANAGER)
    user.is_active = False
    user.save(update_fields=["is_active"])

    with pytest.raises(ValueError, match="désactivé"):
        send_account_invitation(user, invitation_request)


@pytest.mark.django_db
def test_cannot_invite_admin(invitation_request, invited_user):
    user = invited_user(User.Role.ADMIN)

    with pytest.raises(ValueError, match="ne peut pas être invité"):
        send_account_invitation(user, invitation_request)


@pytest.mark.django_db
@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
)
def test_technician_invitation_compatibility(invitation_request, invited_user):
    from apps.accounts.services import send_technician_invitation

    user = invited_user(User.Role.TECHNICIAN)

    sent_count = send_technician_invitation(
        user,
        invitation_request,
    )

    assert sent_count == 1
    assert len(mail.outbox) == 1
