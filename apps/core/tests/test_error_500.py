from django.test import override_settings


@override_settings(DEBUG=False, ROOT_URLCONF="apps.core.tests.error_500_urls")
def test_unhandled_exception_uses_custom_500_page(client):
    client.raise_request_exception = False

    response = client.get("/simulate-server-error/")

    assert response.status_code == 500
    assert "500.html" in [template.name for template in response.templates]
    content = response.content.decode()
    assert 'id="main-content"' in content
    assert 'id="error-title"' in content
    assert "Une erreur est survenue" in content
    assert "Retour à l’accueil" in content
    assert "Simulated server error for test" not in content
