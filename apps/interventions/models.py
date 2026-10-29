import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from apps.clients.models import Client


class Intervention(models.Model):
    """Represent an intervention performed for a client."""

    class Status(models.TextChoices):
        TO_PLAN = "TO_PLAN", "À planifier"
        PLANNED = "PLANNED", "Planifiée"
        IN_PROGRESS = "IN_PROGRESS", "En cours"
        COMPLETED = "COMPLETED", "Terminée"
        CANCELLED = "CANCELLED", "Annulée"

    public_id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
    )
    client = models.ForeignKey(
        Client,
        on_delete=models.PROTECT,
        related_name="interventions",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_interventions",
    )
    title = models.CharField(max_length=255)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.TO_PLAN,
    )
    description = models.TextField(blank=True)
    report = models.TextField(
        blank=True,
        verbose_name="Compte rendu d'intervention",
    )
    address = models.CharField(max_length=255, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    city = models.CharField(max_length=100, blank=True)
    starts_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Date et heure de début",
    )
    ends_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Date et heure de fin",
    )
    technician = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="assigned_interventions",
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(starts_at__isnull=True, ends_at__isnull=True)
                    | (
                        models.Q(starts_at__isnull=False, ends_at__isnull=False)
                        & models.Q(ends_at__gt=models.F("starts_at"))
                    )
                ),
                name="intervention_valid_schedule",
            ),
        ]

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

        if (self.starts_at is None) != (self.ends_at is None):
            errors["ends_at"] = (
                "Les dates de début et de fin doivent être renseignées ensemble."
            )

        elif (
            self.starts_at is not None
            and self.ends_at is not None
            and self.ends_at <= self.starts_at
        ):
            errors["ends_at"] = (
                "La date de fin doit être postérieure à la date de début."
            )

        if (
            self.technician_id is not None
            and self.starts_at is not None
            and self.ends_at is not None
            and self.ends_at > self.starts_at
            and self.status != self.Status.CANCELLED
        ):
            overlapping = Intervention.objects.filter(
                technician_id=self.technician_id,
                starts_at__lt=self.ends_at,
                ends_at__gt=self.starts_at,
            ).exclude(
                status=self.Status.CANCELLED,
            )

            if self.pk is not None:
                overlapping = overlapping.exclude(pk=self.pk)

            if overlapping.exists():
                errors["technician"] = (
                    "Ce technicien possède déjà une intervention "
                    "sur cette plage horaire."
                )

        if self.status == self.Status.COMPLETED and not self.report.strip():
            errors["report"] = (
                "Un compte rendu est obligatoire pour terminer une intervention."
            )

        if errors:
            raise ValidationError(errors)

    def start(self):
        """Start a planned intervention."""
        if self.status != self.Status.PLANNED:
            raise ValidationError("Only a planned intervention can be started.")

        self.status = self.Status.IN_PROGRESS
        self.save(update_fields=["status", "updated_at"])

    def complete(self, report):
        """Complete an intervention with a mandatory report."""
        if self.status != self.Status.IN_PROGRESS:
            raise ValidationError("Only an intervention in progress can be completed.")

        if not isinstance(report, str) or not report.strip():
            raise ValidationError(
                {
                    "report": "Un compte rendu est obligatoire pour"
                    "terminer l'intervention."
                }
            )

        previous_status = self.status
        previous_report = self.report

        self.report = report.strip()
        self.status = self.Status.COMPLETED

        try:
            self.full_clean()
        except ValidationError:
            self.status = previous_status
            self.report = previous_report
            raise

        self.save(update_fields=["report", "status", "updated_at"])

    def cancel(self):
        """Cancel a planned or in-progress intervention."""
        if self.status not in {
            self.Status.TO_PLAN,
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

        previous_technician = self.technician

        self.technician = technician

        try:
            self.full_clean()
        except ValidationError:
            self.technician = previous_technician
            raise

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
