from apps.accounts.models import User


def can_view_technicians(user):
    """Check whether a user can consult the technician datas"""
    return (
        user.is_authenticated
        and user.is_active
        and user.role
        in {
            User.Role.ADMIN,
            User.Role.MANAGER,
        }
    )


def can_manage_technicians(user):
    """Check whether a user can create, update or deactivate technicians"""
    return user.is_authenticated and user.is_active and user.role == User.Role.ADMIN


def can_view_managers(user):
    """Check whether a user can view manager accounts."""
    return can_manage_technicians(user)


def can_manage_managers(user):
    """Check whether a user can manage manager accounts."""
    return can_manage_technicians(user)
