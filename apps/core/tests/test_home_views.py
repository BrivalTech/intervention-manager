import pytest
from django.urls import reverse

from apps.accounts.models import User


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("role", "expected_title", "expected_content"),
    [
        (
            "ADMIN",
            "Tableau de bord - Administration",
            "Synthèse des interventions",
        ),
        (
            "MANAGER",
            "Tableau de bord - Gestion",
            "Synthèse des interventions",
        ),
        (
            "TECHNICIAN",
            "Mes interventions",
            "Synthèse de mes interventions",
        ),
    ],
)
def test_home_displays_dashboard_for_user_role(
    client,
    django_user_model,
    role,
    expected_title,
    expected_content,
):
    user = django_user_model.objects.create_user(
        username=f"user-{role.lower()}",
        password="TestPassword123",
        role=role,
    )
    client.force_login(user)
    response = client.get(reverse("core:home"))

    assert response.status_code == 200
    assert expected_title in response.content.decode()
    assert expected_content in response.content.decode()


@pytest.mark.django_db
def test_home_displays_first_name(client, django_user_model):
    user = django_user_model.objects.create_user(
        username="alice",
        first_name="Alice",
        password="TestPassword123!",
        role=User.Role.MANAGER,
    )
    client.force_login(user)

    response = client.get(reverse("core:home"))

    assert response.status_code == 200
    assert "Bonjour," in response.content.decode()
    assert "Alice" in response.content.decode()


@pytest.mark.django_db
def test_home_uses_username_when_first_name_is_empty(client, django_user_model):
    user = django_user_model.objects.create_user(
        username="alice",
        first_name="",
        password="TestPassword123!",
        role=User.Role.MANAGER,
    )
    client.force_login(user)

    response = client.get(reverse("core:home"))

    assert response.status_code == 200
    assert "alice" in response.content.decode()


@pytest.mark.django_db
def test_home_has_unique_dashboard_title(client, django_user_model):
    user = django_user_model.objects.create_user(
        username="alice",
        password="TestPassword123!",
        role=User.Role.MANAGER,
    )

    client.force_login(user)
    response = client.get(reverse("core:home"))

    assert response.status_code == 200
    assert response.content.decode().count('id="dashboard-title"') == 1


@pytest.mark.django_db
def test_logo_links_to_home(client, django_user_model):
    user = django_user_model.objects.create_user(
        username="admin",
        password="TestPassword123!",
        role=User.Role.ADMIN,
    )
    client.force_login(user)

    response = client.get(reverse("core:home"))
    content = response.content.decode()

    assert response.status_code == 200
    assert 'class="site-brand"' in content
    assert f'href="{reverse("core:home")}"' in content


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("role", "expected"),
    [
        (User.Role.ADMIN, True),
        (User.Role.MANAGER, False),
        (User.Role.TECHNICIAN, False),
    ],
)
def test_design_system_footer_visibility(client, django_user_model, role, expected):
    user = django_user_model.objects.create_user(
        username=f"user-{role.lower()}",
        password="TestPassword123!",
        role=role,
    )

    client.force_login(user)
    response = client.get(reverse("core:home"))
    content = response.content.decode()

    design_system_link = f'href="{reverse("core:design-system")}"'
    assert (design_system_link in content) is expected
