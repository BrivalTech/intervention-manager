from datetime import datetime
from zoneinfo import ZoneInfo

import pytest
from django.core.exceptions import ValidationError

from apps.accounts.models import User
from apps.clients.models import Client
from apps.interventions.models import Intervention


@pytest.mark.django_db
def test_intervention_can_be_created_for_active_client(intervention_author):
    client = Client.objects.create(name="Entreprise Test")
    starts_at = datetime(2026, 11, 10, 9, tzinfo=ZoneInfo("Europe/Paris"))
    ends_at = datetime(2026, 11, 10, 11, tzinfo=ZoneInfo("Europe/Paris"))
    intervention = Intervention.objects.create(
        created_by=intervention_author,
        client=client,
        title="Maintenance du poste de travail",
        starts_at=starts_at,
        ends_at=ends_at,
    )

    assert intervention.client == client
    assert intervention.title == "Maintenance du poste de travail"
    assert intervention.starts_at == starts_at
    assert intervention.ends_at == ends_at


@pytest.mark.django_db
def test_intervention_is_to_plan_by_default(intervention_author):
    client = Client.objects.create(name="Entreprise Test")
    intervention = Intervention.objects.create(
        created_by=intervention_author,
        client=client,
        title="Maintenance du poste de travail",
    )

    assert intervention.status == Intervention.Status.TO_PLAN


@pytest.mark.django_db
def test_intervention_can_be_created_without_schedule(intervention_author):
    client = Client.objects.create(name="Entreprise Test")
    intervention = Intervention.objects.create(
        created_by=intervention_author,
        client=client,
        title="Maintenance du poste de travail",
        description="Vérifier le poste utilisateur.",
    )

    assert intervention.description == "Vérifier le poste utilisateur."
    assert intervention.starts_at is None


@pytest.mark.django_db
def test_intervention_title_is_required(intervention_author):
    client = Client.objects.create(name="Entreprise Test")
    intervention = Intervention.objects.create(
        created_by=intervention_author,
        client=client,
        title="",
    )

    with pytest.raises(ValidationError):
        intervention.full_clean()


@pytest.mark.django_db
def test_intervention_client_is_required(intervention_author):
    intervention = Intervention(
        created_by=intervention_author,
        title="Maintenance du poste de travail",
    )

    with pytest.raises(ValidationError):
        intervention.full_clean()


@pytest.mark.django_db
def test_intervention_cannot_be_created_for_archived_client(intervention_author):
    client = Client.objects.create(name="Entreprise Test", is_active=False)
    intervention = Intervention.objects.create(
        created_by=intervention_author,
        client=client,
        title="Maintenance du poste de travail",
    )

    with pytest.raises(ValidationError):
        intervention.full_clean()


@pytest.mark.django_db
def test_intervention_string_representation_is_title(intervention_author):
    client = Client.objects.create(name="Entreprise Test")
    intervention = Intervention.objects.create(
        created_by=intervention_author,
        client=client,
        title="Maintenance du poste de travail",
    )

    assert str(intervention) == "Maintenance du poste de travail"


@pytest.mark.django_db
def test_intervention_status_must_be_valid(intervention_author):
    client = Client.objects.create(name="Entreprise Test")
    intervention = Intervention.objects.create(
        created_by=intervention_author,
        client=client,
        title="Maintenance du poste de travail",
        status="INVALID",
    )

    with pytest.raises(ValidationError):
        intervention.full_clean()


@pytest.mark.parametrize(
    "status",
    [
        Intervention.Status.TO_PLAN,
        Intervention.Status.PLANNED,
        Intervention.Status.IN_PROGRESS,
        Intervention.Status.COMPLETED,
        Intervention.Status.CANCELLED,
    ],
)
@pytest.mark.django_db
def test_intervention_accepts_valid_status(status, intervention_author):
    client = Client.objects.create(name="Entreprise Test")
    starts_at = datetime(2026, 11, 10, 9, tzinfo=ZoneInfo("Europe/Paris"))
    ends_at = datetime(2026, 11, 10, 11, tzinfo=ZoneInfo("Europe/Paris"))
    intervention = Intervention.objects.create(
        created_by=intervention_author,
        client=client,
        title="Maintenance du poste de travail",
        starts_at=starts_at if status != Intervention.Status.TO_PLAN else None,
        ends_at=ends_at if status != Intervention.Status.TO_PLAN else None,
        status=(
            Intervention.Status.PLANNED
            if status != Intervention.Status.TO_PLAN
            else Intervention.Status.TO_PLAN
        ),
    )

    if status == Intervention.Status.IN_PROGRESS:
        intervention.start()
    elif status == Intervention.Status.COMPLETED:
        intervention.start()
        intervention.complete("Intervention terminée et vérifiée.")
    elif status == Intervention.Status.CANCELLED:
        intervention.cancel()

    intervention.refresh_from_db()

    assert intervention.status == status
    intervention.full_clean()


@pytest.mark.django_db
def test_planned_intervention_can_be_started(intervention_author):
    client = Client.objects.create(name="Entreprise Test")
    intervention = Intervention.objects.create(
        created_by=intervention_author,
        client=client,
        title="Maintenance du poste de travail",
        status=Intervention.Status.PLANNED,
        starts_at=datetime(2026, 11, 10, 9, tzinfo=ZoneInfo("Europe/Paris")),
        ends_at=datetime(2026, 11, 10, 11, tzinfo=ZoneInfo("Europe/Paris")),
    )

    intervention.start()
    intervention.refresh_from_db()

    assert intervention.status == Intervention.Status.IN_PROGRESS


@pytest.mark.django_db
def test_in_progress_intervention_can_be_completed(intervention_author):
    client = Client.objects.create(name="Entreprise Test")
    intervention = Intervention.objects.create(
        created_by=intervention_author,
        client=client,
        title="Maintenance du poste de travail",
        status=Intervention.Status.IN_PROGRESS,
    )

    intervention.complete("Intervention terminée et vérifiée.")
    intervention.refresh_from_db()

    assert intervention.status == Intervention.Status.COMPLETED


@pytest.mark.parametrize(
    "status",
    [
        Intervention.Status.TO_PLAN,
        Intervention.Status.PLANNED,
        Intervention.Status.IN_PROGRESS,
    ],
)
@pytest.mark.django_db
def test_intervention_can_be_cancelled(status, intervention_author):
    client = Client.objects.create(name="Entreprise Test")
    intervention = Intervention.objects.create(
        created_by=intervention_author,
        client=client,
        title="Maintenance du poste de travail",
        status=status,
    )

    intervention.cancel()
    intervention.refresh_from_db()

    assert intervention.status == Intervention.Status.CANCELLED


@pytest.mark.parametrize(
    "status",
    [
        Intervention.Status.TO_PLAN,
        Intervention.Status.IN_PROGRESS,
        Intervention.Status.COMPLETED,
        Intervention.Status.CANCELLED,
    ],
)
@pytest.mark.django_db
def test_only_planned_intervention_can_be_started(status, intervention_author):
    client = Client.objects.create(name="Entreprise Test")
    intervention = Intervention.objects.create(
        created_by=intervention_author,
        client=client,
        title="Maintenance du poste de travail",
        status=status,
    )

    with pytest.raises(ValidationError):
        intervention.start()


@pytest.mark.parametrize(
    "status",
    [
        Intervention.Status.PLANNED,
        Intervention.Status.COMPLETED,
        Intervention.Status.CANCELLED,
    ],
)
@pytest.mark.django_db
def test_only_in_progress_intervention_can_be_completed(status, intervention_author):
    client = Client.objects.create(name="Entreprise Test")
    intervention = Intervention.objects.create(
        created_by=intervention_author,
        client=client,
        title="Maintenance du poste de travail",
        status=status,
    )

    with pytest.raises(ValidationError):
        intervention.complete("Intervention terminée et vérifiée.")


@pytest.mark.parametrize(
    "initial_status",
    [
        Intervention.Status.COMPLETED,
        Intervention.Status.CANCELLED,
    ],
)
@pytest.mark.django_db
def test_completed_or_cancelled_intervention_cannot_be_cancelled(
    initial_status, intervention_author
):
    client = Client.objects.create(name="Entreprise Test")
    intervention = Intervention.objects.create(
        created_by=intervention_author,
        client=client,
        title="Maintenance du poste de travail",
        status=initial_status,
    )

    with pytest.raises(ValidationError):
        intervention.cancel()


@pytest.mark.django_db
def test_intervention_can_be_created_without_technician(intervention_author):
    client = Client.objects.create(name="Entreprise Test")
    intervention = Intervention.objects.create(
        created_by=intervention_author,
        client=client,
        title="Maintenance du poste de travail",
    )

    assert intervention.technician is None


@pytest.mark.django_db
def test_technician_can_be_assigned_to_an_intervention(intervention_author):
    client = Client.objects.create(name="Entreprise Test")
    technician = User.objects.create_user(
        username="technician",
        password="test-password",
        role=User.Role.TECHNICIAN,
    )
    intervention = Intervention.objects.create(
        created_by=intervention_author,
        client=client,
        title="Maintenance du poste de travail",
        technician=technician,
    )

    assert intervention.technician == technician


@pytest.mark.parametrize(
    "role",
    [
        User.Role.ADMIN,
        User.Role.MANAGER,
    ],
)
@pytest.mark.django_db
def test_non_technician_cannot_be_assigned_to_an_intervention(
    role, intervention_author
):
    client = Client.objects.create(name="Entreprise Test")
    user = User.objects.create_user(
        username=f"user-{role.lower()}",
        password="test-password",
        role=role,
    )
    intervention = Intervention.objects.create(
        created_by=intervention_author,
        client=client,
        title="Maintenance du poste de travail",
        technician=user,
    )

    with pytest.raises(ValidationError):
        intervention.full_clean()


@pytest.mark.django_db
def test_technician_can_ne_assigned_after_intervention_created(intervention_author):
    client = Client.objects.create(name="Entreprise Test")
    technician = User.objects.create_user(
        username="technician",
        password="test-password",
        role=User.Role.TECHNICIAN,
    )
    intervention = Intervention.objects.create(
        created_by=intervention_author,
        client=client,
        title="Maintenance du poste de travail",
    )

    intervention.assign_technician(technician)
    intervention.refresh_from_db()

    assert intervention.technician == technician


@pytest.mark.parametrize(
    "role",
    [
        User.Role.ADMIN,
        User.Role.MANAGER,
    ],
)
@pytest.mark.django_db
def test_non_technician_cannot_be_assigned_after_intervention_created(
    role, intervention_author
):
    client = Client.objects.create(name="Entreprise Test")
    user = User.objects.create_user(
        username=f"user-{role.lower()}",
        password="test-password",
        role=role,
    )
    intervention = Intervention.objects.create(
        created_by=intervention_author,
        client=client,
        title="Maintenance du poste de travail",
        technician=user,
    )

    with pytest.raises(ValidationError):
        intervention.assign_technician(user)


@pytest.mark.parametrize(
    "status",
    [
        Intervention.Status.PLANNED,
        Intervention.Status.IN_PROGRESS,
    ],
)
@pytest.mark.django_db
def test_technician_can_be_unassigned_from_active_intervention(
    status, intervention_author
):
    client = Client.objects.create(name="Entreprise Test")
    technician = User.objects.create_user(
        username=f"technician-{status.lower()}",
        password="test-password",
        role=User.Role.TECHNICIAN,
    )
    intervention = Intervention.objects.create(
        created_by=intervention_author,
        client=client,
        title="Maintenance du poste de travail",
        technician=technician,
        status=status,
    )

    intervention.unassign_technician()
    intervention.refresh_from_db()

    assert intervention.technician is None


@pytest.mark.parametrize(
    "status",
    [
        Intervention.Status.COMPLETED,
        Intervention.Status.CANCELLED,
    ],
)
@pytest.mark.django_db
def test_technician_cannot_be_unassigned_from_final_intervention(
    status, intervention_author
):
    client = Client.objects.create(name="Entreprise Test")
    technician = User.objects.create_user(
        username=f"technician-{status.lower()}",
        password="test-password",
        role=User.Role.TECHNICIAN,
    )
    intervention = Intervention.objects.create(
        created_by=intervention_author,
        client=client,
        title="Maintenance du poste de travail",
        technician=technician,
        status=status,
    )

    with pytest.raises(ValidationError):
        intervention.unassign_technician()


@pytest.mark.parametrize(
    "status",
    [
        Intervention.Status.COMPLETED,
        Intervention.Status.CANCELLED,
    ],
)
@pytest.mark.django_db
def test_technician_cannot_be_assigned_to_finale_intervention(
    status, intervention_author
):
    client = Client.objects.create(name="Entreprise Test")
    technician = User.objects.create_user(
        username=f"technician-{status.lower()}",
        password="test-password",
        role=User.Role.TECHNICIAN,
    )
    intervention = Intervention.objects.create(
        created_by=intervention_author,
        client=client,
        title="Maintenance du poste de travail",
        technician=technician,
        status=status,
    )

    with pytest.raises(ValidationError):
        intervention.assign_technician(technician)


@pytest.mark.django_db
def test_technician_can_be_reassigned_on_active_intervention(intervention_author):
    client = Client.objects.create(name="Entreprise Test")
    first_technician = User.objects.create_user(
        username="first-technician",
        password="test-password",
        role=User.Role.TECHNICIAN,
    )
    second_technician = User.objects.create_user(
        username="second-technician",
        password="test-password",
        role=User.Role.TECHNICIAN,
    )
    intervention = Intervention.objects.create(
        created_by=intervention_author,
        client=client,
        title="Maintenance du poste de travail",
        technician=first_technician,
    )

    intervention.assign_technician(second_technician)
    intervention.refresh_from_db()

    assert intervention.technician == second_technician


@pytest.mark.django_db
def test_intervention_without_technician_can_be_unassigned(intervention_author):
    client = Client.objects.create(name="Entreprise Test")
    intervention = Intervention.objects.create(
        created_by=intervention_author,
        client=client,
        title="Maintenance du poste de travail",
    )

    intervention.unassign_technician()
    intervention.refresh_from_db()

    assert intervention.technician is None


@pytest.mark.parametrize(
    ("starts_at", "ends_at", "is_valid"),
    [
        (None, None, True),
        (
            datetime(2026, 11, 10, 9, tzinfo=ZoneInfo("Europe/Paris")),
            datetime(2026, 11, 10, 11, tzinfo=ZoneInfo("Europe/Paris")),
            True,
        ),
        (
            datetime(2026, 11, 10, 9, tzinfo=ZoneInfo("Europe/Paris")),
            None,
            False,
        ),
        (
            None,
            datetime(2026, 11, 10, 11, tzinfo=ZoneInfo("Europe/Paris")),
            False,
        ),
        (
            datetime(2026, 11, 10, 9, tzinfo=ZoneInfo("Europe/Paris")),
            datetime(2026, 11, 10, 9, tzinfo=ZoneInfo("Europe/Paris")),
            False,
        ),
        (
            datetime(2026, 11, 10, 11, tzinfo=ZoneInfo("Europe/Paris")),
            datetime(2026, 11, 10, 9, tzinfo=ZoneInfo("Europe/Paris")),
            False,
        ),
    ],
)
@pytest.mark.django_db
def test_intervention_schedule_validation(
    starts_at,
    ends_at,
    is_valid,
    intervention_author,
):
    client = Client.objects.create(
        name="Entreprise Test",
    )

    intervention = Intervention(
        created_by=intervention_author,
        client=client,
        title="Maintenance du poste de travail",
        starts_at=starts_at,
        ends_at=ends_at,
    )

    if is_valid:
        intervention.full_clean()
    else:
        with pytest.raises(ValidationError) as exc_info:
            intervention.full_clean()

        assert "ends_at" in exc_info.value.message_dict
