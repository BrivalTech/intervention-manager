from django import forms
from django.contrib.auth.forms import SetPasswordForm

from apps.accounts.models import User


class FormControlMixin:
    """Apply design system and accessibility attributes to form fields."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs["class"] = "form-control"

            described_by = []

            if field.help_text:
                described_by.append(f"id_{name}_help")

            if self.is_bound and self.errors.get(name):
                field.widget.attrs["aria-invalid"] = "true"
                described_by.append(f"id_{name}_error")

            if described_by:
                field.widget.attrs["aria-describedby"] = " ".join(described_by)


class AccountCreatingForm(FormControlMixin, forms.ModelForm):
    """Common form for creating a user account."""

    email = forms.EmailField(
        label="Adresse e-mail",
        required=True,
        widget=forms.EmailInput(attrs={"autocomplete": "email"}),
    )

    class Meta:
        model = User
        fields = ["first_name", "last_name", "username", "email"]
        labels = {
            "first_name": "Prénom",
            "last_name": "Nom",
            "username": "Identifiant",
            "email": "Adresse e-mail",
        }
        widgets = {
            "first_name": forms.TextInput(attrs={"autocomplete": "given-name"}),
            "last_name": forms.TextInput(attrs={"autocomplete": "family-name"}),
            "username": forms.TextInput(attrs={"autocomplete": "off"}),
            "email": forms.EmailInput(attrs={"autocomplete": "email"}),
        }

    account_role = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.required = True

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()

        existing_users = User.objects.filter(email__iexact=email)

        if self.instance.pk:
            existing_users = existing_users.exclude(pk=self.instance.pk)

        if existing_users.exists():
            raise forms.ValidationError("Cette adresse e-mail est déjà utilisée.")

        return email

    def clean_first_name(self):
        first_name = self.cleaned_data["first_name"].strip()

        if not first_name:
            raise forms.ValidationError("Le prénom est obligatoire.")

        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data["last_name"].strip()

        if not last_name:
            raise forms.ValidationError("Le nom est obligatoire.")

        return last_name

    def save(self, commit=True):
        if self.account_role is None:
            raise ValueError("Le rôle du compte doit être défini.")

        user = super().save(commit=False)
        user.role = self.account_role
        user.set_unusable_password()

        if commit:
            user.save()

        return user


class AccountUpdateForm(AccountCreatingForm):
    """Update account details without changing credentials."""

    def save(self, commit=True):
        user = forms.ModelForm.save(self, commit=False)

        if commit:
            user.save(
                update_fields=[
                    "first_name",
                    "last_name",
                    "username",
                    "email",
                ]
            )

        return user


class TechnicianCreatingForm(AccountCreatingForm):
    """Create a new Technician account."""

    account_role = User.Role.TECHNICIAN


class TechnicianUpdateForm(AccountUpdateForm):
    """Update a Technician account."""

    account_role = User.Role.TECHNICIAN


class ManagerCreatingForm(AccountCreatingForm):
    """Create a new Manager account."""

    account_role = User.Role.MANAGER


class ManagerUpdateForm(AccountUpdateForm):
    """Update a Manager account."""

    account_role = User.Role.MANAGER


class TechnicianSetPasswordForm(FormControlMixin, SetPasswordForm):
    """Set a technician password using the application design system."""

    pass
