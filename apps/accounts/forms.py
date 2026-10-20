from django import forms

from apps.accounts.models import User


class TechnicianForm(forms.ModelForm):
    """Form for creating a Technician account"""

    email = forms.EmailField(
        label="Adresse e-mail",
        required=True,
        widget=forms.EmailInput(attrs={"autocomplete": "email"}),
    )

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "username",
            "email",
        ]
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.required = True
            field.widget.attrs["class"] = "form-control"

            described_by = []

            if field.help_text:
                described_by.append(f"id_{name}_help")

            if self.is_bound and self.errors.get(name):
                field.widget.attrs["aria-invalid"] = "true"
                described_by.append(f"id_{name}_error")

            if described_by:
                field.widget.attrs["aria-describedby"] = " ".join(described_by)

    def clean_email(self):
        """Reject an email already used by another account."""
        email = self.cleaned_data["email"].strip().lower()

        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Cette adresse e-mail est déjà utilisée.")

        return email

    def clean_first_name(self):
        """Reject an empty first name."""
        first_name = self.cleaned_data["first_name"].strip()

        if not first_name:
            raise forms.ValidationError("Le prénom est obligatoire.")

        return first_name

    def clean_last_name(self):
        """Reject an empty last name."""
        last_name = self.cleaned_data["last_name"].strip()

        if not last_name:
            raise forms.ValidationError("Le nom est obligatoire.")

        return last_name

    def save(self, commit=True):
        """Create a technician without an initial password."""
        user = super().save(commit=False)

        user.role = User.Role.TECHNICIAN
        user.set_unusable_password()

        if commit:
            user.save()

        return user
