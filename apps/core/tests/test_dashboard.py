from datetime import timedelta

import pytest

from apps.accounts.models import User
from apps.core.dashboard import get_dashboard_data
from apps.interventions.models import Intervention


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


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("role", "expected_queries"),
    [
        (User.Role.ADMIN, 4),
        (User.Role.MANAGER, 4),
        (User.Role.TECHNICIAN, 5),
    ],
)
def test_dashboard_query_count(
    dashboard_users,
    intervention_factory,
    today_at,
    django_assert_num_queries,
    role,
    expected_queries,
):
    user = dashboard_users[role]
    intervention_factory(
        "Intervention du jour",
        status=Intervention.Status.PLANNED,
        technician=(user if role == User.Role.TECHNICIAN else None),
        starts_at=today_at(9),
    )

    with django_assert_num_queries(expected_queries):
        data = get_dashboard_data(user)

    assert data["today_count"] == 1


@pytest.mark.django_db
def test_dashboard_interventions_preload_relations(
    dashboard_users,
    intervention_factory,
    today_at,
    django_assert_num_queries,
):
    intervention_factory(
        "Intervention planifiée",
        status=Intervention.Status.PLANNED,
        technician=dashboard_users[User.Role.TECHNICIAN],
        starts_at=today_at(9),
    )
    data = get_dashboard_data(dashboard_users[User.Role.ADMIN])

    with django_assert_num_queries(0):
        for intervention in data["today_interventions"]:
            assert intervention.client.name
            assert intervention.technician.username


@pytest.mark.django_db
def test_inactive_user_has_no_dashboard_data(dashboard_users):
    user = dashboard_users[User.Role.TECHNICIAN]
    user.is_active = False
    user.save(update_fields=["is_active"])

    data = get_dashboard_data(user)

    assert data["today_count"] == 0
    assert data["today_interventions"] == []
    assert data["upcoming_count"] == 0
