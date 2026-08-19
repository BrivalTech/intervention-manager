from django.conf import settings


def test_debug_setting_is_boolean():
    assert isinstance(settings.DEBUG, bool)
