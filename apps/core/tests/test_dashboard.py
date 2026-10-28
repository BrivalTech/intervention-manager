from datetime import datetime, time, timedelta

import pytest
from django.utils import timezone

from apps.accounts.models import User
from apps.clients.models import Client
from apps.core.dashboard import get_dashboard_data
from apps.interventions.models import Intervention


@pytest.fixture
def dashboard_users(db):
    return {
        role: User.objects.create_user(
            username=f"dashboard-{role.lower()}",
            role=role,
        )
        for role in (
            User.Role.ADMIN,
            User.Role.MANAGER,
            User.Role.TECHNICIAN,
        )
    }


@pytest.fixture
def dashboard_client(db):
    return Client.objects.create(name="Client dashboard")


@pytest.fixture
def intervention_factory(dashboard_client, dashboard_users):
    def create(
        title,
        status=Intervention.Status.TO_PLAN,
        technician=None,
        starts_at=None,
    ):
        ends_at = starts_at + timedelta(hours=1) if starts_at is not None else None

        return Intervention.objects.create(
            title=title,
            client=dashboard_client,
            created_by=dashboard_users[User.Role.ADMIN],
            status=status,
            technician=technician,
            starts_at=starts_at,
            ends_at=ends_at,
        )

    return create


@pytest.fixture
def today_at():
    def build(hour):
        return timezone.make_aware(
            datetime.combine(timezone.localdate(), time(hour)),
            timezone.get_current_timezone(),
        )

    return build


@pytest.mark.django_db
def test_admin_dashboard_counts_interventions(
    dashboard_users,
    intervention_factory,
    today_at,
):
    intervention_factory("Sans planning")
    intervention_factory(
        "Planifiée",
        status=Intervention.Status.PLANNED,
        starts_at=today_at(9),
    )
    intervention_factory(
        "En cours",
        status=Intervention.Status.IN_PROGRESS,
        starts_at=today_at(11),
    )

    data = get_dashboard_data(dashboard_users[User.Role.ADMIN])

    assert data["to_plan_count"] == 1
    assert data["in_progress_count"] == 1
    assert data["today_count"] == 2


@pytest.mark.django_db
def test_manager_dashboard_sees_all_interventions(
    dashboard_users,
    intervention_factory,
    today_at,
):
    intervention_factory(
        "Intervention du jour",
        status=Intervention.Status.PLANNED,
        starts_at=today_at(9),
    )

    data = get_dashboard_data(dashboard_users[User.Role.MANAGER])

    assert data["today_count"] == 1
    assert len(data["today_interventions"]) == 1


@pytest.mark.django_db
def test_technician_dashboard_only_sees_assigned_interventions(
    dashboard_users,
    intervention_factory,
    today_at,
):
    technician = dashboard_users[User.Role.TECHNICIAN]
    other_technician = User.objects.create_user(
        username="other-technician",
        role=User.Role.TECHNICIAN,
    )
    assigned = intervention_factory(
        "Mon intervention",
        status=Intervention.Status.PLANNED,
        technician=technician,
        starts_at=today_at(9),
    )

    intervention_factory(
        "Intervention d'un collègue",
        status=Intervention.Status.PLANNED,
        technician=other_technician,
        starts_at=today_at(11),
    )

    data = get_dashboard_data(technician)

    assert data["today_count"] == 1
    assert list(data["today_interventions"]) == [assigned]


@pytest.mark.django_db
def test_dashboard_excludes_other_days(
    dashboard_users,
    intervention_factory,
    today_at,
):
    intervention_factory(
        "Demain",
        status=Intervention.Status.PLANNED,
        starts_at=today_at(9) + timedelta(days=1),
    )

    data = get_dashboard_data(dashboard_users[User.Role.ADMIN])

    assert data["today_count"] == 0
    assert data["today_interventions"] == []


@pytest.mark.django_db
def test_dashboard_limits_today_interventions(
    dashboard_users,
    intervention_factory,
    today_at,
):
    for index in range(7):
        intervention_factory(
            f"Intervention {index}",
            status=Intervention.Status.PLANNED,
            starts_at=today_at(8) + timedelta(minutes=index * 30),
        )

    data = get_dashboard_data(dashboard_users[User.Role.MANAGER])

    assert data["today_count"] == 7
    assert len(data["today_interventions"]) == 5


@pytest.mark.django_db
def test_dashboard_returns_no_data_for_invalid_role(django_user_model):
    user = django_user_model.objects.create_user(username="without-role")
    data = get_dashboard_data(user)

    assert data["today_count"] == 0
    assert data["today_interventions"] == []
    assert data["to_plan_count"] == 0
    assert data["in_progress_count"] == 0
