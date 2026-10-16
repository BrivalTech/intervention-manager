from apps.accounts.models import User


def can_view_clients(user):
    """Check whether a user can access the client datas"""
    return (
        user.is_authenticated
        and user.is_active
        and user.role
        in {
            User.Role.ADMIN,
            User.Role.MANAGER,
        }
    )


def can_manage_clients(user):
    """Check whether a user can create or update client datas"""
    return can_view_clients(user)


def can_archive_client(user):
    """Check whether a user can archive a client"""
    return user.is_authenticated and user.is_active and user.role == User.Role.ADMIN
