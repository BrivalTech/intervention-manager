import uuid

from django.db import migrations


def populate_public_ids(apps, schema_editor):
    Intervention = apps.get_model("interventions", "Intervention")
    db_alias = schema_editor.connection.alias

    interventions = Intervention.objects.using(db_alias).filter(
        public_id__isnull=True
    )

    for intervention in interventions.iterator():
        intervention.public_id = uuid.uuid4()
        intervention.save(update_fields=["public_id"], using=db_alias)


class Migration(migrations.Migration):
    dependencies = [
        ("interventions", "0009_intervention_public_id"),
    ]

    operations = [
        migrations.RunPython(
            populate_public_ids,
            migrations.RunPython.noop,
        ),
    ]
