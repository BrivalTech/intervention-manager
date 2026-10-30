import pytest
from django.urls import reverse

from apps.accounts.models import User


@pytest.fixture
def admin_user(django_user_model):
    return django_user_model.objects.create_user(
        username="admin_manager_tests",
        password="TestPassword123!",
        role=User.Role.ADMIN,
    )


@pytest.fixture
def manager_user(django_user_model):
    return django_user_model.objects.create_user(
        username="manager_tests",
        password="TestPassword123!",
        role=User.Role.MANAGER,
    )


@pytest.fixture
def technician_user(django_user_model):
    return django_user_model.objects.create_user(
        username="technician_manager_tests",
        password="TestPassword123!",
        role=User.Role.TECHNICIAN,
    )


# @pytest.mark.django_db
# @pytest.mark.parametrize(
#     "url_name",
#     [
#         "manager_list",
#         "manager_create",
#     ],
# )
# def test_admin_can_access_manager_pages(client, admin_user, url_name):
#     client.force_login(admin_user)
#     response = client.get(reverse(f"accounts:{url_name}"))
#
#     assert response.status_code == 200


@pytest.mark.django_db
@pytest.mark.parametrize(
    "url_name",
    [
        "manager_list",
        "manager_create",
    ],
)
@pytest.mark.parametrize(
    "user_fixture",
    ["manager_user", "technician_user"],
)
def test_non_admin_cannot_access_manager_pages(
    client,
    request,
    user_fixture,
    url_name,
):
    user = request.getfixturevalue(user_fixture)
    client.force_login(user)
    response = client.get(reverse(f"accounts:{url_name}"))

    assert response.status_code == 403


@pytest.mark.django_db
def test_anonymous_user_cannot_access_manager_list(client):
    response = client.get(reverse("accounts:manager_list"))

    assert response.status_code == 302
    assert response.url.startswith(reverse("accounts:login"))


@pytest.mark.django_db
def test_manager_update_rejects_technician_account(
    client,
    admin_user,
    technician_user,
):
    client.force_login(admin_user)
    response = client.get(
        reverse(
            "accounts:manager_update",
            args=[technician_user.public_id],
        )
    )

    assert response.status_code == 404
