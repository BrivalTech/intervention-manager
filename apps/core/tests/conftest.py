from datetime import datetime, time, timedelta

import pytest
from django.utils import timezone

from apps.accounts.models import User
from apps.clients.models import Client
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
def dashboard_client(db):
    return Client.objects.create(name="Client dashboard")


@pytest.fixture
def today_at():
    def build(hour):
        return timezone.make_aware(
            datetime.combine(timezone.localdate(), time(hour)),
            timezone.get_current_timezone(),
        )

    return build
