from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from apps.accounts.account_config import (
    MANAGER_CONFIG,
    TECHNICIAN_CONFIG,
)
from apps.accounts.account_views import (
    account_create,
    account_list,
    account_resend_invitation,
    account_set_active,
    account_update,
)


@login_required
def technician_list(request):
    return account_list(request, TECHNICIAN_CONFIG)


@login_required
def technician_create(request):
    return account_create(request, TECHNICIAN_CONFIG)


@login_required
def technician_update(request, public_id):
    return account_update(request, public_id, TECHNICIAN_CONFIG)


@login_required
@require_POST
def technician_resend_invitation(request, public_id):
    return account_resend_invitation(request, public_id, TECHNICIAN_CONFIG)


@login_required
@require_POST
def technician_deactivate(request, public_id):
    return account_set_active(request, public_id, TECHNICIAN_CONFIG, active=False)


@login_required
@require_POST
def technician_reactivate(request, public_id):
    return account_set_active(request, public_id, TECHNICIAN_CONFIG, active=True)


@login_required
def manager_list(request):
    return account_list(request, MANAGER_CONFIG)


@login_required
def manager_create(request):
    return account_create(request, MANAGER_CONFIG)


@login_required
def manager_update(request, public_id):
    return account_update(request, public_id, MANAGER_CONFIG)


@login_required
@require_POST
def manager_resend_invitation(request, public_id):
    return account_resend_invitation(request, public_id, MANAGER_CONFIG)


@login_required
@require_POST
def manager_deactivate(request, public_id):
    return account_set_active(request, public_id, MANAGER_CONFIG, active=False)


@login_required
@require_POST
def manager_reactivate(request, public_id):
    return account_set_active(request, public_id, MANAGER_CONFIG, active=True)
