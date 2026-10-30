from datetime import datetime, time, timedelta
from urllib.parse import parse_qs, urlsplit

import pytest
from django.urls import reverse
from django.utils import timezone

from apps.accounts.models import User
from apps.clients.models import Client
from apps.core.dashboard import get_dashboard_data
from apps.interventions.models import Intervention


@pytest.mark.django_db
def test_design_system_page(client):
    response = client.get(reverse("core:design-system"))

    assert response.status_code == 302
    assert response.url.startswith(reverse("accounts:login"))


@pytest.mark.django_db
@pytest.mark.parametrize(
    "role",
    [User.Role.MANAGER, User.Role.TECHNICIAN],
)
def test_design_system_restricted_to_admin(client, django_user_model, role):
    user = django_user_model.objects.create_user(
        username=f"user-{role.lower()}",
        password="TestPassword123!",
        role=role,
    )

    client.force_login(user)
    response = client.get(reverse("core:design-system"))

    assert response.status_code == 403


def test_home_requires_authentication(client):
    response = client.get(reverse("core:home"))

    assert response.status_code == 302
    assert response.url == "/accounts/login/?next=/"


@pytest.mark.django_db
def test_home_accessible_to_authenticated_user(client, django_user_model):
    user = django_user_model.objects.create_user(
        username="testUser",
        password="TestPassword123!",
    )
    client.force_login(user)
    response = client.get(reverse("core:home"))

    assert response.status_code == 200
    assert "home.html" in [t.name for t in response.templates]


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
def test_home_handles_user_without_role(client, django_user_model):
    user = django_user_model.objects.create_user(
        username="user-whitout-role",
        password="TestPassword123",
    )
    client.force_login(user)
    response = client.get(reverse("core:home"))

    assert response.status_code == 200
    assert "Aucun rôle valide" in response.content.decode()


def test_home_redirects_anonymous_user_to_login(client):
    home_url = reverse("core:home")
    login_url = reverse("accounts:login")

    response = client.get(home_url)
    assert response.status_code == 302

    redirect = urlsplit(response.url)
    assert redirect.path == login_url
    assert parse_qs(redirect.query) == {"next": [home_url]}


@pytest.mark.django_db
@pytest.mark.parametrize(
    "role",
    [
        User.Role.ADMIN,
        User.Role.MANAGER,
        User.Role.TECHNICIAN,
    ],
)
def test_authenticated_users_access_home(
    client,
    django_user_model,
    role,
):
    user = django_user_model.objects.create_user(
        username=f"user-{role.lower()}",
        password="TestPassword123",
        role=role,
    )
    client.force_login(user)
    response = client.get(reverse("core:home"))

    assert response.status_code == 200
    assert response.wsgi_request.user.is_authenticated


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("username", "password"),
    [
        ("unknown_user", "TestPassword123!"),
        ("testuser", "WrongPassword123!"),
        ("", ""),
        ("testuser", ""),
        ("", "TestPassword123!"),
    ],
)
def test_login_rejects_invalid_credentials(
    client,
    django_user_model,
    username,
    password,
):
    django_user_model.objects.create_user(
        username="testuser",
        password="TestPassword123!",
        role=User.Role.MANAGER,
    )

    response = client.post(
        reverse("accounts:login"),
        {"username": username, "password": password},
    )

    assert response.status_code == 200
    assert not response.wsgi_request.user.is_authenticated
    assert "_auth_user_id" not in client.session
    assert response.context["form"].errors


@pytest.mark.django_db
def test_login_rejects_inactive_user(client, django_user_model):
    django_user_model.objects.create_user(
        username="inactive_user",
        password="TestPassword123!",
        role=User.Role.TECHNICIAN,
        is_active=False,
    )

    response = client.post(
        reverse("accounts:login"),
        {"username": "inactive_user", "password": "TestPassword123!"},
    )

    assert response.status_code == 200
    assert not response.wsgi_request.user.is_authenticated
    assert "_auth_user_id" not in client.session
    assert response.context["form"].errors


@pytest.mark.django_db
def test_invalid_login_displays_accessible_error(client, django_user_model):
    django_user_model.objects.create_user(
        username="testuser",
        password="TestPassword123!",
        role=User.Role.MANAGER,
    )

    response = client.post(
        reverse("accounts:login"),
        {"username": "testuser", "password": "WrongPassword123!"},
    )

    assert response.status_code == 200

    content = response.content.decode()
    assert 'class="message message--error"' in content
    assert 'role="alert"' in content
    assert "Connexion impossible" in content


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


@pytest.mark.django_db
def test_navigation_uses_post_logout(client, django_user_model):
    user = django_user_model.objects.create_user(
        username="admin",
        password="TestPassword123!",
        role=User.Role.ADMIN,
    )

    client.force_login(user)
    response = client.get(reverse("core:home"))
    content = response.content.decode()

    assert response.status_code == 200
    assert 'method="post"' in content
    assert f'action="{reverse("accounts:logout")}"' in content


@pytest.mark.django_db
def test_home_provides_dashboard_data(client, django_user_model):
    user = django_user_model.objects.create_user(
        username="dashboard-manager",
        role=User.Role.MANAGER,
    )

    client.force_login(user)
    response = client.get(reverse("core:home"))

    assert response.status_code == 200
    assert "dashboard" in response.context
    assert response.context["dashboard"]["today_count"] == 0
    assert response.context["dashboard"]["today_interventions"] == []


@pytest.mark.django_db
def test_admin_dashboard_displays_operational_indicators(
    client,
    django_user_model,
):
    admin = django_user_model.objects.create_user(
        username="dashboard-admin",
        role=User.Role.ADMIN,
    )

    client.force_login(admin)
    response = client.get(reverse("core:home"))

    assert response.status_code == 200

    content = response.content.decode()

    assert "Tableau de bord - Administration" in content
    assert "Interventions du jour" in content
    assert "À planifier" in content
    assert "En cours" in content


@pytest.mark.django_db
def test_admin_dashboard_displays_management_links(client, django_user_model):
    admin = django_user_model.objects.create_user(
        username="dashboard-admin-links",
        role=User.Role.ADMIN,
    )

    client.force_login(admin)
    response = client.get(reverse("core:home"))
    content = response.content.decode()

    assert response.status_code == 200

    expected_urls = [
        reverse("interventions:list"),
        reverse("clients:list"),
        reverse("accounts:technician_list"),
        reverse("accounts:manager_list"),
    ]

    for url in expected_urls:
        assert f'href="{url}"' in content


@pytest.mark.django_db
@pytest.mark.parametrize(
    "role",
    [
        User.Role.MANAGER,
        User.Role.TECHNICIAN,
    ],
)
def test_admin_dashboard_is_not_displayed_to_other_roles(
    client,
    django_user_model,
    role,
):
    user = django_user_model.objects.create_user(
        username=f"dashboard-{role.lower()}",
        role=role,
    )

    client.force_login(user)
    response = client.get(reverse("core:home"))

    assert response.status_code == 200
    assert "Tableau de bord - Administration" not in response.content.decode()


@pytest.mark.django_db
def test_manager_dashboard_displays_indicators(client, django_user_model):
    manager = django_user_model.objects.create_user(
        username="manager-dashboard-indicators",
        role=User.Role.MANAGER,
    )

    client.force_login(manager)
    response = client.get(reverse("core:home"))
    content = response.content.decode()

    assert response.status_code == 200
    assert "Tableau de bord - Gestion" in content
    assert "Interventions du jour" in content
    assert "À planifier" in content
    assert "En cours" in content


@pytest.mark.django_db
def test_manager_dashboard_displays_operational_links(
    client,
    django_user_model,
):
    manager = django_user_model.objects.create_user(
        username="manager-dashboard-links",
        role=User.Role.MANAGER,
    )

    client.force_login(manager)
    response = client.get(reverse("core:home"))
    content = response.content.decode()

    assert response.status_code == 200
    assert f'href="{reverse("interventions:list")}"' in content
    assert f'href="{reverse("clients:list")}"' in content
    assert f'href="{reverse("accounts:manager_list")}"' not in content
    assert f'href="{reverse("accounts:technician_list")}"' in content


@pytest.mark.django_db
def test_manager_dashboard_is_not_displayed_to_other_roles(
    client,
    django_user_model,
):
    for role in (User.Role.ADMIN, User.Role.TECHNICIAN):
        user = django_user_model.objects.create_user(
            username=f"manager-dashboard-check-{role.lower()}",
            role=role,
        )

        client.force_login(user)
        response = client.get(reverse("core:home"))

        assert response.status_code == 200
        assert "Tableau de bord - Gestion" not in response.content.decode()


@pytest.mark.django_db
def test_manager_dashboard_displays_today_intervention(
    client,
    django_user_model,
):
    manager = django_user_model.objects.create_user(
        username="manager-today",
        role=User.Role.MANAGER,
    )
    customer = Client.objects.create(name="Client planning")
    starts_at = timezone.make_aware(
        datetime.combine(timezone.localdate(), time(9)),
        timezone.get_current_timezone(),
    )
    intervention = Intervention.objects.create(
        title="Maintenance réseau",
        client=customer,
        created_by=manager,
        status=Intervention.Status.PLANNED,
        starts_at=starts_at,
        ends_at=starts_at + timedelta(hours=1),
    )

    client.force_login(manager)
    response = client.get(reverse("core:home"))

    assert response.status_code == 200
    assert intervention.title in response.content.decode()
    assert customer.name in response.content.decode()
    assert "09:00" in response.content.decode()
    assert (
        f'href="{reverse("interventions:detail", args=[intervention.public_id])}"'
    ) in (response.content.decode())


@pytest.mark.django_db
def test_technician_dashboard_counts_upcoming_interventions(
    dashboard_users,
    intervention_factory,
    today_at,
):
    technician = dashboard_users[User.Role.TECHNICIAN]
    other_technician = User.objects.create_user(
        username="technician-colleague",
        role=User.Role.TECHNICIAN,
    )
    intervention_factory(
        "Intervention demain",
        status=Intervention.Status.PLANNED,
        technician=technician,
        starts_at=today_at(9) + timedelta(days=1),
    )
    intervention_factory(
        "Intervention dans trois jours",
        status=Intervention.Status.PLANNED,
        technician=technician,
        starts_at=today_at(9) + timedelta(days=3),
    )
    intervention_factory(
        "Intervention aujourd'hui",
        status=Intervention.Status.PLANNED,
        technician=technician,
        starts_at=today_at(11),
    )
    intervention_factory(
        "Intervention d'un collègue",
        status=Intervention.Status.PLANNED,
        technician=other_technician,
        starts_at=today_at(14) + timedelta(days=1),
    )
    intervention_factory(
        "Intervention annulée",
        status=Intervention.Status.CANCELLED,
        technician=technician,
        starts_at=today_at(16) + timedelta(days=1),
    )

    data = get_dashboard_data(technician)

    assert data["upcoming_count"] == 2
    assert data["today_count"] == 1


@pytest.mark.django_db
def test_technician_dashboard_counts_only_own_in_progress(
    dashboard_users,
    intervention_factory,
    today_at,
):
    technician = dashboard_users[User.Role.TECHNICIAN]
    colleague = User.objects.create_user(
        username="another-technician",
        role=User.Role.TECHNICIAN,
    )
    intervention_factory(
        "Mon intervention en cours",
        status=Intervention.Status.IN_PROGRESS,
        technician=technician,
        starts_at=today_at(9),
    )
    intervention_factory(
        "Intervention du collègue",
        status=Intervention.Status.IN_PROGRESS,
        technician=colleague,
        starts_at=today_at(11),
    )

    data = get_dashboard_data(technician)

    assert data["in_progress_count"] == 1
    assert data["today_count"] == 1


@pytest.mark.django_db
def test_technician_dashboard_hides_colleague_interventions(
    client,
    django_user_model,
):
    technician = django_user_model.objects.create_user(
        username="dashboard-technician",
        role=User.Role.TECHNICIAN,
    )
    colleague = django_user_model.objects.create_user(
        username="dashboard-colleague",
        role=User.Role.TECHNICIAN,
    )
    customer = Client.objects.create(name="Client technicien")
    starts_at = timezone.make_aware(
        datetime.combine(timezone.localdate(), time(9)),
        timezone.get_current_timezone(),
    )
    own_intervention = Intervention.objects.create(
        title="Mon dépannage",
        client=customer,
        created_by=technician,
        technician=technician,
        status=Intervention.Status.PLANNED,
        starts_at=starts_at,
        ends_at=starts_at + timedelta(hours=1),
    )
    Intervention.objects.create(
        title="Intervention confidentielle du collègue",
        client=customer,
        created_by=technician,
        technician=colleague,
        status=Intervention.Status.PLANNED,
        starts_at=starts_at,
        ends_at=starts_at + timedelta(hours=1),
    )

    client.force_login(technician)
    response = client.get(reverse("core:home"))
    content = response.content.decode()

    assert response.status_code == 200
    assert own_intervention.title in content
    assert "Intervention confidentielle du collègue" not in content
    assert "Tableau de bord - Administration" not in content
    assert "Tableau de bord - Gestion" not in content


@pytest.mark.django_db
@pytest.mark.parametrize(
    "role",
    [
        User.Role.ADMIN,
        User.Role.MANAGER,
        User.Role.TECHNICIAN,
    ],
)
def test_dashboard_has_single_main_heading(
    client,
    django_user_model,
    role,
):
    user = django_user_model.objects.create_user(
        username=f"heading-{role.lower()}",
        role=role,
    )

    client.force_login(user)
    response = client.get(reverse("core:home"))

    assert response.status_code == 200
    assert response.content.decode().count("<h1") == 1


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("role", "prefix"),
    [
        (User.Role.ADMIN, "admin"),
        (User.Role.MANAGER, "manager"),
        (User.Role.TECHNICIAN, "technician"),
    ],
)
def test_dashboard_renders_shared_components(
    client,
    django_user_model,
    role,
    prefix,
):
    user = django_user_model.objects.create_user(
        username=f"shared-components-{role.lower()}",
        role=role,
    )

    client.force_login(user)
    response = client.get(reverse("core:home"))

    assert response.status_code == 200

    content = response.content.decode()
    assert f'id="{prefix}-metrics-title"' in content
    assert f'id="{prefix}-today-title"' in content
    assert f'id="{prefix}-links-title"' in content
    assert content.count('class="dashboard-metrics"') == 1
    assert content.count('class="dashboard-shortcuts"') == 1
