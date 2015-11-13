# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.management import call_command
from django.db import migrations, models


class Migration(migrations.Migration):

    def load_data(apps, schema_editor):
        call_command("loaddata", "../fixtures/initial_user.json")

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.RunPython(load_data),
    ]
