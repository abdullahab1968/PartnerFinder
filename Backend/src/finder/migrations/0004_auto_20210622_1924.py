# Generated by Django 3.0.5 on 2021-06-22 19:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('finder', '0003_bsfcalls1_eucalls1_innovationcalls1_isfcalls1_mapidsbsf1_mapidseu1_mapidsinnovation1_mapidsisf1_mapi'),
    ]

    operations = [
        migrations.DeleteModel(
            name='MapIdsBSF1',
        ),
        migrations.DeleteModel(
            name='MapIdsEU1',
        ),
        migrations.DeleteModel(
            name='MapIdsINNOVATION1',
        ),
        migrations.DeleteModel(
            name='MapIdsISF1',
        ),
        migrations.DeleteModel(
            name='MapIdsMST1',
        ),
        migrations.DeleteModel(
            name='MapIdsTechnion1',
        ),
    ]
