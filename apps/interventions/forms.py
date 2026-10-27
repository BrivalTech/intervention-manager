from django import forms

from apps.accounts.models import User
from apps.clients.models import Client
from apps.interventions.models import Intervention


class InterventionForm(forms.ModelForm):
    """Form for creating an intervention."""

    class Meta:
        model = Intervention
        fields = [
            "client",
            "title",
            "description",
            "address",
            "postal_code",
            "city",
            "technician",
            "starts_at",
            "ends_at",
        ]
        labels = {
            "client": "Client",
            "title": "Titre de l'intervention",
            "description": "Description",
            "address": "Adresse",
            "postal_code": "Code postal",
            "city": "Ville",
            "technician": "Technicien",
            "starts_at": "Date et heure de début",
            "ends_at": "Date et heure de fin",
        }
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "address": forms.TextInput(attrs={"autocomplete": "street-address"}),
            "postal_code": forms.TextInput(attrs={"autocomplete": "postal-code"}),
            "city": forms.TextInput(attrs={"autocomplete": "address-level2"}),
            "starts_at": forms.DateTimeInput(
                format="%Y-%m-%dT%H:%M", attrs={"type": "datetime-local"}
            ),
            "ends_at": forms.DateTimeInput(
                format="%Y-%m-%dT%H:%M",
                attrs={"type": "datetime-local"},
            ),
        }
        help_texts = {
            "starts_at": (
                "Les dates sont facultatives, mais doivent être renseignées ensemble."
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["client"].queryset = Client.objects.filter(is_active=True).order_by(
            "name"
        )

        self.fields["technician"].queryset = User.objects.filter(
            role=User.Role.TECHNICIAN,
            is_active=True,
        ).order_by("username")

        self.fields["technician"].empty_label = "Non affecté"

        for name in ("starts_at", "ends_at"):
            self.fields[name].input_formats = [
                "%Y-%m-%dT%H:%M",
                "%Y-%m-%dT%H:%M:%S",
            ]

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

    def clean_title(self):
        """Reject an empty or whitespace-only title."""
        title = self.cleaned_data["title"].strip()

        if not title:
            raise forms.ValidationError("Le titre de l'intervention est obligatoire.")

        return title
