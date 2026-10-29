import pytest

from apps.accounts.models import User


@pytest.fixture
def intervention_author(db):
    """Administrator who created an intervention."""
    return User.objects.create_user(
        username="intervention_author",
        role=User.Role.ADMIN,
    )
