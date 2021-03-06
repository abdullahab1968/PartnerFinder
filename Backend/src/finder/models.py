from djongo import models


class Address(models.Model):
    """
    class to define the data model of organization's address.
    """

    country = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.country + ' ' + self.city


class MapIds(models.Model):
    """
    class to define the data model of mapping between organization id and document id that
    relates to this organization in the inverted index
    """
    originalID = models.IntegerField(unique=True)
    indexID = models.IntegerField()


class OrganizationProfile(models.Model):
    """
    class to define the data model of Organization profile which contains the necessary fields.
    """
    pic = models.IntegerField(unique=True)
    legalName = models.CharField(max_length=200)
    businessName = models.CharField(max_length=200)
    classificationType = models.CharField(max_length=50, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    address = models.OneToOneField(
        Address, blank=True, null=True, on_delete=models.CASCADE)
    dataStatus = models.CharField(max_length=200, default='')
    numberOfProjects = models.IntegerField(default=0)
    consorsiumRoles = models.BooleanField(default=False)
    collaborations = models.IntegerField(default=0)

    def __str__(self):
        return str(self.pic)


class AlertsSettings(models.Model):
    """
    class to define the data model of Alerts Settings.
    """
    email = models.EmailField(max_length=300, blank=True, default='ishai@freemindconsultants.com')
    turned_on = models.BooleanField(default=False)
    ID = models.IntegerField(unique=True, default=1)

    def __str__(self):
        return self.email


class UpdateSettings(models.Model):
    """
    class to define the data model of Update Settings.
    """
    eu_last_update = models.IntegerField()
    b2match_last_update = models.IntegerField()
    ID = models.IntegerField(unique=True, default=1)

    def __str__(self):
        return self.eu_last_update + ' ' + self.b2match_last_update


class Tag(models.Model):
    """
    class to define the data model of the tags in the DB.
    """
    tag = models.CharField(max_length=200, blank=True, null=True)
    organizations = models.ManyToManyField(
        OrganizationProfile, blank=True, related_name='tagsAndKeywords')

    def __str__(self):
        return self.tag


class Call(models.Model):
    """
    class to define the data model of proposal call from the EU DB
    """
    ccm2Id = models.IntegerField(unique=True)
    deadlineDate = models.IntegerField()
    type = models.IntegerField()
    identifier = models.CharField(max_length=200)
    status = models.CharField(max_length=100)
    sumbissionProcedure = models.CharField(max_length=100)
    title = models.CharField(max_length=500)
    callTitle = models.CharField(max_length=500)
    hasConsortium = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class CallTag(models.Model):
    """
    class to define the data model of the EU calls tags.
    """
    tag = models.CharField(max_length=200, blank=True, null=True)
    calls = models.ManyToManyField(
        Call, blank=True, related_name='tagsAndKeywords')

    def __str__(self):
        return self.tag


class Location(models.Model):
    location = models.CharField(max_length=200, blank=True)

    # participant = models.(Participants, blank=True, null=True, on_delete=models.CASCADE, related_name='locationA')
    def __str__(self):
        return self.location


class MapIDsB2match(models.Model):
    originalID = models.IntegerField(unique=True)
    indexID = models.IntegerField(unique=True)


class MapIDsB2matchUpcoming(models.Model):
    originalID = models.IntegerField(unique=True)
    indexID = models.IntegerField(unique=True)


class Participants(models.Model):
    """
        Participants from B2MATCH events contains: name, organization name, location, organization url,
        org icon url and description
        NOTE: may contain empty fields
    """
    participant_name = models.CharField(max_length=200)
    organization_name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)

    location = models.OneToOneField(Location, on_delete=models.CASCADE)
    participant_img_url = models.CharField(
        max_length=200, blank=True, null=True)
    org_type = models.CharField(max_length=200, blank=True, null=True)
    org_icon_url = models.CharField(max_length=200, blank=True, null=True)
    org_url = models.CharField(max_length=200, blank=True, null=True)

    # tags = models.ManyToManyField(TagP,related_name='participants_tags')

    def __str__(self):
        return self.participant_name


class TagP(models.Model):
    tag = models.CharField(max_length=200, blank=True, null=True)
    participant = models.ManyToManyField(Participants, blank=True, related_name='tagsAndKeywordsP')

    def __str__(self):
        return self.tag


class Event(models.Model):
    """
        Event Object which contains Event name, url and if the event is up coming or from the past
    """
    event_name = models.CharField(max_length=200, unique=True)
    event_url = models.CharField(max_length=200)
    event_date = models.DateField(blank=True, null=True)
    is_upcoming = models.BooleanField(default=False, null=True)
    event_part = models.ManyToManyField(Participants, blank=True, related_name='Part_Event')

    def __str__(self):
        return self.event_name

class Scores(models.Model):
    """
    Score model for RES, Countries and Org type (for B2MATCH)
    """
    RES = models.FloatField(null=True, default=0)

    # Countries
    Italy = models.FloatField(null=True, default=0)

    France = models.FloatField(null=True, default=0)

    Austria = models.FloatField(null=True, default=0)

    Germany = models.FloatField(null=True, default=0)

    Denmark = models.FloatField(null=True, default=0)

    Czech_Republic = models.FloatField(null=True, default=0)

    Finland = models.FloatField(null=True, default=0)

    Ireland = models.FloatField(null=True, default=0)

    Israel = models.FloatField(null=True, default=0)

    Portugal = models.FloatField(null=True, default=0)

    Ukranie = models.FloatField(null=True, default=0)

    United_Kingdom = models.FloatField(null=True, default=0)

    Turkey = models.FloatField(null=True, default=0)

    Switzerland = models.FloatField(null=True, default=0)

    Spain = models.FloatField(null=True, default=0)

    Norway = models.FloatField(null=True, default=0)

    # Types

    Association_Agency = models.FloatField(null=True, default=0)

    University = models.FloatField(null=True, default=0)

    Company = models.FloatField(null=True, default=0)

    R_D_Institution = models.FloatField(null=True, default=0)

    Start_Up = models.FloatField(null=True, default=0)

    Others = models.FloatField(null=True, default=0)


class EventsForAlerts(models.Model):
    """
    Event result of alerts
    """
    event_name = models.CharField(max_length=200, unique=True)
    event_url = models.CharField(max_length=200)
    event_score = models.FloatField(blank=False, null=False)
    event_date = models.DateField(blank=True, null=True)


class IsfCalls(models.Model):
   """
   ISF Website Calls
   """
   CallID = models.IntegerField(unique=True, null=True)
   organizationName = models.CharField(max_length=200, blank=True, null=True)
   status = models.CharField(max_length=200, blank=True, null=True)
   registrationDeadline = models.CharField(max_length=200, blank=True, null=True)
   submissionDeadline = models.CharField(max_length=200, blank=True, null=True)
   institutionType = models.CharField(max_length=200, blank=True, null=True)
   numberOfPartners = models.CharField(max_length=200,blank=True, null=True)
   grantPeriod = models.CharField(max_length=200,blank=True, null=True)
   budget = models.CharField(max_length=200, blank=True, null=True)
   information = models.CharField(max_length=200, blank=True, null=True)
   deadlineDate = models.DateField(max_length=200, blank=True, null=True)
   link = models.CharField(max_length=200, blank=True, null=True)
   open = models.BooleanField(default=False, null=True)


   def __str__(self):
       return self.organizationName

class InnovationCalls(models.Model):
   """
   Innovation Israel Website Calls
   """

   CallID = models.IntegerField(unique=True, null=True)
   organizationName = models.CharField(max_length=200, blank=True, null=True)
   registrationDeadline = models.CharField(max_length=200, blank=True, null=True)
   submissionDeadline = models.CharField(max_length=200, blank=True, null=True)
   information = models.CharField(max_length=200, blank=True, null=True)
   areaOfResearch = models.CharField(max_length=200, blank=True, null=True)
   link = models.CharField(max_length=200, blank=True, null=True)
   deadlineDate = models.DateField(max_length=200, blank=True, null=True)
   open = models.BooleanField(default=False, null=True)


   def __str__(self):
       return self.organizationName


class MstCalls(models.Model):
   """
    Israel  ministry of science and technology website calls
   """

   CallID = models.IntegerField(unique=True, null=True)
   organizationName = models.CharField(max_length=200, blank=True, null=True)
   submissionDeadline = models.CharField(max_length=200, blank=True, null=True)
   information = models.CharField(max_length=200, blank=True, null=True)
   link = models.CharField(max_length=200, blank=True, null=True)
   deadlineDate = models.DateField(max_length=200, blank=True, null=True)
   open = models.BooleanField(default=False, null=True)

   def __str__(self):
       return self.organizationName


class bsfCalls(models.Model):
   """
   BSF Website Calls
   """
   CallID = models.IntegerField(unique=True, null=True)
   deadlineDate = models.DateField(max_length=200, blank=True, null=True)
   organizationName = models.CharField(max_length=200, blank=True, null=True)
   information = models.CharField(max_length=200, blank=True, null=True)
   areaOfResearch = models.CharField(max_length=200, blank=True, null=True)
   link = models.CharField(max_length=200, blank=True, null=True)
   open = models.BooleanField(default=False, null=True)

   def __str__(self):
       return self.organizationName

class TechnionCalls(models.Model):

   """
   Technion Website Calls
   """
   CallID = models.IntegerField(unique=True, null=True)
   deadlineDate = models.DateField(max_length=200, blank=True, null=True)
   organizationName = models.CharField(max_length=200, blank=True, null=True)
   information = models.CharField(max_length=200, blank=True, null=True)
   areaOfResearch = models.CharField(max_length=200, blank=True, null=True)
   link = models.CharField(max_length=200, blank=True, null=True)
   open = models.BooleanField(default=False, null=True)

   def __str__(self):
       return self.organizationName


class EuCalls(models.Model):
   """
    EU website calls
   """

   CallID = models.IntegerField(unique=True, null=True)
   ccm2Id = models.IntegerField(unique=True, default=1)
   organizationName = models.CharField(max_length=200, blank=True, null=True)
   information = models.CharField(max_length=200, blank=True, null=True)
   title = models.CharField(max_length=200, blank=True, null=True)
   areaOfResearch = models.CharField(max_length=200, blank=True, null=True)
   link = models.CharField(max_length=200, blank=True, null=True)
   deadlineDate = models.DateField(max_length=200, blank=True, null=True)
   open = models.BooleanField(default=False, null=True)

   def __str__(self):
       return self.organizationName


class MapIdsBSF(models.Model):
    """
    class to define the data model of mapping between organization id and document id that
    relates to this organization in the inverted index
    """
    originalID = models.IntegerField(unique=True)
    indexID = models.IntegerField()

class MapIdsISF(models.Model):
    """
    class to define the data model of mapping between organization id and document id that
    relates to this organization in the inverted index
    """
    originalID = models.IntegerField(unique=True)
    indexID = models.IntegerField()

class MapIdsMST(models.Model):
    """
    class to define the data model of mapping between organization id and document id that
    relates to this organization in the inverted index
    """
    originalID = models.IntegerField(unique=True)
    indexID = models.IntegerField()

class MapIdsINNOVATION(models.Model):
    """
    class to define the data model of mapping between organization id and document id that
    relates to this organization in the inverted index
    """
    originalID = models.IntegerField(unique=True)
    indexID = models.IntegerField()


class MapIdsTechnion(models.Model):
    """
    class to define the data model of mapping between organization id and document id that
    relates to this organization in the inverted index
    """
    originalID = models.IntegerField(unique=True)
    indexID = models.IntegerField()


class MapIdsEU(models.Model):
    """
    class to define the data model of mapping between organization id and document id that
    relates to this organization in the inverted index
    """
    originalID = models.IntegerField(unique=True)
    indexID = models.IntegerField()


class EmailSubscription(models.Model):

    """
    class to define the data model of email subscription settings.
    """

    ID = models.IntegerField(unique=True, null=False, blank= False)
    email = models.EmailField(max_length=300, blank=True)
    organizationName = models.CharField(max_length=200, blank=True, null=True)

class UpdateTime(models.Model):

    """
    class to define the data model of Update Settings.
    """
    eu_update = models.IntegerField()
    technion_update = models.IntegerField()
    bsf_update = models.IntegerField()
    isf_update = models.IntegerField()
    mst_update = models.IntegerField()
    innovation_update = models.IntegerField()
    ID = models.IntegerField(unique=True, default=1)

#*******************************************Temporarily models******************************************************

class IsfCalls1(models.Model):
   """
   ISF Website Calls
   """
   CallID = models.IntegerField(unique=True, null=True)
   organizationName = models.CharField(max_length=200, blank=True, null=True)
   status = models.CharField(max_length=200, blank=True, null=True)
   registrationDeadline = models.CharField(max_length=200, blank=True, null=True)
   submissionDeadline = models.CharField(max_length=200, blank=True, null=True)
   institutionType = models.CharField(max_length=200, blank=True, null=True)
   numberOfPartners = models.CharField(max_length=200,blank=True, null=True)
   grantPeriod = models.CharField(max_length=200,blank=True, null=True)
   budget = models.CharField(max_length=200, blank=True, null=True)
   information = models.CharField(max_length=200, blank=True, null=True)
   deadlineDate = models.DateField(max_length=200, blank=True, null=True)
   link = models.CharField(max_length=200, blank=True, null=True)
   open = models.BooleanField(default=False, null=True)


   def __str__(self):
       return self.organizationName

class InnovationCalls1(models.Model):
   """
   Innovation Israel Website Calls
   """

   CallID = models.IntegerField(unique=True, null=True)
   organizationName = models.CharField(max_length=200, blank=True, null=True)
   registrationDeadline = models.CharField(max_length=200, blank=True, null=True)
   submissionDeadline = models.CharField(max_length=200, blank=True, null=True)
   information = models.CharField(max_length=200, blank=True, null=True)
   areaOfResearch = models.CharField(max_length=200, blank=True, null=True)
   link = models.CharField(max_length=200, blank=True, null=True)
   deadlineDate = models.DateField(max_length=200, blank=True, null=True)
   open = models.BooleanField(default=False, null=True)


   def __str__(self):
       return self.organizationName


class MstCalls1(models.Model):
   """
    Israel  ministry of science and technology website calls
   """

   CallID = models.IntegerField(unique=True, null=True)
   organizationName = models.CharField(max_length=200, blank=True, null=True)
   submissionDeadline = models.CharField(max_length=200, blank=True, null=True)
   information = models.CharField(max_length=200, blank=True, null=True)
   link = models.CharField(max_length=200, blank=True, null=True)
   deadlineDate = models.DateField(max_length=200, blank=True, null=True)
   open = models.BooleanField(default=False, null=True)

   def __str__(self):
       return self.organizationName


class bsfCalls1(models.Model):
   """
   BSF Website Calls
   """
   CallID = models.IntegerField(unique=True, null=True)
   deadlineDate = models.DateField(max_length=200, blank=True, null=True)
   organizationName = models.CharField(max_length=200, blank=True, null=True)
   information = models.CharField(max_length=200, blank=True, null=True)
   areaOfResearch = models.CharField(max_length=200, blank=True, null=True)
   link = models.CharField(max_length=200, blank=True, null=True)
   open = models.BooleanField(default=False, null=True)

   def __str__(self):
       return self.organizationName

class TechnionCalls1(models.Model):

   """
   Technion Website Calls
   """
   CallID = models.IntegerField(unique=True, null=True)
   deadlineDate = models.DateField(max_length=200, blank=True, null=True)
   organizationName = models.CharField(max_length=200, blank=True, null=True)
   information = models.CharField(max_length=200, blank=True, null=True)
   areaOfResearch = models.CharField(max_length=200, blank=True, null=True)
   link = models.CharField(max_length=200, blank=True, null=True)
   open = models.BooleanField(default=False, null=True)

   def __str__(self):
       return self.organizationName


class EuCalls1(models.Model):
   """
    EU website calls
   """

   CallID = models.IntegerField(unique=True, null=True)
   ccm2Id = models.IntegerField(unique=True, default=1)
   organizationName = models.CharField(max_length=200, blank=True, null=True)
   information = models.CharField(max_length=200, blank=True, null=True)
   title = models.CharField(max_length=200, blank=True, null=True)
   areaOfResearch = models.CharField(max_length=200, blank=True, null=True)
   link = models.CharField(max_length=200, blank=True, null=True)
   deadlineDate = models.DateField(max_length=200, blank=True, null=True)
   open = models.BooleanField(default=False, null=True)

   def __str__(self):
       return self.organizationName

