# Generated by Django 2.2.10 on 2020-05-31 08:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('finder', '0046_merge_20200527_2048'),
    ]

    operations = [
        migrations.AlterField(
            model_name='call',
            name='callTitle',
            field=models.CharField(max_length=500),
        ),
        migrations.AlterField(
            model_name='call',
            name='status',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='call',
            name='sumbissionProcedure',
            field=models.CharField(max_length=100),
        ),
    ]
