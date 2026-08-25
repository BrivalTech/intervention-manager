from apps.accounts.models import User


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
