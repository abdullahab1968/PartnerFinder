from django.contrib import admin

# Register your models here.
# from .models import Finder

# admin.site.register(Finder)

from .models import OrganizationProfile, Address, Tag, Event, Participants, TagP\
    , Location, Scores,IsfCalls,InnovationCalls, MstCalls, bsfCalls, EmailSubscription

admin.site.register(OrganizationProfile)
admin.site.register(Address)
admin.site.register(Tag)
admin.site.register(Event)
admin.site.register(Participants)
admin.site.register(TagP)
admin.site.register(Location)
admin.site.register(Scores)
admin.site.register(bsfCalls)
admin.site.register(IsfCalls)
admin.site.register(InnovationCalls)
admin.site.register(MstCalls)
admin.site.register(EmailSubscription)