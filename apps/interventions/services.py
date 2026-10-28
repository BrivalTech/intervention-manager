from django.db import transaction

from apps.interventions.models import Intervention
from apps.interventions.permissions import (
    can_edit_intervention,
    can_manage_assignment,
    can_update_status,
)


def create_intervention(
    *,
    client,
    created_by,
    title,
    description="",
    address="",
    postal_code="",
    city="",
    starts_at=None,
    ends_at=None,
    technician=None,
):
    """Create and validate an intervention before saving it."""
    intervention = Intervention(
        client=client,
        created_by=created_by,
        title=title,
        description=description,
        address=address,
        postal_code=postal_code,
        city=city,
        starts_at=starts_at,
        ends_at=ends_at,
        technician=technician,
        status=(
            Intervention.Status.PLANNED
            if starts_at is not None and ends_at is not None
            else Intervention.Status.TO_PLAN
        ),
    )

    intervention.full_clean()
    intervention.save()

    return intervention


@transaction.atomic
def update_intervention(*, user, intervention, **data):
    """Update an editable intervention and validate business rules."""
    if not can_edit_intervention(user, intervention):
        raise PermissionError("You do not have permission to edit this intervention.")

    editable_fields = {
        "client",
        "title",
        "description",
        "address",
        "postal_code",
        "city",
        "technician",
        "starts_at",
        "ends_at",
    }

    unknown_fields = set(data) - editable_fields
    if unknown_fields:
        raise ValueError("Unknown intervention fields.")

    intervention.refresh_from_db()

    previous_values = {field: getattr(intervention, field) for field in editable_fields}
    previous_status = intervention.status

    try:
        for field, value in data.items():
            setattr(intervention, field, value)

        if intervention.starts_at is None and intervention.ends_at is None:
            intervention.status = Intervention.Status.TO_PLAN
        elif intervention.starts_at is not None and intervention.ends_at is not None:
            intervention.status = Intervention.Status.PLANNED

        intervention.full_clean()
        intervention.save()

    except Exception:
        for field, value in previous_values.items():
            setattr(intervention, field, value)

        intervention.status = previous_status
        raise

    return intervention


def assign_technician(
    *,
    user,
    intervention,
    technician,
):
    """Assign a technician when the user has permission to manage
    assignments."""
    if not can_manage_assignment(user):
        raise PermissionError(
            "You do not have permission to manage technician assignment."
        )

    intervention.assign_technician(technician)

    return intervention


def unassign_technician(*, user, intervention):
    """Unassign a technician when the user can manage assignments."""
    if not can_manage_assignment(user):
        raise PermissionError(
            "You do not have permission to manage technician assignment."
        )

    intervention.unassign_technician()

    return intervention


def update_intervention_status(
    *,
    user,
    intervention,
    action,
    report=None,
):
    """Perform an authorized status action on an intervention."""
    if not can_update_status(user, intervention, action):
        raise PermissionError(
            "You do not have permission to update this intervention status."
        )

    if action == "complete":
        intervention.complete(report)
    elif action == "start":
        intervention.start()
    elif action == "cancel":
        intervention.cancel()
    else:
        raise ValueError("Unknown intervention status action.")

    return intervention
