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
    """Return whether the user can perform a status action on an
    intervention."""
    if user.role in {
        User.Role.ADMIN,
        User.Role.MANAGER,
    }:
        return action in {
            "start",
            "complete",
            "cancel",
        }

    if user.role != User.Role.TECHNICIAN:
        return False

    if intervention.technician_id != user.id:
        return False

    return action in {
        "start",
        "complete",
    }
