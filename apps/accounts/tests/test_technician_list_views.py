import pytest
from django.urls import reverse

from apps.accounts.models import User


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("role", "expected_status"),
    [
        (User.Role.ADMIN, 200),
        (User.Role.MANAGER, 200),
        (User.Role.TECHNICIAN, 403),
    ],
)
def test_technician_list_permissions(
    client,
    django_user_model,
    role,
    expected_status,
):
    user = django_user_model.objects.create_user(
        username=f"user-{role.lower()}",
        password="TestPassword123!",
        role=role,
    )

    client.force_login(user)
    response = client.get(reverse("accounts:technician_list"))

    assert response.status_code == expected_status


@pytest.mark.django_db
def test_technician_list_requires_authentication(client):
    response = client.get(reverse("accounts:technician_list"))

    assert response.status_code == 302
    assert response.url.startswith(reverse("accounts:login"))


@pytest.mark.django_db
def test_technician_list_only_contains_technicians(client, django_user_model):
    admin = django_user_model.objects.create_user(
        username="admin",
        role=User.Role.ADMIN,
    )

    client.force_login(admin)
    django_user_model.objects.create_user(
        username="technician-one",
        role=User.Role.TECHNICIAN,
    )
    django_user_model.objects.create_user(
        username="manager-one",
        role=User.Role.MANAGER,
    )

    response = client.get(reverse("accounts:technician_list"))

    assert response.status_code == 200

    usernames = [user.username for user in response.context["technicians"]]

    assert usernames == ["technician-one"]


@pytest.mark.django_db
def test_technician_list_search(client, django_user_model):
    admin = django_user_model.objects.create_user(
        username="admin",
        role=User.Role.ADMIN,
    )

    client.force_login(admin)

    django_user_model.objects.create_user(
        username="tech-alice",
        first_name="Alice",
        role=User.Role.TECHNICIAN,
    )
    django_user_model.objects.create_user(
        username="tech-bob",
        first_name="Bob",
        role=User.Role.TECHNICIAN,
    )

    response = client.get(reverse("accounts:technician_list"), {"q": "Alice"})

    assert response.status_code == 200
    assert response.context["result_count"] == 1
    assert response.context["technicians"][0].username == "tech-alice"


@pytest.mark.django_db
def test_technician_list_filter_inactive(client, django_user_model):
    admin = django_user_model.objects.create_user(
        username="admin",
        role=User.Role.ADMIN,
    )

    client.force_login(admin)

    django_user_model.objects.create_user(
        username="tech-active",
        role=User.Role.TECHNICIAN,
    )
    django_user_model.objects.create_user(
        username="tech-inactive",
        role=User.Role.TECHNICIAN,
        is_active=False,
    )

    response = client.get(
        reverse("accounts:technician_list"),
        {"status": "inactive"},
    )

    assert response.status_code == 200
    assert response.context["result_count"] == 1
    assert response.context["technicians"][0].username == "tech-inactive"


@pytest.mark.django_db
def test_technician_list_pagination(client, django_user_model):
    admin = django_user_model.objects.create_user(
        username="admin",
        role=User.Role.ADMIN,
    )

    client.force_login(admin)

    for index in range(15):
        django_user_model.objects.create_user(
            username=f"technician-{index:02d}",
            role=User.Role.TECHNICIAN,
        )

    response = client.get(reverse("accounts:technician_list"), {"page": "2"})

    assert response.status_code == 200
    assert response.context["result_count"] == 15
    assert response.context["page_obj"].number == 2
    assert len(response.context["technicians"]) == 5
