import uuid

from django.db import migrations


def populate_public_ids(apps, schema_editor):
    Client = apps.get_model("clients", "Client")
    db_alias = schema_editor.connection.alias

    clients = Client.objects.using(db_alias).filter(
        public_id__isnull=True
    )

    for client in clients.iterator():
        client.public_id = uuid.uuid4()
        client.save(update_fields=["public_id"], using=db_alias)


class Migration(migrations.Migration):
    dependencies = [
        ("clients", "0002_client_public_id"),
    ]

    operations = [
        migrations.RunPython(
            populate_public_ids,
            migrations.RunPython.noop,
        ),
    ]
