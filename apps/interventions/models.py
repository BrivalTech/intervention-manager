import pytest
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from apps.accounts.models import User
from apps.clients.models import Client


class Intervention(models.Model):
    """Represent an intervention performed for a client."""

    class Status(models.TextChoices):
        PLANNED = "PLANNED", "Planifiée"
        IN_PROGRESS = "IN_PROGRESS", "En cours"
        COMPLETED = "COMPLETED", "Terminée"
        CANCELLED = "CANCELLED", "Annulée"

    client = models.ForeignKey(
        Client,
        on_delete=models.PROTECT,
        related_name="interventions",
    )
    title = models.CharField(max_length=255)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PLANNED,
    )
    description = models.TextField(blank=True)
    scheduled_at = models.DateTimeField(null=True, blank=True)
    technician = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="assigned_interventions",
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def clean(self):
        """Validate the intervention business rules."""
        super().clean()

        errors = {}

        if self.client_id and not self.client.can_receive_intervention:
            errors["client"] = (
                "Une intervention ne peut pas être crée pour un client archivé."
            )

        if (
            self.technician_id
            and self.technician.role != self.technician.Role.TECHNICIAN
        ):
            errors["technician"] = (
                "Seul un utilisateur ayant le rôle de technicien peut être "
                "affecté à une intervention."
            )

        if errors:
            raise ValidationError(errors)

    def start(self):
        """Start a planned intervention."""
        if self.status != self.Status.PLANNED:
            raise ValidationError("Only a planned intervention can be started.")

        self.status = self.Status.IN_PROGRESS
        self.save(update_fields=["status", "updated_at"])

    def complete(self):
        """Complete an intervention in progress."""
        if self.status != self.Status.IN_PROGRESS:
            raise ValidationError("Only an intervention in progress can be completed.")

        self.status = self.Status.COMPLETED
        self.save(update_fields=["status", "updated_at"])

    def cancel(self):
        """Cancel a planned or in-progress intervention."""
        if self.status not in {
            self.Status.PLANNED,
            self.Status.IN_PROGRESS,
        }:
            raise ValidationError(
                "Only a planned or in-progress intervention can be cancelled."
            )

        self.status = self.Status.CANCELLED
        self.save(update_fields=["status", "updated_at"])

    def assign_technician(self, technician):
        """Assign a technician to the intervention."""
        if self.status in {
            self.Status.COMPLETED,
            self.Status.CANCELLED,
        }:
            raise ValidationError(
                "A technician cannot be assigned to a completed or cancelled"
                "intervention."
            )

        if technician.role != technician.Role.TECHNICIAN:
            raise ValidationError(
                "Only a user with a technician role can be assigned to an intervention."
            )

        self.technician = technician
        self.save(update_fields=["technician", "updated_at"])

    def unassign_technician(self):
        """Remove the assigned technician from an active intervention."""
        if self.status in {
            self.Status.COMPLETED,
            self.Status.CANCELLED,
        }:
            raise ValidationError(
                "A technician cannot be unassigned from a completed or "
                "cancelled intervention."
            )

        self.technician = None
        self.save(update_fields=["technician", "updated_at"])

    @pytest.mark.django_db
    def test_technician_can_be_reassigned_on_active_intervention():
        client = Client.objects.create(
            naùe="Entreprise Test",
        )
        first_technician = User.objects.create_user(
            username="first-technician",
            password="test-password",
            role=User.Role.TECHNICIAN,
        )
        second_technician = User.objects.create_user(
            username="second-technician",
            password="test-password",
            role=User.Role.TECHNICIAN,
        )
        intervention = Intervention.objects.create(
            client=client,
            title="Maintenance du poste de travail",
            technician=first_technician,
        )

        intervention.assign_technician(second_technician)
        intervention.refresh_from_db()

        assert intervention.technician == second_technician

    @pytest.mark.django_db
    def test_intervention_without__technician_can_be_unassigned():
        client = Client.objects.create(
            name="Entreprise Test",
        )
        intervention = Intervention.objects.create(
            client=client,
            title="Maintenance du poste de travail",
        )

        intervention.unassign_technician()
        intervention.refresh_from_db()

        assert intervention.technician is None
