from dataclasses import dataclass

from django import forms

from apps.accounts.forms import (
    ManagerCreatingForm,
    ManagerUpdateForm,
    TechnicianCreatingForm,
    TechnicianUpdateForm,
)
from apps.accounts.models import User
from apps.accounts.permissions import (
    can_manage_managers,
    can_manage_technicians,
    can_view_managers,
    can_view_technicians,
)


@dataclass(frozen=True)
class AccountConfig:
    role: str
    label: str
    list_url: str
    list_template: str
    form_template: str
    create_form: type[forms.ModelForm]
    update_form: type[forms.ModelForm]
    can_view: object
    can_manage: object
    plural_label: str
    create_url: str
    update_url: str
    deactivate_url: str
    reactivate_url: str
    resend_url: str


TECHNICIAN_CONFIG = AccountConfig(
    role=User.Role.TECHNICIAN,
    label="technicien",
    list_url="accounts:technician_list",
    list_template="accounts/technician_list.html",
    form_template="accounts/technician_form.html",
    create_form=TechnicianCreatingForm,
    update_form=TechnicianUpdateForm,
    can_view=can_view_technicians,
    can_manage=can_manage_technicians,
    plural_label="techniciens",
    create_url="accounts:technician_create",
    update_url="accounts:technician_update",
    deactivate_url="accounts:technician_deactivate",
    reactivate_url="accounts:technician_reactivate",
    resend_url="accounts:technician_resend_invitation",
)

MANAGER_CONFIG = AccountConfig(
    role=User.Role.MANAGER,
    label="gestionnaire",
    list_url="accounts:manager_list",
    list_template="accounts/manager_list.html",
    form_template="accounts/manager_form.html",
    create_form=ManagerCreatingForm,
    update_form=ManagerUpdateForm,
    can_view=can_view_managers,
    can_manage=can_manage_managers,
    plural_label="gestionnaires",
    create_url="accounts:manager_create",
    update_url="accounts:manager_update",
    deactivate_url="accounts:manager_deactivate",
    reactivate_url="accounts:manager_reactivate",
    resend_url="accounts:manager_resend_invitation",
)
