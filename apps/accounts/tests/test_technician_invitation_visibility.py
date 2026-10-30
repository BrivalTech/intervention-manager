import pytest
from django.urls import reverse

from apps.accounts.models import User


@pytest.mark.django_db
def test_manager_cannot_see_resend_invitation_button(
    client,
    django_user_model,
):
    manager = django_user_model.objects.create_user(
        username="manager_resend",
        role=User.Role.MANAGER,
    )

    technician = django_user_model.objects.create_user(
        username="tech_pending",
        email="alice@example.com",
        role=User.Role.TECHNICIAN,
    )
    technician.set_unusable_password()
    technician.save(update_fields=["password"])

    client.force_login(manager)

    response = client.get(reverse("accounts:technician_list"))

    assert response.status_code == 200

    invitation_url = reverse(
        "accounts:technician_resend_invitation",
        args=[technician.public_id],
    )

    assert invitation_url not in response.content.decode()


@pytest.mark.django_db
def test_resend_invitation_button_hidden_after_activation(
    client,
    django_user_model,
):
    admin = django_user_model.objects.create_user(
        username="admin_activated",
        role=User.Role.ADMIN,
    )

    technician = django_user_model.objects.create_user(
        username="tech_activated",
        password="SecureTestPassword123!",
        role=User.Role.TECHNICIAN,
    )

    client.force_login(admin)

    response = client.get(reverse("accounts:technician_list"))

    invitation_url = reverse(
        "accounts:technician_resend_invitation",
        args=[technician.public_id],
    )

    assert invitation_url not in response.content.decode()
