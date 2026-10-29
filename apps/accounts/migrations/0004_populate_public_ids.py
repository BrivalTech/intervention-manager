import uuid

from django.db import migrations


def populate_public_ids(apps, schema_editor):
    User = apps.get_model("accounts", "User")
    db_alias = schema_editor.connection.alias

    accounts = User.objects.using(db_alias).filter(
        public_id__isnull=True
    )

    for account in accounts.iterator():
        account.public_id = uuid.uuid4()
        account.save(update_fields=["public_id"], using=db_alias)


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0003_user_public_id"),
    ]

    operations = [
        migrations.RunPython(
            populate_public_ids,
            migrations.RunPython.noop,
        ),
    ]
