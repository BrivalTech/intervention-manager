from datetime import timedelta

import pytest
from django.utils import timezone

from apps.accounts.models import User
from apps.clients.models import Client
from apps.interventions.forms import InterventionForm
from apps.interventions.templatetags.intervention_form_tags import (
    accessible_field,
)


@pytest.fixture
def active_client():
    return Client.objects.create(name="Entreprise Alpha")


@pytest.fixture
def form_data(active_client):
    return {
        "client": active_client.pk,
        "title": "Maintenance informatique",
        "description": "Vérification des équipements",
    }


@pytest.mark.django_db
def test_form_accepts_valid_data(form_data, intervention_author):
    form = InterventionForm(data=form_data)
    form.instance.created_by = intervention_author

    assert form.is_valid(), form.errors


@pytest.mark.django_db
def test_form_rejects_archived_client(
    form_data,
    active_client,
    intervention_author,
):
    active_client.archive()
    form = InterventionForm(data=form_data)
    form.instance.created_by = intervention_author

    assert not form.is_valid()
    assert "client" in form.errors


@pytest.mark.django_db
def test_form_only_lists_active_clients(active_client):
    archived_client = Client.objects.create(name="Client archivé")
    archived_client.archive()
    form = InterventionForm()

    assert active_client in form.fields["client"].queryset
    assert archived_client not in form.fields["client"].queryset


@pytest.mark.django_db
def test_form_only_lists_active_technicians(django_user_model):
    active = django_user_model.objects.create_user(
        username="technician-active",
        role=User.Role.TECHNICIAN,
    )
    inactive = django_user_model.objects.create_user(
        username="technician-inactive",
        role=User.Role.TECHNICIAN,
        is_active=False,
    )
    manager = django_user_model.objects.create_user(
        username="manager-form",
        role=User.Role.MANAGER,
    )

    form = InterventionForm()
    technicians = form.fields["technician"].queryset

    assert active in technicians
    assert inactive not in technicians
    assert manager not in technicians


@pytest.mark.django_db
@pytest.mark.parametrize("title", ["", "   "])
def test_form_requires_title(form_data, intervention_author, title):
    form_data["title"] = title
    form = InterventionForm(data=form_data)
    form.instance.created_by = intervention_author

    assert not form.is_valid()
    assert "title" in form.errors


@pytest.mark.django_db
def test_form_rejects_incomplete_schedule(form_data, intervention_author):
    form_data["starts_at"] = "2026-11-02T09:00"
    form = InterventionForm(data=form_data)
    form.instance.created_by = intervention_author

    assert not form.is_valid()
    assert "ends_at" in form.errors


@pytest.mark.django_db
def test_form_rejects_end_before_start(form_data, intervention_author):
    form_data["starts_at"] = "2026-11-02T11:00"
    form_data["ends_at"] = "2026-11-02T09:00"
    form = InterventionForm(data=form_data)
    form.instance.created_by = intervention_author

    assert not form.is_valid()
    assert "ends_at" in form.errors


@pytest.mark.django_db
def test_form_accepts_valid_schedule(form_data, intervention_author):
    start = timezone.localtime(timezone.now()).replace(
        second=0,
        microsecond=0,
    ) + timedelta(days=1)
    end = start + timedelta(hours=2)
    form_data["starts_at"] = start.strftime("%Y-%m-%dT%H:%M")
    form_data["ends_at"] = end.strftime("%Y-%m-%dT%H:%M")
    form = InterventionForm(data=form_data)
    form.instance.created_by = intervention_author

    assert form.is_valid(), form.errors


@pytest.mark.django_db
def test_form_excludes_internal_fields():
    form = InterventionForm()

    for field in ("created_by", "status", "report", "created_at", "updated_at"):
        assert field not in form.fields


@pytest.mark.django_db
def test_form_applies_design_system_classes():
    form = InterventionForm()

    for field in form.fields.values():
        assert "form-control" in field.widget.attrs["class"]


@pytest.mark.django_db
def test_form_marks_invalid_fields_accessibly(form_data, intervention_author):
    form_data["title"] = ""
    form = InterventionForm(data=form_data)
    form.instance.created_by = intervention_author

    assert not form.is_valid()

    html = accessible_field(form["title"])
    assert 'aria-invalid="true"' in html
    assert 'aria-describedby="id_title_error"' in html


@pytest.mark.django_db
def test_form_validation_is_not_triggered_during_initialization(
    form_data,
    intervention_author,
):
    form = InterventionForm(data=form_data)
    assert form._errors is None

    form.instance.created_by = intervention_author
    assert form.is_valid(), form.errors
