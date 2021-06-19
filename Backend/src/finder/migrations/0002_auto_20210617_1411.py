# Generated by Django 3.0.5 on 2021-06-17 14:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('finder', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='EuCalls',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('CallID', models.IntegerField(null=True, unique=True)),
                ('ccm2Id', models.IntegerField(default=1, unique=True)),
                ('organizationName', models.CharField(blank=True, max_length=200, null=True)),
                ('information', models.CharField(blank=True, max_length=200, null=True)),
                ('title', models.CharField(blank=True, max_length=200, null=True)),
                ('areaOfResearch', models.CharField(blank=True, max_length=200, null=True)),
                ('link', models.CharField(blank=True, max_length=200, null=True)),
                ('deadlineDate', models.DateField(blank=True, max_length=200, null=True)),
                ('open', models.BooleanField(default=False, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='MapIdsEU',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('originalID', models.IntegerField(unique=True)),
                ('indexID', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='MapIdsTechnion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('originalID', models.IntegerField(unique=True)),
                ('indexID', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='TechnionCalls',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('CallID', models.IntegerField(null=True, unique=True)),
                ('deadlineDate', models.DateField(blank=True, max_length=200, null=True)),
                ('organizationName', models.CharField(blank=True, max_length=200, null=True)),
                ('information', models.CharField(blank=True, max_length=200, null=True)),
                ('areaOfResearch', models.CharField(blank=True, max_length=200, null=True)),
                ('link', models.CharField(blank=True, max_length=200, null=True)),
                ('open', models.BooleanField(default=False, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='UpdateTime',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('eu_update', models.IntegerField()),
                ('technion_update', models.IntegerField()),
                ('bsf_update', models.IntegerField()),
                ('isf_update', models.IntegerField()),
                ('mst_update', models.IntegerField()),
                ('innovation_update', models.IntegerField()),
                ('ID', models.IntegerField(default=1, unique=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='emailsubscription',
            name='status',
        ),
        migrations.AddField(
            model_name='emailsubscription',
            name='organizationName',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='emailsubscription',
            name='ID',
            field=models.IntegerField(unique=True),
        ),
    ]
