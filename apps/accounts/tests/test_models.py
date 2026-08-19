import pytest

from apps.accounts.models import User


@pytest.mark.django_db
def test_user_can_be_technician():
    user = User.objects.create_user(
        username="technician",
        password="test-password",
        role=User.Role.TECHNICIAN,
    )

    assert user.role == User.Role.TECHNICIAN
    assert user.is_active is True


#
# @pytest.mark.django_db
# def test_user_can_be_manager():
#     user = User.objects.create_user(
#         username="manager",
#         password="test-password",
#         role=User.Role.MANAGER,
#     )
#
#     assert user.role == User.Role.MANAGER
