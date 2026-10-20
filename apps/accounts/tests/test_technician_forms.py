import pytest

from apps.accounts.forms import TechnicianForm
from apps.accounts.models import User


@pytest.fixture
def valid_technician_data():
    return {
        "first_name": "Alice",
        "last_name": "Martin",
        "username": "alice.martin",
        "email": "alice@example.com",
    }


@pytest.mark.django_db
def test_technician_creation_form_valid(valid_technician_data):
    form = TechnicianForm(data=valid_technician_data)

    assert form.is_valid(), form.errors


@pytest.mark.django_db
def test_technician_creation_sets_role_and_unusable_password(
    valid_technician_data,
):
    form = TechnicianForm(data=valid_technician_data)

    assert form.is_valid(), form.errors

    technician = form.save()

    assert technician.role == User.Role.TECHNICIAN
    assert technician.is_active is True
    assert technician.has_usable_password() is False
    assert technician.pk is not None


@pytest.mark.django_db
def test_technician_creation_requires_email(valid_technician_data):
    valid_technician_data["email"] = ""

    print(valid_technician_data)
    form = TechnicianForm(data=valid_technician_data)

    assert not form.is_valid()
    assert "email" in form.errors


@pytest.mark.django_db
def test_technician_creation_rejects_duplicate_email(
    valid_technician_data,
    django_user_model,
):
    django_user_model.objects.create_user(
        username="existing",
        email="alice@example.com",
        role=User.Role.MANAGER,
    )

    valid_technician_data["email"] = "ALICE@example.com"
    form = TechnicianForm(data=valid_technician_data)

    assert not form.is_valid()
    assert "email" in form.errors


@pytest.mark.django_db
def test_technician_creation_rejects_duplicate_username(
    valid_technician_data,
    django_user_model,
):
    django_user_model.objects.create_user(
        username="alice.martin",
        role=User.Role.MANAGER,
    )

    form = TechnicianForm(data=valid_technician_data)

    assert not form.is_valid()
    assert "username" in form.errors


@pytest.mark.django_db
def test_technician_creation_requires_first_and_last_name(
    valid_technician_data,
):
    valid_technician_data["first_name"] = "   "
    valid_technician_data["last_name"] = "   "
    form = TechnicianForm(data=valid_technician_data)

    assert not form.is_valid()
    assert "first_name" in form.errors
    assert "last_name" in form.errors
