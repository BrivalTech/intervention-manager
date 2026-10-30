import pytest

from apps.accounts.models import User
from apps.clients.models import Client
from apps.interventions.models import Intervention


@pytest.fixture
def user_factory(db):
    """Create a user with customizable attributes."""

    def create(**kwargs):
        username = kwargs.pop("username", None)
        if username is None:
            username = f"test_user_{User.objects.count() + 1}"

        password = kwargs.pop("password", "TestPassword123!")
        role = kwargs.pop("role", User.Role.ADMIN)

        return User.objects.create_user(
            username=username,
            password=password,
            role=role,
            **kwargs,
        )

    return create


@pytest.fixture
def sample_user(user_factory):
    return user_factory()


@pytest.fixture
def client_factory(db):
    """Create a client with customizable attributes."""

    def create(**kwargs):
        name = kwargs.pop("name", None)
        if name is None:
            name = f"Client test {Client.objects.count() + 1}"

        return Client.objects.create(
            name=name,
            **kwargs,
        )

    return create


@pytest.fixture
def sample_client(client_factory):
    """Create a default active business client."""
    return client_factory()


@pytest.fixture
def intervention_factory_generic(db, client_factory, user_factory):
    """Create an intervention with its required relationships."""

    def create(**kwargs):
        client = kwargs.pop("client", None)
        created_by = kwargs.pop("created_by", None)
        title = kwargs.pop("title", "Intervention de test")

        return Intervention.objects.create(
            client=client if client is not None else client_factory(),
            created_by=(created_by if created_by is not None else user_factory()),
            title=title,
            **kwargs,
        )

    return create


@pytest.fixture
def intervention(intervention_factory_generic):
    """Create a default intervention."""
    return intervention_factory_generic()
