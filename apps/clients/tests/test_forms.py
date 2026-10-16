import pytest

from apps.clients.forms import ClientForm


def test_client_form_accepts_valid_data():
    form = ClientForm(
        data={
            "name": "Entreprise Allibi",
            "contact_name": "Marie Durand",
            "email": "contact@allibi.fr",
            "phone": "0102030405",
            "address": "10 rue des Lilas",
            "postal_code": "75001",
            "city": "Paris",
            "notes": "Client professionnel",
        }
    )

    assert form.is_valid(), form.errors
    assert form.cleaned_data["name"] == "Entreprise Allibi"


@pytest.mark.parametrize("name", ["", "   "])
def test_client_form_requires_name(name):
    form = ClientForm(data={"name": name})

    assert not form.is_valid()
    assert "name" in form.errors


def test_client_form_rejects_invalid_email():
    form = ClientForm(
        data={
            "name": "Entreprise Allibi",
            "email": "adresse-invalide",
        }
    )

    assert not form.is_valid()
    assert "email" in form.errors


def test_client_form_accepts_optional_fields_empty():
    form = ClientForm(data={"name": "Entreprise Allibi"})

    assert form.is_valid(), form.errors


def test_client_form_trims_client_name():
    form = ClientForm(data={"name": "  Entreprise Allibi  "})

    assert form.is_valid(), form.errors
    assert form.cleaned_data["name"] == "Entreprise Allibi"


def test_client_form_excludes_internal_fields():
    form = ClientForm()

    assert "is_active" not in form.fields
    assert "created_at" not in form.fields
    assert "updated_at" not in form.fields


def test_client_form_uses_accessible_field_labels():
    form = ClientForm()

    assert form.fields["name"].label == "Nom du client"
    assert form.fields["email"].label == "Adresse e-mail"
    assert form.fields["notes"].label == "Notes"


@pytest.mark.django_db
def test_client_form_creates_active_client():
    form = ClientForm(data={"name": "Entreprise Alpha"})

    assert form.is_valid(), form.errors

    client = form.save()

    assert client.pk is not None
    assert client.name == "Entreprise Alpha"
    assert client.is_active is True


def test_client_form_applies_design_system_classes():
    form = ClientForm()
    for field in form:
        assert "form-control" in field.field.widget.attrs["class"]


def test_client_form_marks_invalid_field_accessibly():
    form = ClientForm(
        data={
            "name": "Entreprise Alpha",
            "email": "adresse-invalide",
        }
    )

    assert not form.is_valid()

    email_widget = form.fields["email"].widget
    assert email_widget.attrs["aria-invalid"] == "true"
    assert email_widget.attrs["aria-describedby"] == "id_email_error"


def test_client_form_does_not_mark_valid_fields_invalid():
    form = ClientForm(data={"name": "Entreprise Alpha"})

    assert form.is_valid()

    for field in form.fields.values():
        assert "aria-invalid" not in field.widget.attrs
