import pytest

from apps.accounts.forms import TechnicianUpdateForm
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
def test_update_technician_information(technician):
    original_password = technician.password

    form = TechnicianUpdateForm(
        data={
            "first_name": "Alicia",
            "last_name": "Martin",
            "username": "alicia",
            "email": "alicia@example.com",
        },
        instance=technician,
    )

    assert form.is_valid(), form.errors

    form.save()
    technician.refresh_from_db()

    assert technician.first_name == "Alicia"
    assert technician.username == "alicia"
    assert technician.email == "alicia@example.com"
    assert technician.role == User.Role.TECHNICIAN
    assert technician.password == original_password


@pytest.mark.django_db
def test_update_technician_with_same_email(technician):
    form = TechnicianUpdateForm(
        data={
            "first_name": "Alice",
            "last_name": "Martin",
            "username": "alice",
            "email": "alice@example.com",
        },
        instance=technician,
    )

    assert form.is_valid(), form.errors


@pytest.mark.django_db
def test_update_technician_rejects_duplicate_email(
    technician,
    django_user_model,
):
    django_user_model.objects.create_user(
        username="bob",
        email="bob@example.com",
        role=User.Role.TECHNICIAN,
    )

    form = TechnicianUpdateForm(
        data={
            "first_name": "Alice",
            "last_name": "Martin",
            "username": "alice",
            "email": "bob@example.com",
        },
        instance=technician,
    )

    assert not form.is_valid()
    assert "email" in form.errors
