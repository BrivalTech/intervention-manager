from django.core.exceptions import ValidationError
from django.db import models

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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def clean(self):
        """Validate the intervention business rules."""
        super().clean()

        if self.client_id and not self.client.can_receive_intervention:
            raise ValidationError(
                {
                    "client": "Une intervention ne peut pas être crée pour un "
                    "client archivé."
                }
            )
