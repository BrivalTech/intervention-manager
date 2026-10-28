from django import template

register = template.Library()


@register.filter
def accessible_field(field):
    """Render a form field with accessible error attributes."""
    attrs = {}

    if field.errors:
        attrs["aria-invalid"] = "true"

        described_by = []

        if field.help_text:
            described_by.append(f"{field.auto_id}_help")

        described_by.append(f"{field.auto_id}_error")

        attrs["aria-describedby"] = " ".join(described_by)

    return field.as_widget(attrs=attrs)
