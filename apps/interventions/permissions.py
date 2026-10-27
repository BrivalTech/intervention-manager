from apps.accounts.models import User


def can_view_interventions(user):
    """Check whether the user can view interventions."""
    return (
        user.is_authenticated
        and user.is_active
        and user.role
        in {
            User.Role.ADMIN,
            User.Role.MANAGER,
            User.Role.TECHNICIAN,
        }
    )


def can_create_intervention(user):
    """Check whether the user can create an intervention."""
    return (
        user.is_authenticated
        and user.is_active
        and user.role
        in {
            User.Role.ADMIN,
            User.Role.MANAGER,
        }
    )


def can_manage_assignment(user):
    """Return whether the user can manage technician assignment."""
    return user.role in {
        User.Role.ADMIN,
        User.Role.MANAGER,
    }


def can_update_status(user, intervention, action):
    """Check whether a user can perform a status transition."""
    if not user.is_authenticated or not user.is_active:
        return False

    allowed_statuses = {
        "start": {intervention.Status.PLANNED},
        "complete": {intervention.Status.IN_PROGRESS},
        "cancel": {
            intervention.Status.TO_PLAN,
            intervention.Status.PLANNED,
            intervention.Status.IN_PROGRESS,
        },
    }

    if action not in allowed_statuses:
        return False

    if intervention.status not in allowed_statuses[action]:
        return False

    if user.role in {User.Role.ADMIN, User.Role.MANAGER}:
        return True

    if user.role == User.Role.TECHNICIAN:
        return intervention.technician_id == user.pk and action in {"start", "complete"}

    return False


def can_edit_intervention(user, intervention):
    """Check whether the user can edit an intervention."""
    return (
        user.is_authenticated
        and user.is_active
        and user.role
        in {
            User.Role.ADMIN,
            User.Role.MANAGER,
        }
        and intervention.status
        in {
            intervention.Status.TO_PLAN,
            intervention.Status.PLANNED,
        }
    )
