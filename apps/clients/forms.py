from django import forms

from apps.clients.models import Client


class ClientForm(forms.ModelForm):
    """Form for creation and editing a client."""

    class Meta:
        model = Client
        fields = [
            "name",
            "contact_name",
            "email",
            "phone",
            "address",
            "postal_code",
            "city",
            "notes",
        ]
        labels = {
            "name": "Nom du client",
            "contact_name": "Nom du contact",
            "email": "Adresse e-mail",
            "phone": "Téléphone",
            "address": "Adresse",
            "postal_code": "Code postal",
            "city": "Ville",
            "notes": "Notes",
        }
        widgets = {
            "email": forms.EmailInput(),
            "phone": forms.TextInput(attrs={"autocomplete": "tel"}),
            "address": forms.TextInput(attrs={"autocomplete": "street-address"}),
            "postal_code": forms.TextInput(attrs={"autocomplete": "postal-code"}),
            "city": forms.TextInput(attrs={"autocomplete": "address-level2"}),
            "notes": forms.Textarea(attrs={"rows": 4}),
        }

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

    def clean_name(self):
        """Reject a client name containing only whitespace."""
        name = self.cleaned_data["name"].strip()

        if not name:
            raise forms.ValidationError("Le nom du client est obligatoire.")

        return name
