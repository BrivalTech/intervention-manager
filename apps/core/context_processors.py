from apps.accounts.permissions import can_view_managers, can_view_technicians
from apps.clients.permissions import can_view_clients
from apps.interventions.permissions import can_view_interventions


def navigation_permissions(request):
    """ "Expose navigation permissions to templates"""
    return {
        "nav_can_view_clients": can_view_clients(request.user),
        "nav_can_view_technicians": can_view_technicians(request.user),
        "nav_can_view_managers": can_view_managers(request.user),
        "nav_can_view_interventions": can_view_interventions(request.user),
    }
