# Generated by Django 3.0.5 on 2021-02-09 19:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('finder', '0005_auto_20210209_1920'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='BsfEvents',
            new_name='BsfEvent',
        ),
    ]