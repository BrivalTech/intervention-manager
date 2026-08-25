from apps.interventions.models import Intervention
from apps.interventions.permissions import can_manage_assignment, can_update_status


def create_intervention(
    *,
    client,
    title,
    description="",
    scheduled_at=None,
    technician=None,
):
    """Create and validate an intervention before saving it."""
    intervention = Intervention(
        client=client,
        title=title,
        description=description,
        scheduled_at=scheduled_at,
        technician=technician,
    )

    intervention.full_clean()
    intervention.save()

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


def update_intervention_status(*, user, intervention, action):
    """Perform an authorized status actions on an intervention."""
    if not can_update_status(user, intervention, action):
        raise PermissionError(
            "You do not have permission to update this intervention status."
        )

    actions = {
        "start": intervention.start,
        "complete": intervention.complete,
        "cancel": intervention.cancel,
    }

    actions[action]()

    return intervention
