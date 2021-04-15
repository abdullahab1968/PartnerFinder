# Generated by Django 3.0.5 on 2021-04-14 22:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('country', models.CharField(blank=True, max_length=200)),
                ('city', models.CharField(blank=True, max_length=200, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='AlertsSettings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(blank=True, default='ishai@freemindconsultants.com', max_length=300)),
                ('turned_on', models.BooleanField(default=False)),
                ('ID', models.IntegerField(default=1, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='BsfCall',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('CallID', models.IntegerField(null=True, unique=True)),
                ('deadlineDate', models.DateField(blank=True, max_length=200, null=True)),
                ('organizationName', models.CharField(blank=True, max_length=200, null=True)),
                ('information', models.CharField(blank=True, max_length=200, null=True)),
                ('areaOfResearch', models.CharField(blank=True, max_length=200, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Call',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ccm2Id', models.IntegerField(unique=True)),
                ('deadlineDate', models.IntegerField()),
                ('type', models.IntegerField()),
                ('identifier', models.CharField(max_length=200)),
                ('status', models.CharField(max_length=100)),
                ('sumbissionProcedure', models.CharField(max_length=100)),
                ('title', models.CharField(max_length=500)),
                ('callTitle', models.CharField(max_length=500)),
                ('hasConsortium', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='EventsForAlerts',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event_name', models.CharField(max_length=200, unique=True)),
                ('event_url', models.CharField(max_length=200)),
                ('event_score', models.FloatField()),
                ('event_date', models.DateField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='InnovationCalls',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('organizationName', models.CharField(blank=True, max_length=200, null=True)),
                ('registrationDeadline', models.CharField(blank=True, max_length=200, null=True)),
                ('submissionDeadline', models.CharField(blank=True, max_length=200, null=True)),
                ('information', models.CharField(blank=True, max_length=200, null=True)),
                ('areaOfResearch', models.CharField(blank=True, max_length=200, null=True)),
                ('link', models.CharField(blank=True, max_length=200, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='IsfCalls',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('organizationName', models.CharField(blank=True, max_length=200, null=True)),
                ('status', models.CharField(blank=True, max_length=200, null=True)),
                ('registrationDeadline', models.CharField(blank=True, max_length=200, null=True)),
                ('submissionDeadline', models.CharField(blank=True, max_length=200, null=True)),
                ('institutionType', models.CharField(blank=True, max_length=200, null=True)),
                ('numberOfPartners', models.CharField(blank=True, max_length=200, null=True)),
                ('grantPeriod', models.CharField(blank=True, max_length=200, null=True)),
                ('budget', models.CharField(blank=True, max_length=200, null=True)),
                ('information', models.CharField(blank=True, max_length=200, null=True)),
                ('deadline', models.CharField(blank=True, max_length=200, null=True)),
                ('link', models.CharField(blank=True, max_length=200, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('location', models.CharField(blank=True, max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='MapIds',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('originalID', models.IntegerField(unique=True)),
                ('indexID', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='MapIDsB2match',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('originalID', models.IntegerField(unique=True)),
                ('indexID', models.IntegerField(unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='MapIDsB2matchUpcoming',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('originalID', models.IntegerField(unique=True)),
                ('indexID', models.IntegerField(unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='MapIdsBSF',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('originalID', models.IntegerField(unique=True)),
                ('indexID', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='MapIdsINNOVATION',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('originalID', models.IntegerField(unique=True)),
                ('indexID', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='MapIdsISF',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('originalID', models.IntegerField(unique=True)),
                ('indexID', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='MapIdsMSF',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('originalID', models.IntegerField(unique=True)),
                ('indexID', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='MstCalls',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('organizationName', models.CharField(blank=True, max_length=200, null=True)),
                ('submissionDeadline', models.CharField(blank=True, max_length=200, null=True)),
                ('information', models.CharField(blank=True, max_length=200, null=True)),
                ('link', models.CharField(blank=True, max_length=200, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='OrganizationProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pic', models.IntegerField(unique=True)),
                ('legalName', models.CharField(max_length=200)),
                ('businessName', models.CharField(max_length=200)),
                ('classificationType', models.CharField(blank=True, max_length=50, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('dataStatus', models.CharField(default='', max_length=200)),
                ('numberOfProjects', models.IntegerField(default=0)),
                ('consorsiumRoles', models.BooleanField(default=False)),
                ('collaborations', models.IntegerField(default=0)),
                ('address', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='finder.Address')),
            ],
        ),
        migrations.CreateModel(
            name='Participants',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('participant_name', models.CharField(max_length=200)),
                ('organization_name', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True, null=True)),
                ('participant_img_url', models.CharField(blank=True, max_length=200, null=True)),
                ('org_type', models.CharField(blank=True, max_length=200, null=True)),
                ('org_icon_url', models.CharField(blank=True, max_length=200, null=True)),
                ('org_url', models.CharField(blank=True, max_length=200, null=True)),
                ('location', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='finder.Location')),
            ],
        ),
        migrations.CreateModel(
            name='Scores',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('RES', models.FloatField(default=0, null=True)),
                ('Italy', models.FloatField(default=0, null=True)),
                ('France', models.FloatField(default=0, null=True)),
                ('Austria', models.FloatField(default=0, null=True)),
                ('Germany', models.FloatField(default=0, null=True)),
                ('Denmark', models.FloatField(default=0, null=True)),
                ('Czech_Republic', models.FloatField(default=0, null=True)),
                ('Finland', models.FloatField(default=0, null=True)),
                ('Ireland', models.FloatField(default=0, null=True)),
                ('Israel', models.FloatField(default=0, null=True)),
                ('Portugal', models.FloatField(default=0, null=True)),
                ('Ukranie', models.FloatField(default=0, null=True)),
                ('United_Kingdom', models.FloatField(default=0, null=True)),
                ('Turkey', models.FloatField(default=0, null=True)),
                ('Switzerland', models.FloatField(default=0, null=True)),
                ('Spain', models.FloatField(default=0, null=True)),
                ('Norway', models.FloatField(default=0, null=True)),
                ('Association_Agency', models.FloatField(default=0, null=True)),
                ('University', models.FloatField(default=0, null=True)),
                ('Company', models.FloatField(default=0, null=True)),
                ('R_D_Institution', models.FloatField(default=0, null=True)),
                ('Start_Up', models.FloatField(default=0, null=True)),
                ('Others', models.FloatField(default=0, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='UpdateSettings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('eu_last_update', models.IntegerField()),
                ('b2match_last_update', models.IntegerField()),
                ('ID', models.IntegerField(default=1, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='TagP',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tag', models.CharField(blank=True, max_length=200, null=True)),
                ('participant', models.ManyToManyField(blank=True, related_name='tagsAndKeywordsP', to='finder.Participants')),
            ],
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tag', models.CharField(blank=True, max_length=200, null=True)),
                ('organizations', models.ManyToManyField(blank=True, related_name='tagsAndKeywords', to='finder.OrganizationProfile')),
            ],
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event_name', models.CharField(max_length=200, unique=True)),
                ('event_url', models.CharField(max_length=200)),
                ('event_date', models.DateField(blank=True, null=True)),
                ('is_upcoming', models.BooleanField(default=False, null=True)),
                ('event_part', models.ManyToManyField(blank=True, related_name='Part_Event', to='finder.Participants')),
            ],
        ),
        migrations.CreateModel(
            name='CallTag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tag', models.CharField(blank=True, max_length=200, null=True)),
                ('calls', models.ManyToManyField(blank=True, related_name='tagsAndKeywords', to='finder.Call')),
            ],
        ),
    ]
