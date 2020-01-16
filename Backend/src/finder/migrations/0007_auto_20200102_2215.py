# Generated by Django 2.2.7 on 2020-01-02 20:15

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('finder', '0006_auto_20200102_2155'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organizationprofile',
            name='address',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='organizationprofile',
            name='tagsAndKeywords',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.TextField(), size=None),
        ),
    ]