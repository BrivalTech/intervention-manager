import uuid

from django.core.exceptions import ValidationError
from django.db import models


class Client(models.Model):
    """Represent a client for whom interventions can be managed."""

    public_id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
    )
    name = models.CharField(max_length=255)
    contact_name = models.CharField(max_length=255, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    address = models.CharField(max_length=255, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    city = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    @property
    def can_receive_intervention(self):
        """Return whether a new intervention can be created for the client."""
        return self.is_active

    def archive(self):
        """Archive the client only when no interventions remain active."""
        from apps.interventions.models import Intervention

        blocking_statuses = {
            Intervention.Status.TO_PLAN,
            Intervention.Status.PLANNED,
            Intervention.Status.IN_PROGRESS,
        }

        if self.interventions.filter(
            status__in=blocking_statuses,
        ).exists():
            raise ValidationError(
                "Impossible d'archiver ce client : "
                "des interventions sont encore à planifier, planifiées ou en cours."
            )

        self.is_active = False
        self.save(update_fields=["is_active", "updated_at"])

    def restore(self):
        """Restore the client by making it as active."""
        self.is_active = True
        self.save(update_fields=["is_active", "updated_at"])
