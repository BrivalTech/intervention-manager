from django.urls import reverse


def test_home_page(client):
    response = client.get(reverse("core:home"))
    assert response.status_code == 200
    assert "home.html" in [t.name for t in response.templates]


def test_design_system_page(client):
    response = client.get(reverse("core:design-system"))
    assert response.status_code == 200
    assert "design-system.html" in [t.name for t in response.templates]
