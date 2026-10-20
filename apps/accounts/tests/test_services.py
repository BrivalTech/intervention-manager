import re

import pytest
from django.core import mail
from django.test import RequestFactory, override_settings
from django.urls import reverse

from apps.accounts.models import User
from apps.accounts.services import send_technician_invitation


@pytest.mark.django_db
@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    DEFAULT_FROM_EMAIL="no-reply@example.com",
)
def test_send_technician_invitation(django_user_model):
    technician = django_user_model.objects.create_user(
        username="alice",
        first_name="Alice",
        email="alice@example.com",
        role=User.Role.TECHNICIAN,
    )
    technician.set_unusable_password()
    technician.save(update_fields=["password"])
    request = RequestFactory().get("/", HTTP_HOST="testserver")
    sent_count = send_technician_invitation(technician, request)

    assert sent_count == 1
    assert len(mail.outbox) == 1

    email = mail.outbox[0]

    assert email.to == ["alice@example.com"]
    assert "Invitation" in email.subject
    assert "/accounts/invitation/" in email.body
    assert "Alice" in email.body


@pytest.mark.django_db
@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
)
def test_invitation_rejected_when_password_exists(django_user_model):
    technician = django_user_model.objects.create_user(
        username="alice",
        password="TestPassword123!",
        email="alice@example.com",
        role=User.Role.TECHNICIAN,
    )

    request = RequestFactory().get("/")

    with pytest.raises(ValueError):
        send_technician_invitation(technician, request)

    assert len(mail.outbox) == 0


@pytest.mark.django_db
@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    DEFAULT_FROM_EMAIL="no-reply@example.com",
)
def test_technician_can_set_password_from_invitation(
    client,
    django_user_model,
):
    technician = django_user_model.objects.create_user(
        username="technician_activation",
        first_name="Alice",
        email="alice@example.com",
        role=User.Role.TECHNICIAN,
    )
    technician.set_unusable_password()
    technician.save(update_fields=["password"])

    request = RequestFactory().get("/", HTTP_HOST="testserver")
    send_technician_invitation(technician, request)
    invitation_url = re.search(
        r"https?://[^\s]+/accounts/invitation/[^\s]+",
        mail.outbox[0].body,
    ).group(0)

    from urllib.parse import urlsplit

    invitation_path = urlsplit(invitation_url).path
    response = client.get(invitation_path)

    # Django redirects to a URL containing "set-password"
    # after validating the token.
    assert response.status_code == 302

    password_form_url = response.url

    response = client.post(
        password_form_url,
        {
            "new_password1": "SecureTestPassword123!",
            "new_password2": "SecureTestPassword123!",
        },
    )

    assert response.status_code == 302
    assert response.url == reverse("accounts:login")

    technician.refresh_from_db()

    assert technician.has_usable_password() is True
    assert technician.check_password("SecureTestPassword123!")

    response = client.get(invitation_path, follow=True)

    assert response.status_code == 200
    assert response.context["validlink"] is False
