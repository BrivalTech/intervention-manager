import uuid

import pytest


@pytest.mark.django_db
@pytest.mark.parametrize(
    "fixture_name",
    ["sample_user", "sample_client", "intervention"],
)
def test_public_id_is_uuid(request, fixture_name):
    instance = request.getfixturevalue(fixture_name)

    assert isinstance(instance.public_id, uuid.UUID)
    assert instance.public_id.version == 4


@pytest.mark.django_db
@pytest.mark.parametrize(
    "fixture_name",
    ["sample_user", "sample_client", "intervention"],
)
def test_public_id_is_stable(request, fixture_name):
    instance = request.getfixturevalue(fixture_name)
    initial_public_id = instance.public_id

    instance.save()
    instance.refresh_from_db()

    assert instance.public_id == initial_public_id


@pytest.mark.django_db
@pytest.mark.parametrize(
    "fixture_name",
    ["sample_user", "sample_client", "intervention"],
)
def test_primary_key_remains_numeric(request, fixture_name):
    instance = request.getfixturevalue(fixture_name)

    assert isinstance(instance.pk, int)


@pytest.mark.django_db
@pytest.mark.parametrize(
    "factory_name",
    ["user_factory", "client_factory", "intervention_factory_generic"],
)
def test_public_ids_are_unique(request, factory_name):
    factory = request.getfixturevalue(factory_name)

    first = factory()
    second = factory()

    assert first.public_id != second.public_id
