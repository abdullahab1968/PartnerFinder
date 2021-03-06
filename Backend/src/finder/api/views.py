import datetime
import traceback
from dateutil.parser import parse
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from time import sleep
from ..models import Event, TagP, Participants, Location, MapIDsB2match, \
    MapIDsB2matchUpcoming, Scores, UpdateSettings, AlertsSettings, IsfCalls, InnovationCalls, MstCalls,bsfCalls, \
     TechnionCalls, EuCalls,MapIdsTechnion, MapIdsISF, MapIdsINNOVATION, MapIdsMST, MapIdsBSF, MapIdsEU,Call, \
    OrganizationProfile, MapIds, CallTag, EmailSubscription,UpdateTime

from .serializers import OrganizationProfileSerializer, AddressSerializer, TagSerializer, EventSerializer, \
    ParticipantsSerializer, CallSerializer, CallTagSerializer, \
    AlertsSettingsSerializer, UpdateSettingsSerializer, ScoresSerializer, \
    EventsForAlertsSerializer, IsfCallsSerializer, InnovationCallsSerializer\
    , MstCallsSerializer, BsfCallsSerializer, TechnionCallsSerializer, EuCallsSerializer,\
    EmailSubscriptionSerializer, UpdateTimeSerializer

import json

import operator
from bs4 import BeautifulSoup
from selenium import webdriver

from celery.schedules import crontab

from .EU import *
from .B2MATCH import *
from .BSF import *
from .ISF import *
from.Innovation import *
from .MST import *
from .Technion import *
from .EUCALLS import *
from .QueryProcess import *
from .emails import *
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from urllib.request import urlopen as req
import re
import os
import pytz
from ..tasks import bsf_update_task, isf_update_task, innovation_update_task, mst_update_task, technion_update_task, eu_update_task


class OrganizationProfileViewSet(viewsets.ModelViewSet):
    queryset = OrganizationProfile.objects.all()
    permission_classes = [
        permissions.AllowAny
    ]
    serializer_class = OrganizationProfileSerializer

    @action(detail=False, methods=['GET'])
    def update_organizations(self, request):
        """
        method to define API to update organizations in the local DB
        :param request: HTTP request
        :return: HTTP Response
        """

        print("*" * 50, "\nSTART UPDATING EU DB\n", "*" * 50)
        print("HERE")

        try:
            try:
                index = load_index('EU_Index')
                # if os.path.exists('EU_Index_Temp.0') and os.path.getsize('EU_Index_Temp.0') > os.path.getsize(
                #         'EU_Index.0'):
                #     destroy_and_rename(old_index_name='EU_Index', new_index_name='EU_Index_Temp')
                # else:
                index.destroy()
            except:
                pass
            try:
                dictionary = load_dictionary("Dictionary")
                os.remove("Dictionary")
            except:
                pass

            index = build_index('EU_Index', 'EU')
            MapIds.objects.all().delete()
            queue_status = {}
            graph = Graph()
            visitngQueue = collections.deque()
            startOrg = '999993953'
            visitngQueue.append(startOrg)
            queue_status[startOrg] = 'visiting'
            while len(visitngQueue) > 0:
                currPic = visitngQueue.popleft()
                print("CURR", currPic)
                try:
                    currOrg = get_organization_profile_by_pic(currPic)
                    currAdjacent = get_pics_from_collaborations(
                        currOrg['collaborations'])
                except:
                    continue
                for pic in currAdjacent:
                    if pic not in graph.vertices or queue_status[pic] == 'notVisited':
                        graph.add(currPic, pic)
                        queue_status[pic] = 'visiting'
                        visitngQueue.append(pic)

                currOrg = translate_data(currOrg)
                print("AFTER TRANSLATE", currOrg['pic'])
                add_organization_to_DB(currOrg)
                print("AFTER ADD")
                index = add_org_to_index(index, currOrg)
                print("ADDED TO INDEX")
                queue_status[currPic] = 'visited'

            # if os.path.exists('EU_Index_Temp.0') and os.path.getsize('EU_Index_Temp.0') > os.path.getsize('EU_Index.0'):
            #     destroy_and_rename(old_index_name='EU_Index', new_index_name='EU_Index_Temp')
            # else:
            #     index.destroy()

            response = {'success': 'Organizations updated successfully!'}
            if not setUpdateSettings(euDate=time.mktime(datetime.now().timetuple())):
                raise
        except:
            setUpdateSettings(euDate=time.mktime(datetime.now().timetuple()))
            # if os.path.exists('EU_Index_Temp.0') and os.path.getsize('EU_Index_Temp.0') > os.path.getsize('EU_Index.0'):
            #     destroy_and_rename(old_index_name='EU_Index', new_index_name='EU_Index_Temp')
            # else:
            #     index.destroy()
            response = {'error': 'Error while updating organizations.'}

        return Response(response, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'])
    def generic_search(self, request):
        """
        method to define API that defines generic function to search organizations from EU and participants from B2Match
        :param request: HTTTP request with tags, countries, types, and role fields
        :return: HTTP response with the relevant objects
        """

        try:
            data = request.query_params['data']
            data = json.loads(data)
            countries = data['countries']
            types = data['types']
            tags = data['tags']
            role = data['role']
            print(data)
            EURes = get_orgs_by_parameters(tags=tags, countries=countries, types=types,
                                           role=role)
            # B2MATCHRes = getB2MATCHPartByCountriesAndTags(tags, countries)
            B2MATCHRes = []
            B2MATCH = []
            EU = []
            for val in EURes:
                EU.append({'legalName': val.legalName,
                           'country': val.address.country,
                           'description': val.description, 'classificationType': val.classificationType,
                           'dataStatus': val.dataStatus, 'numberOfProjects': val.numberOfProjects,
                           'consorsiumRoles': val.consorsiumRoles})

            for val in B2MATCHRes:
                B2MATCH.append({'participant_name': val.participant_name, 'organization_name': val.organization_name,
                                'org_type': val.org_type,
                                'address': val.location.location, 'description': val.description,
                                'participant_img': val.participant_img_url,
                                'org_url': val.org_url, 'org_icon_url': val.org_icon_url})

            response = {'EU': EU, 'B2MATCH': B2MATCH}
        except:
            response = {'EU': [], 'B2MATCH': [], 'error': 'Error while searching for organizations and participants'}

        return Response(response, status=status.HTTP_200_OK)


class AlertsSettingsViewSet(viewsets.ModelViewSet):
    queryset = AlertsSettings.objects.all()
    permission_classes = [
        permissions.AllowAny
    ]
    serializer_class = AlertsSettingsSerializer

    @action(detail=False, methods=['GET'])
    def get_settings(self, request):
        """
        method to define API to get alerts settings
        :param request: HTTP request
        :return: HTTP Response
        """
        try:
            alertsSettings = AlertsSettings.objects.all()[0]
            response = {'email': alertsSettings.email,
                        'turned_on': alertsSettings.turned_on}
        except:
            response = {'email': '', 'turned_on': '', 'error': 'Error while uploading alerts settings'}

        return Response(response, status=status.HTTP_200_OK)

    @action(detail=False, methods=['POST'])
    def set_settings(self, request):
        """
        method to define API to update the alerts settings
        :param request: HTTP request with updated email and turned_on flag
        :return: HTTP response
        """

        try:
            data = request.query_params['data']
            data = json.loads(data)
            email = data['email']
            turned_on = data['turned_on']

            try:
                AlertsSettings.objects.get(ID=1)
                AlertsSettings.objects.filter(ID=1).update(email=email)
                AlertsSettings.objects.filter(ID=1).update(turned_on=turned_on)
            except:
                alertsSettings = AlertsSettings(
                    email=email, turned_on=turned_on, ID=1)
                alertsSettings.save()

            response = {'success': 'Alerts Settings Updated Successfully.'}
        except:
            response = {'error': 'Error while updating alerts settings'}

        return Response(response, status=status.HTTP_200_OK)


class UpdateSettingsViewSet(viewsets.ModelViewSet):
    queryset = UpdateSettings.objects.all()
    permission_classes = [
        permissions.AllowAny
    ]
    serializer_class = UpdateSettingsSerializer

    @action(detail=False, methods=['GET'])
    def get_settings(self, request):
        """
        method to define API to get last update times
        :param request: HTTP request
        :return: HTTP Response
        """
        try:
            updateSettings = UpdateSettings.objects.all()[0]
            response = {'EU': updateSettings.eu_last_update,
                        'B2MATCH': updateSettings.b2match_last_update}
        except:
            response = {'EU': '', 'B2MATCH': '', 'error': 'Error while uploading updates settings'}

        return Response(response, status=status.HTTP_200_OK)


class CallViewSet(viewsets.ModelViewSet):
    queryset = Call.objects.all()
    permission_classes = [
        permissions.AllowAny
    ]
    serializer_class = CallSerializer

    @action(detail=False, methods=['GET'])
    def consortium_builder(self, request):
        """
        method to define API to build a consortium for EU grants calls that have at least three months deadline and
        there are three different potential partners from at least three different countries.
        if we have at least one relevant call an email will be sent to the user
        :param request: HTTP request
        :return: HTTP Response
        """
        print('*' * 40, "Started consortium builder", '*' * 40)
        try:
            response = {'success': 'Please Turn Alerts ON!'}
            try:
                alerts_settings = AlertsSettings.objects.all()[0]
            except:
                alerts_settings['turned_on'] = False
            if not alerts_settings.turned_on:
                return Response(response, status=status.HTTP_200_OK)

            email = alerts_settings.email

            Call.objects.all().delete()
            CallTag.objects.all().delete()
            calls = get_proposal_calls()

            calls_to_send = []

            for call in calls:
                call = has_consortium(call)
                if call['hasConsortium']:
                    calls_to_send.append({'title': call['title']})
                    add_call_to_DB(call)

            body = MIMEMultipart('alternative')

            calls = ''
            for call in calls_to_send:
                calls += '<li><b>' + call['title'] + '</b>.</li>'

            signature = 'Sincerly,<br>Consortium Builder Alerts'
            html = """\
            <html>
              <head><h3>You have new proposal calls that might interest you</h3></head>
              <body>
                <ol> 
                {}
                </ol>
                <br>
                <br>
                {}
              </body>
            </html>
            """.format(calls, signature)

            content = MIMEText(html, 'html')
            body.attach(content)
            body['Subject'] = 'EU Proposal Calls Alert'
            if len(calls_to_send) > 0:
                send_mail(receiver_email=email, message=body)
            response = {'success': 'Finished building consortium successfully!'}
        except:
            response = {'error': 'Error while building consortium.'}

        return Response(response, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'])
    def get_calls(self, request):
        """
        method to define API to get all calls that has a potential participants
        :param request: HTTP request
        :return: HTTP Response
        """
        response = {'calls': []}
        try:
            calls = Call.objects.all()
            res = []
            for call in calls:
                res.append({'type': call.type, 'status': call.status, 'ccm2Id': call.ccm2Id,
                            'identifier': call.identifier, 'title': call.title,
                            'callTitle': call.callTitle, 'deadlineDate': call.deadlineDate,
                            'sumbissionProcedure': call.sumbissionProcedure})
            response['calls'] = res
        except:
            response = {'error': 'Error while uploading consortium calls', 'calls': []}

        return Response(response, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'])
    def search_organizations(self, request):
        """
        method to define API to search for organizations for a specific ccm2id call
        :param request: HTTP request
        :return: HTTP Response
        """
        try:
            data = request.query_params['data']
            data = json.loads(data)
            id = int(data['ccm2Id'])
            call = Call.objects.get(ccm2Id=id)
            tags = CallTag.objects.filter(calls=call)
            tagsList = []
            for tag in tags:
                tagsList.append(tag.tag)

            EURes = get_orgs_by_parameters(tags=tagsList, countries=[], types=[], role='')
            EU = []
            for val in EURes:
                EU.append({'legalName': val.legalName,
                           'country': val.address.country,
                           'description': val.description, 'classificationType': val.classificationType,
                           'dataStatus': val.dataStatus, 'numberOfProjects': val.numberOfProjects,
                           'consorsiumRoles': val.consorsiumRoles})

            response = {'EU': EU}
        except:
            response = {'EU': [], 'error': 'Error while uploading organizations.'}

        return Response(response, status=status.HTTP_200_OK)


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    permission_classes = [
        permissions.AllowAny
    ]
    serializer_class = EventSerializer

    def create(self, request, *args, **kwargs):
        return Response({'message': 'cant add event like that'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['POST'])
    def add_all_events(self, request):
        """
                method to define API to iimport all the events from B2MATCH and save it to the local DB
        """
        Event.objects.all().delete()
        TagP.objects.all().delete()
        Participants.objects.all().delete()
        MapIDsB2matchUpcoming.objects.all().delete()
        MapIDsB2match.objects.all().delete()
        Location.objects.all().delete()
        setUpdateSettings(b2matchDate=time.mktime(datetime.now().timetuple()))
        try:
            all_event_b2match = "https://events.b2match.com/?all=true"
            b2match = "https://events.b2match.com"
            all_events_page = requests.get(all_event_b2match)
            all_events_soup = BeautifulSoup(all_events_page.content, 'html.parser')
            itemes = all_events_soup.find_all(class_="last next")
            all_events_last_page = itemes[0].find("a")['href']
            all_events = all_events_soup.find_all(
                class_="event-card-wrapper col-sm-6 col-md-4")

            for item in all_events:
                try:
                    url = b2match + item.find("a")['href']
                except:
                    pass
                try:
                    event_title = item.find(class_="event-card-title").get_text()
                except:
                    pass
                try:
                    event_date_ = item.find(class_="event-card-date").get_text()
                    event_date_ = event_date_.upper()
                    dt = re.findall(
                        "((([0-9]{2})| ([0-9]{1}))\ (\w+)\,\ [0-9]{4})", event_date_)

                except:
                    pass

                event_date = datetime.strptime(dt[0][0], '%d %B, %Y')

                url = get_the_participent_urls(url)
                upComing = False
                CurrentDate = datetime.now()
                if CurrentDate < event_date:
                    upComing = True

                event = Event(event_name=event_title, event_url=url,
                              event_date=event_date, is_upcoming=upComing)
                event.save()

            curr_page = "/?all=true&page="
            i = 2
            while 1:
                all_events_page = requests.get(b2match + curr_page + str(i))
                all_events_soup = BeautifulSoup(
                    all_events_page.content, 'html.parser')
                all_events = all_events_soup.find_all(
                    class_="event-card-wrapper col-sm-6 col-md-4")
                for item in all_events:
                    try:
                        url = b2match + item.find("a")['href']
                    except:
                        pass
                    try:
                        event_title = item.find(
                            class_="event-card-title").get_text()
                    except:
                        pass

                    # newEvent = B2match_event(url,date,event_title,event_location,event_text)
                    # all_events_list.append(newEvent)
                    try:
                        event_date_ = item.find(
                            class_="event-card-date").get_text()
                        event_date_ = event_date_.upper()
                        dt = re.findall(
                            "((([0-9]{2})| ([0-9]{1}))\ (\w+)\,\ [0-9]{4})", event_date_)

                    except:
                        pass

                    event_date = datetime.strptime(dt[0][0], '%d %B, %Y')
                    try:
                        url = get_the_participent_urls(url)
                        upComing = False
                        CurrentDate = datetime.now()
                        if CurrentDate < event_date:
                            upComing = True

                        event = Event(event_name=event_title, event_url=url,
                                      event_date=event_date, is_upcoming=upComing)
                        event.save()
                    except:
                        pass

                    # all_events_list.append({"naem": event_title, "date": date, "location": event_location, "url": url, "event_text": event_text})

                if (curr_page + str(i) == all_events_last_page):
                    break

                i += 1
            res = Event.objects.all()
            response = []
            for val in res:
                response.append({'event_name': val.event_name,
                                 'event_url': val.event_url})
        except:
            response = {'error': 'Error while adding events.'}

        return Response(response, status=status.HTTP_200_OK)

    @action(detail=False, methods=['POST'])
    def update_upcoming_events(self, request):
        """
                updating upcoming events in the database <not tested yet>
        """
        print("updating....")

        try:

            os.remove("B2MATCH_upcoming_Index_temp")
            os.remove("B2MATCH_upcoming_Index_temp.0")
        except:
            pass
        try:
            newEvents = []
            upcoming_event_b2match = "https://events.b2match.com"
            b2match = "https://events.b2match.com"
            upcoming_events_page = requests.get(upcoming_event_b2match)
            upcoming_events_soup = BeautifulSoup(
                upcoming_events_page.content, 'html.parser')
            itemes = upcoming_events_soup.find_all(class_="last next")
            upcoming_events_last_page = itemes[0].find("a")['href']
            upcoming_events = upcoming_events_soup.find_all(
                class_="event-card-wrapper col-sm-6 col-md-4")

            for item in upcoming_events:
                try:
                    url = b2match + item.find("a")['href']
                except:
                    pass
                try:
                    event_title = item.find(class_="event-card-title").get_text()
                except:
                    pass
                try:
                    event_date_ = item.find(class_="event-card-date").get_text()
                    event_date_ = event_date_.upper()
                    dt = re.findall(
                        "((([0-9]{2})| ([0-9]{1}))\ (\w+)\,\ [0-9]{4})", event_date_)
                except:
                    pass

                event_date = datetime.strptime(dt[0][0], '%d %B, %Y')

                url = get_the_participent_urls(url)
                upComing = False
                CurrentDate = datetime.now()
                if CurrentDate < event_date:
                    upComing = True

                event = Event(event_name=event_title, event_url=url,
                              event_date=event_date, is_upcoming=upComing)
                newEvents.append(event)

            curr_page = "/?page="
            i = 2
            while 1:
                upcoming_events_page = requests.get(b2match + curr_page + str(i))
                upcoming_events_soup = BeautifulSoup(
                    upcoming_events_page.content, 'html.parser')
                upcoming_events = upcoming_events_soup.find_all(
                    class_="event-card-wrapper col-sm-6 col-md-4")
                for item in upcoming_events:
                    try:
                        url = b2match + item.find("a")['href']
                    except:
                        pass
                    try:
                        event_title = item.find(
                            class_="event-card-title").get_text()
                    except:
                        pass

                    # newEvent = B2match_event(url,date,event_title,event_location,event_text)
                    # all_events_list.append(newEvent)
                    try:
                        event_date_ = item.find(
                            class_="event-card-date").get_text()
                        event_date_ = event_date_.upper()
                        dt = re.findall(
                            "((([0-9]{2})| ([0-9]{1}))\ (\w+)\,\ [0-9]{4})", event_date_)

                    except:
                        pass

                    event_date = datetime.strptime(dt[0][0], '%d %B, %Y')
                    try:
                        url = get_the_participent_urls(url)
                        upComing = False
                        CurrentDate = datetime.now()
                        if CurrentDate < event_date:
                            upComing = True
                        event = Event(event_name=event_title, event_url=url,
                                      event_date=event_date, is_upcoming=upComing)
                        newEvents.append(event)
                    except:
                        pass

                if (curr_page + str(i) == upcoming_events_last_page):
                    break
                i += 1
            myEvents = list(Event.objects.filter(is_upcoming=True))

            toupdate = []
            eventNoLongerUpcoming = []
            newEvents2 = []
            for e in newEvents:
                newEvents2.append(e.event_name)

            for event in myEvents:
                if event.event_name not in newEvents2:
                    eventNoLongerUpcoming.append(event)
                else:
                    toupdate.append(event)

            changeEventStatus(eventNoLongerUpcoming)
            deleteEventsTree(toupdate)

            for e in toupdate:
                e.delete()

            for e in newEvents:
                try:
                    e.save()
                except:
                    print(e.event_name, "NAME EVENT")
                # e.save()

            add_Participants_from_Upcoming_Event()
            # delete old index and replace with new one
            deleteOldIndexAndReplace()
            if not setUpdateSettings(b2matchDate=time.mktime(datetime.now().timetuple())):
                raise
            response = {'success': 'B2MATCH repository updated successfully'}
        except:
            setUpdateSettings(b2matchDate=time.mktime(datetime.now().timetuple()))
            response = {'error': 'Error while updating B2match repository.'}

        return Response(response, status=status.HTTP_200_OK)


class ParticipantsViewSet(viewsets.ModelViewSet):
    queryset = Participants.objects.all()
    permission_classes = [
        permissions.AllowAny
    ]
    serializer_class = ParticipantsSerializer

    @action(detail=False, methods=['POST'])
    def add_Participants_from_Event(self, request):
        """
                method to define API to import all the participants from the events we have in our DB and save them to the local DB
        """
        try:
            events = Event.objects.all()
            for event in events:

                try:
                    url_arr = getParticipentFromUrl(
                        event.event_url)
                except:
                    continue
                for item in url_arr:
                    try:
                        part_temp = getParticipentDATA(item)
                    except:
                        continue
                    location = Location(location=part_temp[3])
                    location.save()
                    try:
                        participant = Participants(participant_name=part_temp[0], participant_img_url=part_temp[1],
                                                   organization_name=part_temp[2], org_type=part_temp[4],
                                                   org_url=part_temp[5],
                                                   org_icon_url=part_temp[6], description=part_temp[8],
                                                   location=location)

                        participant.save()
                        event.event_part.add(participant)
                    except:
                        continue

                    for i in part_temp[7]:
                        try:
                            currTag = TagP.objects.get(tag=i)
                            currTag.participant.add(participant)
                        except:
                            currTag = TagP(tag=i)
                            currTag.save()
                            currTag.participant.add(participant)
                    if not event.is_upcoming:
                        try:
                            # this is the path for the index
                            # index = load_index(
                            #     '/Users/mahmoodnael/PycharmProjects/PartnerFinderApril/Backend/src/B2MATCH_Index')
                            index = load_index('B2MATCH_Index')
                        except:
                            index = None

                        if index is None:
                            # this is the path for the index
                            # index = build_index(
                            #     '/Users/mahmoodnael/PycharmProjects/PartnerFinderApril/Backend/src/B2MATCH_Index')
                            index = build_index('B2MATCH_Index', 'B2MATCH')

                        index = add_par_to_index(
                            index, participant, part_temp[7], False)
                    elif event.is_upcoming:
                        try:
                            # this is the path for the index

                            # index = load_index('/Users/mahmoodnael/PycharmProjects/PartnerFinderApril/Backend/src/B2MATCH_upcoming_Index')
                            index = load_index('B2MATCH_upcoming_Index.0')
                        except:
                            index = None

                        if index is None:
                            # this is the path for the index
                            # index = build_index('/Users/mahmoodnael/PycharmProjects/PartnerFinderApril/Backend/src/B2MATCH_upcoming_Index')
                            index = build_index('B2MATCH_upcoming_Index', "B2MATCH")
                        index = add_par_to_index(
                            index, participant, part_temp[7], True)
            response = {'success': 'Adding participant successfully.'}
        except:
            response = {'error': 'Error while adding participant'}
        return Response({'message': response}, status=status.HTTP_200_OK)


class ScoresViewSet(viewsets.ModelViewSet):
    queryset = Scores.objects.all()
    permission_classes = [
        permissions.AllowAny
    ]
    serializer_class = ScoresSerializer

    def create(self, request, *args, **kwargs):
        return Response({'message': 'cant add event like that'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['POST'])
    def updatescores(self, request):
        """
        API to update scores in the data base
        :param request: scores from user about RES, countries and orgs type
        :return: the updated scores
        """
        try:
            data = request.query_params['data']
            data = json.loads(data)

            try:
                scores = Scores.objects.all()[0]
                ATTRIBUTES = {'RES', 'Italy', 'France', 'Austria', 'Germany', 'Denmark', 'Czech_Republic', 'Finland'
                    , 'Ireland', 'Israel', 'Portugal', 'Ukranie', 'United_Kingdom', 'Turkey', 'Switzerland', 'Spain'
                    , 'Norway', 'Association_Agency', 'Company', 'University', 'R_D_Institution', 'Start_Up', 'Others'}

                for atr in ATTRIBUTES:
                    setattr(scores, atr, data[atr])
            except:
                scores = Scores(RES=data['RES'],
                                Italy=data['Italy'], France=data['France'], Austria=data['Austria'],
                                Germany=data['Germany'],
                                Denmark=data['Denmark'], Czech_Republic=data['Czech_Republic'], Finland=data['Finland'],
                                Ireland=data['Ireland'], Israel=data['Israel'], Portugal=data['Portugal'],
                                Ukranie=data['Ukranie'], United_Kingdom=data['United_Kingdom'], Turkey=data['Turkey'],
                                Switzerland=data['Switzerland'], Spain=data['Spain'], Norway=data['Norway'],
                                Association_Agency=data['Association_Agency'], University=data['University'],
                                R_D_Institution=data['R_D_Institution'], Start_Up=data['Start_Up'],
                                Others=data['Others'])
            scores.save()
            response = {'Success': 'Scores updated successfully.'}
        except:
            response = {'Error': 'Error while updating scores.'}
        return Response(response, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'])
    def getscores(self, request):
        """
        API to send current scoures
        :param request:
        :return:
        """
        try:
            scores = Scores.objects.all()[0]
            response = ScoresSerializer(scores).data
        except:
            response = {'Error': 'Error while uploading scores.'}

        return Response(response, status=status.HTTP_200_OK)


class AlertsB2match(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    permission_classes = [
        permissions.AllowAny
    ]
    serializer_class = EventSerializer

    @action(detail=False, methods=['GET'])
    def alertB2match(self, request):
        """
        api for alerts sends recommnded events via mail and saves them temprorarly to the database
        :param request:
        :return:
        """
        try:
            events = Event.objects.filter(is_upcoming=True)
            myEvents = []
            for event in events:
                parts = event.event_part.all()
                count = len(parts)
                if count < 50:
                    continue
                else:
                    eventScore = getScoreForEvent(parts)
                    myEvents.append((event, eventScore))
                    updateAlertsEvents(myEvents)

            myEvents.sort(key=operator.itemgetter(1), reverse=True)
            alerts_settings = AlertsSettings.objects.all()[0]
            email = alerts_settings.email
            body = MIMEMultipart('alternative')
            ms = ''
            for ev in myEvents:
                ms += '<li><b>' + ev[0].event_name + '</b><a href="' + ev[0].event_url + '">' + ev[
                    0].event_url + '</a></li>'

            signature = 'Sincerly,<br>B2MATCH Event Alerts'
            html = """\
                    <html>
                      <head><h3>You have new events that might interest you</h3></head>
                      <body>
                        <ol> 
                        {}
                        </ol>
                        <br>
                        <br>
                        {}
                      </body>
                    </html>
                    """.format(ms, signature)

            response = {'success': 'Finished building recommended events successfully.'}

            content = MIMEText(html, 'html')
            body.attach(content)
            body['Subject'] = 'B2MATCH Events Alert'
            send_mail(receiver_email=email, message=body)
        except:
            response = {'Error': 'Error while building recommended events.'}

        return Response(response, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'])
    def getEventFromAlerts(self, request):
        """
        function to send response of events returned from alerts
        :param request:
        :return:
        """
        try:
            events = EventsForAlerts.objects.all()
            myEvents = sorted(events, key=lambda x: x.event_score, reverse=True)
            response = []
            for event in myEvents:
                date = str(event.event_date).split('T')[0]
                response.append({'event_name': event.event_name, 'event_url': event.event_url, 'date': date})
        except:
            response = {'Error': 'Error while uploading recommended events.'}

        return Response(response, status=status.HTTP_200_OK)


def setUpdateSettings(euDate=None, b2matchDate=None):
    """
    function to update the last update settings (times)
    :param euDate: EU last update
    :param b2matchDate: B2match last update
    :return: True/False
    """

    if not b2matchDate and not euDate:
        return False

    if euDate:
        euDate = int(euDate)
    if b2matchDate:
        b2matchDate = int(b2matchDate)

    try:
        UpdateSettings.objects.get(ID=1)
        if euDate:
            UpdateSettings.objects.filter(ID=1).update(eu_last_update=euDate)
        if b2matchDate:
            UpdateSettings.objects.filter(ID=1).update(
                b2match_last_update=b2matchDate)
    except:
        updateSettings = UpdateSettings(
            eu_last_update=euDate, b2match_last_update=b2matchDate, ID=1)
        updateSettings.save()

    return True


class ProposalCallsViewSet(viewsets.ModelViewSet):
    queryset = bsfCalls.objects.all()
    permission_classes = [
        permissions.AllowAny
    ]
    serializer_class = BsfCallsSerializer

    @action(detail=False, methods=['GET'])
    def call_search(self, request):

        """
        Method to define API to search for calls in the DB, that is related to the user input
        :param request: HTTP request that contain data, which is tags, dates
        :return: HTTP response

        """

        BSF, ISF, INNOVATION, MST, Technion, EU = [], [], [], [], [], []

        try:
            data = request.query_params['data']
            print("This is the data:", data)
            data = json.loads(data)
            organizations = data['organizations']
            tags = data['tags']
            from_date = data['start_date']
            to_date = data['end_date']
            call_status = data['status']


            if not organizations:
                organizations = 'BSF, ISF, INNOVATION, MST, Technion, EU'


            if call_status == 'Closed':
                from_date = ''
                to_date = ''

            today = datetime.now(pytz.timezone('Israel'))
            today_date = today.strftime("%d/%m/%Y")

            if today_date == to_date and call_status == 'Open':
                to_date = ''


            if 'BSF' in organizations:

                try:

                    bsf_result = get_bsf_call_by(tags, from_date, to_date, call_status)

                    BSF = []
                    for value in bsf_result:
                        BSF.append({
                                    'organizationName': value.organizationName,
                                    'deadlineDate': value.deadlineDate,
                                    'information': value.information,
                                    'areaOfResearch': value.areaOfResearch,
                                    'link': 'https://www.bsf.org.il/calendar/'})

                except Exception as e:
                        print(e)
                        traceback.print_exc()


            if 'ISF' in organizations:

                try:

                    Isf_result = get_Isf_call_by(tags, from_date, to_date, call_status)

                    ISF = []
                    for value in Isf_result:
                        ISF.append({
                                    'organizationName': value.organizationName,
                                    'registrationDeadline': value.registrationDeadline,
                                    'information': value.information,
                                    'institutionType': value.institutionType,
                                    'link': value.link})

                except Exception as e:
                    print(e)



            if 'INNOVATION' in organizations:

                try :

                    Innovation_result = get_Innovation_call_by(tags, from_date, to_date, call_status)

                    INNOVATION = []
                    for value in Innovation_result:
                        INNOVATION.append({
                                           'organizationName': value.organizationName,
                                           'submissionDeadline': value.submissionDeadline,
                                           'information': value.information,
                                           'areaOfResearch': value.areaOfResearch,
                                           'link': value.link})


                except Exception as e:
                    print(e)


            if 'MST' in organizations:

                try:

                    mst_result = get_Mst_call_by(tags, from_date, to_date, call_status)

                    MST = []
                    for value in mst_result:
                        MST.append({
                                    'organizationName': value.organizationName,
                                    'submissionDeadline': value.submissionDeadline,
                                    'information': value.information,
                                    'link': value.link})

                except Exception as e:
                        print(e)


            if 'Technion' in organizations:

                try:

                    technion_result = get_technion_call_by(tags, from_date, to_date, call_status)

                    Technion = []
                    for value in technion_result:
                        Technion.append({
                                        'organizationName': value.organizationName,
                                        'deadlineDate': value.deadlineDate,
                                        'information': value.information,
                                        'areaOfResearch': value.areaOfResearch,
                                        'link': value.link})

                except Exception as e:
                        print(e)


            if 'EU' in organizations:

                try:

                    eu_result = get_eu_call_by(tags, from_date, to_date, call_status)

                    EU = []
                    for value in eu_result:
                        EU.append({
                                    'organizationName': value.organizationName,
                                    'deadlineDate': value.deadlineDate,
                                    'information': value.information,
                                    'areaOfResearch': value.areaOfResearch,
                                    'link': value.link})

                except Exception as e:
                        print(e)


            response = {'BSF': BSF, 'ISF': ISF, 'INNOVATION': INNOVATION, 'MST': MST, 'Technion': Technion, 'EU': EU}

        except Exception as e:
            print(e)
            response = {'Error': 'Error while searching for calls'}

        return Response(response, status=status.HTTP_200_OK)


class BsfCallsViewSet(viewsets.ModelViewSet):
    queryset = bsfCalls.objects.all()
    permission_classes = [
        permissions.AllowAny
    ]
    serializer_class = BsfCallsSerializer

    @action(detail=False, methods=['POST'])
    def add_bsfcalls_to_db(self, request):

        """
        Method to define API add BSF calls and the generated index to the local DB
        :param request: HTTP request
        :return: HTTP response
        """

        bsfCalls.objects.all().delete()
        MapIdsBSF.objects.all().delete()
        _url = 'https://www.bsf.org.il/calendar/'
        deadline = get_events_deadline(_url) # deadline is a list of strings
        event_details = get_events_details(_url) # event_details is a list of strings
        field_name = get_field_name(_url) # field_name is a list of strings

        try:
            os.remove('C:/Users/FinalProject/Desktop/PartnerFinder/Backend/src/Index/BsfIndex')
            os.remove('C:/Users/FinalProject/Desktop/PartnerFinder/Backend/src/Index/BsfIndex.0')
            os.remove('C:/Users/FinalProject/Desktop/PartnerFinder/Backend/src/Index/Dictionary_BSF')
            print('Deleting BSF Index...')
        except:
            pass

        index = make_index('C:/Users/FinalProject/Desktop/PartnerFinder/Backend/src/Index/BsfIndex', 'BSF')
        print('Building BSF Index...')


        try:
            for i,item in enumerate (deadline):
                date = bsfCalls(CallID=i, deadlineDate=item, organizationName= 'NSF-BSF',information=event_details[i] ,areaOfResearch=field_name[i], link= 'https://www.bsf.org.il/calendar/', open=True)
                date.save()

                originalID = i
                indexID = len(index)
                document = get_document_from_bsf_call(event_details[i], field_name[i])
                newMap = MapIdsBSF(originalID=originalID, indexID=indexID)
                newMap.save()
                index = add_document_to_curr_index(index, [document], 'BSF')

            response = {'success': 'BSF calls added successfully.'}

            if not setUpdateTime(bsfDate=time.mktime(datetime.now().timetuple())):
                raise

        except Exception as e:
            print(e)
            setUpdateTime(bsfDate=time.mktime(datetime.now().timetuple()))
            response = {'error': 'Error while adding BSF calls to DB'}

        return Response(response, status=status.HTTP_200_OK)


class IsfCallsViewSet(viewsets.ModelViewSet):

    queryset = IsfCalls.objects.all()
    permission_classes = [
        permissions.AllowAny
    ]
    serializer_class = IsfCallsSerializer

    @action(detail=False, methods=['POST'])
    def add_isfcalls_to_db(self, request):

        """
       Method to define API add ISF calls and the generated index to the local DB
       :param request: HTTP request
       :return: HTTP response
       """

        IsfCalls.objects.all().delete()
        MapIdsISF.objects.all().delete()
        _url = 'https://www.isf.org.il/#/support-channels/1/10'
        name = 'Personal Research Grants'

        call_names, call_links = [], []

        try:
            os.remove('C:/Users/FinalProject/Desktop/PartnerFinder/Backend/src/Index/IsfIndex')
            os.remove('C:/Users/FinalProject/Desktop/PartnerFinder/Backend/src/Index/IsfIndex.0')
            os.remove('C:/Users/FinalProject/Desktop/PartnerFinder/Backend/src/Index/Dictionary_ISF')
            print('Deleting ISF Index...')

        except:
            pass

        index = make_index('C:/Users/FinalProject/Desktop/PartnerFinder/Backend/src/Index/IsfIndex', 'ISF')
        print('Building ISF Index...')


        try:
            call_names, call_links = get_proposal_names_links(_url, name)

        except Exception as e:
            print(e)

        try:
            for i, item in enumerate(call_names):
                call_info = get_calls_status(call_links[i], item)

                if call_info[7] == 'Closed':

                    call = IsfCalls(CallID=i, organizationName=item, status=call_info[0]
                                    , registrationDeadline=call_info[7], submissionDeadline=call_info[8],
                                    institutionType=call_info[1], numberOfPartners=call_info[2],
                                    grantPeriod=call_info[3], budget=call_info[4],
                                    information=call_info[5], deadlineDate=call_info[6], link=call_links[i], open=False)
                else:

                    call = IsfCalls(CallID= i, organizationName=item, status=call_info[0]
                                    , registrationDeadline=call_info[7], submissionDeadline=call_info[8],
                                    institutionType=call_info[1], numberOfPartners=call_info[2],
                                    grantPeriod=call_info[3], budget=call_info[4],
                                    information=call_info[5], deadlineDate=call_info[6], link=call_links[i], open=True )

                call.save()

                originalID = i
                indexID = len(index)
                document = get_document_from_isf_call(call_info[5], item)
                newMap = MapIdsISF(originalID=originalID, indexID=indexID)
                newMap.save()
                index = add_document_to_curr_index(index, [document], 'ISF')


            response = {'success': 'ISF calls added successfully.'}

            if not setUpdateTime(isfDate=time.mktime(datetime.now().timetuple())):
                raise

        except Exception as e:
            print(repr(e))
            setUpdateTime(isfDate=time.mktime(datetime.now().timetuple()))
            traceback.print_exc()

            response = {'error': 'Error while adding ISF calls to DB'}


        return Response(response, status=status.HTTP_200_OK)


class InnovCallsViewSet(viewsets.ModelViewSet):

    queryset = InnovationCalls.objects.all()
    permission_classes = [
        permissions.AllowAny
    ]
    serializer_class = InnovationCallsSerializer

    @action(detail=False, methods=['POST'])
    def add_innovcalls_to_db(self, request):

        """
         Method to define API add Innovation Israel calls and the generated index to the local DB
         :param request: HTTP request
         :return: HTTP response
         """

        InnovationCalls.objects.all().delete()
        MapIdsINNOVATION.objects.all().delete()

        _url = 'https://www.innovationisrael.org.il/en/page/calls-proposals'
        names, urls = (),()
        names_list, urls_list, date_list = [], [], []
        counter = 0

        try:
            os.remove('C:/Users/FinalProject/Desktop/PartnerFinder/Backend/src/Index/InnovationIndex')
            os.remove('C:/Users/FinalProject/Desktop/PartnerFinder/Backend/src/Index/InnovationIndex.0')
            os.remove('C:/Users/FinalProject/Desktop/PartnerFinder/Backend/src/Index/Dictionary_INNOVATION')
            print('Deleting Innovation Index...')

        except:
            pass

        index = make_index('C:/Users/FinalProject/Desktop/PartnerFinder/Backend/src/Index/InnovationIndex', 'INNOVATION')
        print('Building Innovation Index...')


        try:
            names_url = get_calls_org(_url)
            names, urls = zip(*names_url)
            names_list, urls_list, date_list = get_innovation_hebrew_calls('https://innovationisrael.org.il/kol-kore-view')

        except Exception as e:
            print(e)

        try:

            for i,item in enumerate(urls):
                org_name = names[i]
                date = get_call_date(item)
                info = get_call_info(item)
                field = get_call_field(item)

                if date[2] is None:

                    call = InnovationCalls(CallID=i, organizationName= org_name,registrationDeadline= date[0],
                                             submissionDeadline= date[1], information= info,
                                           areaOfResearch= field,link= item, deadlineDate= date[2], open=False)
                else:
                    call = InnovationCalls(CallID=i, organizationName=org_name, registrationDeadline=date[0],
                                           submissionDeadline=date[1], information=info,
                                           areaOfResearch=field, link=item, deadlineDate=date[2], open=True)

                call.save()

                originalID = i
                indexID = len(index)
                document = get_document_from_innovation_call(org_name, info, field)
                index = add_document_to_curr_index(index, [document], 'INNOVATION')
                newMap = MapIdsINNOVATION(originalID=originalID, indexID=indexID)
                newMap.save()


            for i,item in enumerate(urls_list):
                org_name = names_list[i]
                date = date_list[i]
                str_date = date.strftime("%d/%m/%Y")

                counter = InnovationCalls.objects.latest('CallID').CallID

                call = InnovationCalls(CallID=counter + 1, organizationName= org_name,registrationDeadline= str_date,
                                         submissionDeadline= str_date, information= 'Not Available',
                                       areaOfResearch='Not Available',link= item, deadlineDate= date, open=True)

                call.save()

                originalID = counter + 1
                indexID = len(index)
                document = get_document_from_innovation_call('Not Available', org_name, "")
                newMap = MapIdsINNOVATION(originalID=originalID, indexID=indexID)
                newMap.save()
                index = add_document_to_curr_index(index, [document], 'INNOVATION')
                counter += 1


            response = {'success': 'Innovation Israel calls added successfully.'}

            if not setUpdateTime(innovationDate=time.mktime(datetime.now().timetuple())):
                raise

        except Exception as e:
            print(e)
            setUpdateTime(innovationDate=time.mktime(datetime.now().timetuple()))
            response = {'error': 'Error while adding Innovation Israel calls to DB'}

        return Response(response, status=status.HTTP_200_OK)


class MstCallsViewSet(viewsets.ModelViewSet):

    queryset = MstCalls.objects.all()
    permission_classes = [
        permissions.AllowAny
    ]
    serializer_class = MstCallsSerializer

    @action(detail=False, methods=['POST'])
    def add_mstcalls_to_db(self, request):

        """
         Method to define API add Ministry of science and technology calls and the generated index to the local DB
         :param request: HTTP request
         :return: HTTP response
         """

        counter = 0
        MstCalls.objects.all().delete()
        MapIdsMST.objects.all().delete()

        _url = 'https://www.gov.il/he/departments/publications/?OfficeId=75d0cbd7-46cf-487b-930c-2e7b12d7f846&limit=10&publicationType=7159e036-77d5-44f9-a1bf-4500e6125bf1'
        calls_number = get_calls_number(_url)

        if calls_number % 10 == 0:
            pages_number = calls_number // 10

        else:
            pages_number = (calls_number // 10) + 1

        try:
            os.remove('C:/Users/FinalProject/Desktop/PartnerFinder/Backend/src/Index/MstIndex')
            os.remove('C:/Users/FinalProject/Desktop/PartnerFinder/Backend/src/Index/MstIndex.0')
            os.remove('C:/Users/FinalProject/Desktop/PartnerFinder/Backend/src/Index/Dictionary_MST')
            print('Deleting MST Index...')

        except:
            pass

        index = make_index('C:/Users/FinalProject/Desktop/PartnerFinder/Backend/src/Index/MstIndex', 'MST')
        print('Building MST Index...')


        try:

            data = get_calls(_url)
            call_name, link, deadline, about, deadline_date = zip(*data)
            call_name_list, link_list, deadline_list, about_list, deadline_date_list = list(call_name), list(link), list(deadline), list(about), list(deadline_date)

            for i,item in enumerate(call_name_list):

                if deadline_date_list[i] is None:

                    call = MstCalls(CallID=counter, organizationName=item, submissionDeadline=deadline_list[i],
                                    information=about_list[i], link=link_list[i], deadlineDate=deadline_date_list[i], open= False)
                else:
                    call = MstCalls(CallID=counter, organizationName=item, submissionDeadline=deadline_list[i],
                                    information=about_list[i], link=link_list[i], deadlineDate=deadline_date_list[i],
                                    open=True)

                call.save()

                originalID = i
                indexID = len(index)
                document = get_document_from_mst_call(call_name_list[i],about_list[i])
                newMap = MapIdsMST(originalID=originalID, indexID=indexID)
                newMap.save()
                index = add_document_to_curr_index(index, [document], 'MST')
                counter += 1

        except Exception as e:
            print(e)


        try:

            skip = 10

            while pages_number >= 2:

                if skip > 10:
                    _url = _url[:-2]
                    _url = _url + str(skip)
                    new_url = re.sub("limit=10", "limit="+ str(skip + 10), _url)

                else:
                    _url = _url + '&skip=' + str(skip)
                    new_url = re.sub("limit=10", "limit=" + str(skip + 10), _url)

                data = get_calls(new_url)
                call_name, link, deadline, about, deadline_date = zip(*data)
                call_name_list, link_list, deadline_list, about_list, deadline_date_list = list(call_name), list(link), list(deadline), list(about), list(deadline_date)

                for i, item in enumerate(call_name_list):
                    call = MstCalls(CallID=counter, organizationName=item, submissionDeadline=deadline_list[i],
                                    information=about_list[i], link=link_list[i], deadlineDate=deadline_date_list[i])
                    call.save()

                    originalID = counter
                    indexID = len(index)
                    document = get_document_from_mst_call(call_name_list[i], about_list[i])
                    newMap = MapIdsMST(originalID=originalID, indexID=indexID)
                    newMap.save()
                    index = add_document_to_curr_index(index, [document], 'MST')
                    counter += 1

                skip += 10
                pages_number -= 1

            response = {'success': 'MST calls added successfully.'}

            if not setUpdateTime(mstDate=time.mktime(datetime.now().timetuple())):
                raise

        except Exception as e:
            print(e)
            setUpdateTime(mstDate=time.mktime(datetime.now().timetuple()))
            response = {'error': 'Error while adding MST calls to DB'}

        return Response(response, status=status.HTTP_200_OK)


class TechnionCallsViewSet(viewsets.ModelViewSet):

    queryset = TechnionCalls.objects.all()
    permission_classes = [
        permissions.AllowAny
    ]
    serializer_class = TechnionCallsSerializer

    @action(detail=False, methods=['POST'])
    def add_technioncalls_to_db(self, request):

        """
         Method to define API add Technion calls and the generated index to the local DB
         :param request: HTTP request
         :return: HTTP response
         """

        TechnionCalls.objects.all().delete()
        MapIdsTechnion.objects.all().delete()

        _url = 'https://www.trdf.co.il/eng/Current_Calls_for_Proposals.html?fund=allfunds&type=alltypes&ql=0'

        calls_number = get_calls_num(_url)

        if calls_number % 20 == 0:
            pages_number = calls_number // 20

        else:
            pages_number = (calls_number // 20) + 1

        try:
            os.remove('C:/Users/FinalProject/Desktop/PartnerFinder/Backend/src/Index/TechnionIndex')
            os.remove('C:/Users/FinalProject/Desktop/PartnerFinder/Backend/src/Index/TechnionIndex.0')
            os.remove('C:/Users/FinalProject/Desktop/PartnerFinder/Backend/src/Index/Dictionary_Technion')
            print('Deleting Technion Index...')

        except:
            pass

        index = make_index('C:/Users/FinalProject/Desktop/PartnerFinder/Backend/src/Index/TechnionIndex', 'Technion')
        print('Building Technion Index...')

        try:

            data = get_calls_data(_url)

            title = data['title']
            field = data['field']
            date = data['date']
            links = data['link']


            for i,item in enumerate (date):
                info = get_call_information(links[i])
                call = TechnionCalls(CallID=i, deadlineDate=item,organizationName=title[i],
                                     information=info, areaOfResearch=field[i],
                                     link=links[i], open=True)
                call.save()

                originalID = i
                indexID = len(index)
                document = get_document_from_technion_call(title[i], field[i], info)
                newMap = MapIdsTechnion(originalID=originalID, indexID=indexID)
                newMap.save()
                index = add_document_to_curr_index(index, [document], 'Technion')


        except Exception as e:
            print(e)
            response = {'error': 'Error while adding Technion calls to DB'}


        try:

            page_content = 20

            while pages_number >= 2:

                if _url[-2:] == '=0':
                    _url = _url[:-1]
                    new_url = _url + str(page_content)

                else:
                    new_url = _url + str(page_content)

                data = get_calls_data(new_url)

                title = data['title']
                field = data['field']
                date = data['date']
                links = data['link']

                latest_id = TechnionCalls.objects.latest('CallID')
                latest_id_num = latest_id.CallID + 1

                for i, item in enumerate(date):
                    info = get_call_information(links[i])
                    call = TechnionCalls(CallID=latest_id_num, deadlineDate=item, organizationName=title[i],
                                         information=info, areaOfResearch=field[i],
                                         link=links[i], open=True)
                    call.save()

                    originalID = latest_id_num
                    indexID = len(index)
                    document = get_document_from_technion_call(title[i], field[i], info)
                    newMap = MapIdsTechnion(originalID=originalID, indexID=indexID)
                    newMap.save()
                    index = add_document_to_curr_index(index, [document], 'Technion')
                    latest_id_num += 1

                page_content += 20
                pages_number -=1

            response = {'success': 'Technion calls added successfully.'}

            if not setUpdateTime(technionDate=time.mktime(datetime.now().timetuple())):
                raise

        except Exception as e:
            print(e)
            setUpdateTime(technionDate=time.mktime(datetime.now().timetuple()))
            response = {'error': 'Error while adding Technion calls to DB'}

        return Response(response, status=status.HTTP_200_OK)



class EuCallsViewSet(viewsets.ModelViewSet):
    queryset = EuCalls.objects.all()
    permission_classes = [
        permissions.AllowAny
    ]
    serializer_class = EuCallsSerializer

    @action(detail=False, methods=['POST'])
    def add_eucalls_to_db(self, request):

        """
        Method to define API add EU calls and the generated index to the local DB
        :param request: HTTP request
        :return: HTTP response
        """

        EuCalls.objects.all().delete()
        MapIdsEU.objects.all().delete()

        calls_obj = get_eu_calls()

        try:
            os.remove('C:/Users/FinalProject/Desktop/PartnerFinder/Backend/src/Index/EuIndex')
            os.remove('C:/Users/FinalProject/Desktop/PartnerFinder/Backend/src/Index/EuIndex.0')
            os.remove('C:/Users/FinalProject/Desktop/PartnerFinder/Backend/src/Index/Dictionary_Eu')
            print('Deleting EU Index...')

        except:
            pass
        try:
            index = make_index('C:/Users/FinalProject/Desktop/PartnerFinder/Backend/src/Index/EuIndex', 'EU')
            print('Building EU Index...')
        except Exception as e:
            traceback.print_exc()
            print(e)

        try:
            for i, item in enumerate(calls_obj):

                newCall = EuCalls(CallID=i, organizationName=calls_obj[i]['identifier'],
                                  ccm2Id=calls_obj[i]['ccm2Id'],
                                  information=calls_obj[i]['title'],
                                  title = calls_obj[i]['callTitle'],
                                  areaOfResearch=calls_obj[i]['tags'],
                                  link=calls_obj[i]['link'],
                                  deadlineDate=calls_obj[i]['deadlineDatesLong'], open=True)
                newCall.save()

                originalID = i
                indexID = len(index)
                document = get_document_from_eu_call(calls_obj[i]['identifier'],calls_obj[i]['title'],calls_obj[i]['tags'])
                newMap = MapIdsEU(originalID=originalID, indexID=indexID)
                newMap.save()
                index = add_document_to_curr_index(index, [document], 'EU')

            response = {'success': 'EU calls added successfully.'}

            if not setUpdateTime(euDate=time.mktime(datetime.now().timetuple())):
                raise

        except Exception as e:
            print(e)
            setUpdateTime(euDate=time.mktime(datetime.now().timetuple()))
            response = {'error': 'Error while adding EU calls to DB'}

        return Response(response, status=status.HTTP_200_OK)


class EmailSubscriptionViewSet(viewsets.ModelViewSet):
    queryset = EmailSubscription.objects.all()
    permission_classes = [
        permissions.AllowAny
    ]
    serializer_class = EmailSubscriptionSerializer

    @action(detail=False, methods=['GET'])
    def get_emails(self, request):

        """
        Method to define API to get email subscription settings
        :param request: HTTP request
        :return: HTTP Response
        """

        try:
            EmailSubscriptions = EmailSubscription.objects.all()
            email_responses = []

            for item in EmailSubscriptions:

                email_responses.append({'email':item.email,
                                         'status':item.status,
                                         'ID': item.ID})

            response = {'emails': email_responses}

        except:
            response = {'email': '', 'turned_on': '', 'error': 'Error while uploading email subscription settings'}

        return Response(response, status=status.HTTP_200_OK)



    @action(detail=False, methods=['POST'])
    def delete_email(self, request):

        """
        Method to define API to delete email subscription
        :param request: HTTP request that contain email data
        :return: HTTP Response
        """

        try:

            data = request.query_params['data']
            data = json.loads(data)
            email = data['email']

            try :

                filtered_emails = EmailSubscription.objects.filter(email=email)

                if filtered_emails.exists():
                    EmailSubscription.objects.filter(email=email).delete()
                    response = {'Success': 'Email ' + email + ' deleted successfully'}

                else:
                    response = {'Error': 'Email ' + email + ' did not subscribe yet'}


            except Exception as e:
                print(e)
                response = {'Error': 'Failed to unsubscribe the email'}

        except Exception as e:
                    print(e)
                    response = {'Error':'Error while parsing the data'}

        return Response(response, status=status.HTTP_200_OK)



    @action(detail=False, methods=['POST'])
    def set_emails(self, request):

        """
        Method to define API to update the email subscription settings
        :param request: HTTP request with updated email and status flag
        :return: HTTP response
        """

        try:
            data = request.query_params['data']
            data = json.loads(data)
            email = data['email']
            organization = data['organizations']
            #organization = ''.join(organization)
            #response = {'Success': 'New email have been successfully subscribed.'}
            try:

                filtered_emails = EmailSubscription.objects.filter(email=email)
                if filtered_emails.exists():

                    if len(filtered_emails) > 1:

                        EmailSubscription.objects.filter(email=email).delete()

                        latest_id = EmailSubscription.objects.latest('ID')
                        latest_id_num = latest_id.ID + 1

                        email_info = EmailSubscription(ID=latest_id_num, email=email,
                                                        organizationName=organization)

                        email_info.save()

                    else:
                        latest_id = EmailSubscription.objects.latest('ID')
                        latest_id_num = latest_id.ID + 1

                        if EmailSubscription.objects.filter(email=email,  organizationName=organization).exists():
                            raise Exception

                        else:
                            EmailSubscription.objects.filter(email=email).delete()

                            email_info = EmailSubscription(ID=latest_id_num, email=email,
                                                           organizationName=organization)

                            email_info.save()

                    response = {'Success': 'New email have been successfully subscribed.'}

                else:

                    try:

                        latest_id = EmailSubscription.objects.latest('ID')
                        latest_id_num = latest_id.ID + 1

                        email_info = EmailSubscription(ID=latest_id_num, email=email,
                                                       organizationName=organization)

                        email_info.save()

                    except Exception as e:
                        print(e)
                        emailSubscription = EmailSubscription(email=email, ID=1, organizationName=organization)
                        emailSubscription.save()

                    response = {'Success': 'New email have been successfully subscribed.'}

            except Exception as e:
                response = {'Error': 'Error while updating email subscription settings'}

        except:
            response = {'Error': 'Error while updating email subscription settings'}

        return Response(response, status=status.HTTP_200_OK)



    @action(detail=False, methods=['GET'])
    def send_emails(self, request):

        """
        Method to define API to send proposal calls updates to subscribed emails
        :param request: HTTP request
        :return: HTTP Response
        """

        signature = ''
        available_calls = []
        calls_deadline = []
        try:
            response = {'Error': 'Please insert at least one email!'}

            try:
                email_sub = EmailSubscription.objects.all()

                for item in email_sub:
                    email = item.email
                    organization = item.organizationName


                    if 'BSF' in organization:

                        try:
                            available_calls = get_field_name('https://www.bsf.org.il/calendar/')
                            calls_deadline = get_events_deadline('https://www.bsf.org.il/calendar/')
                        except:
                            response = {'Error': 'Error while Getting BSF available calls'}

                        if len(available_calls) != 0 :

                            body = MIMEMultipart('alternative')

                            calls = ''
                            for i,item in enumerate(available_calls):

                                date = calls_deadline[i]
                                str_date = date.strftime("%d/%m/%Y")
                                calls += '<li>' + item + '<br>' + '<b>' +' Deadline: (' + str_date  + ')' + '</b>' + '.</li>'
                                calls += '<br>'

                            signature = 'Sincerely,<br>Research Funding Portal Proposal Calls Alerts'
                            html = """\
                                        <html>
                                          <head><h3>You have new NSF-BSF proposal calls that might interest you</h3></head>
                                          <body>
                                            <ol>
                                            {}
                                            </ol>
                                            <br>
                                            <p> For more information please visit: https://www.bsf.org.il/calendar/</p> 
                                            <br>
                                            {}
                                          </body>
                                        </html>
                                        """.format(calls, signature)

                            response = {'Success': 'Finished building Proposal Calls Alert.'}

                            content = MIMEText(html, 'html')
                            body.attach(content)
                            body['Subject'] = 'BSF Proposal Calls Alert'
                            email_processing(receiver_email=email, message=body)

                        else:
                            response = {'Error': 'NO calls is open in BSF right now '}


                    if 'ISF' in organization:

                        try:
                            isf_calls = IsfCalls.objects.filter(open=True)
                            calls_list = []
                            deadline_list = []
                            for item in isf_calls:
                                calls_list.append(item.organizationName)
                                temp_date = item.deadlineDate
                                str_date = temp_date.strftime("%d/%m/%Y")
                                deadline_list.append(str_date)

                        except:
                            calls_list = []
                            deadline_list = []
                            response = {'Error': 'Error while Getting ISF available calls'}

                        if len(calls_list) != 0:

                            body = MIMEMultipart('alternative')

                            calls = ''
                            for i,item in calls_list:
                                calls += '<li>' + item + '<br>' + '<b>' +' Deadline: (' + deadline_list[i]  + ')' + '</b>' + '.</li>'
                                calls += '<br>'

                            signature = 'Sincerely,<br>Research Funding Portal Proposal Calls Alerts'
                            html = """\
                                                       <html>
                                                         <head><h3>You have new ISF proposal calls that might interest you</h3></head>
                                                         <body>
                                                           <ol>
                                                           {}
                                                           </ol>
                                                           <br>
                                                           <p> For more information please visit: https://www.isf.org.il/#/support-channels/1/10</p> 
                                                           <br>
                                                           {}
                                                         </body>
                                                       </html>
                                                       """.format(calls, signature)

                            response = {'Success': 'Finished building Proposal Calls Alert.'}

                            content = MIMEText(html, 'html')
                            body.attach(content)
                            body['Subject'] = 'ISF Proposal Calls Alert'
                            email_processing(receiver_email=email, message=body)

                        else:
                            response = {'Error': 'NO calls is open in ISF right now '}


                    if 'INNOVATION' in organization:

                        try:

                            innovation_calls = InnovationCalls.objects.filter(open=True)
                            calls_list = []
                            deadline_list = []

                            for item in innovation_calls:
                                calls_list.append(item.organizationName)
                                temp_date = item.deadlineDate
                                str_date = temp_date.strftime("%d/%m/%Y")
                                deadline_list.append(str_date)

                        except:
                            calls_list = []
                            deadline_list = []
                            response = {'Error': 'Error while Getting Innovation Israel available calls'}

                        if len(calls_list) != 0:

                            body = MIMEMultipart('alternative')

                            calls = ''
                            for i,item in enumerate(calls_list):
                                calls += '<li>' + item + '<br>' + '<b>' +' Deadline: (' + deadline_list[i] + ')' + '</b>' + '.</li>'
                                calls += '<br>'

                            signature = 'Sincerely,<br>Research Funding Portal Proposal Calls Alerts'
                            html = """\
                                                       <html>
                                                         <head><h3>You have new Innovation Israel proposal calls that might interest you</h3></head>
                                                         <body>
                                                           <ol>
                                                           {}
                                                           </ol>
                                                           <br>
                                                           <p> For more information please visit: https://innovationisrael.org.il/en/page/calls-proposals</p> 
                                                           <br>
                                                           {}
                                                         </body>
                                                       </html>
                                                       """.format(calls, signature)

                            response = {'Success': 'Finished building Proposal Calls Alert.'}

                            content = MIMEText(html, 'html')
                            body.attach(content)
                            body['Subject'] = 'Innovation Israel Proposal Calls Alert'
                            email_processing(receiver_email=email, message=body)

                        else:
                            response = {'Error': 'NO calls is open in Innovation Israel right now '}



                    if 'MST' in organization:

                        try:

                            mst_calls = MstCalls.objects.filter(open=True)
                            calls_list = []
                            deadline_list = []

                            for item in mst_calls:
                                calls_list.append(item.organizationName)
                                temp_date = item.deadlineDate
                                str_date = temp_date.strftime("%d/%m/%Y")
                                deadline_list.append(str_date)

                        except:
                            calls_list = []
                            deadline_list = []
                            response = {'Error': 'Error while Getting Innovation Israel available calls'}

                        if len(calls_list) != 0:

                            body = MIMEMultipart('alternative')

                            calls = ''
                            for i, item in enumerate(calls_list):
                                calls += '<li>' + item + '<br>' + '<b>' +' Deadline: (' + deadline_list[i] + ')' + '</b>' +'.</li>'
                                calls += '<br>'

                            signature = 'Sincerely,<br>Research Funding Portal Proposal Calls Alerts'
                            html = """\
                                                           <html>
                                                             <head><h3>You have new MST proposal calls that might interest you</h3></head>
                                                              <body>
                                                               <ol>
                                                               {}
                                                               </ol>
                                                               <br>
                                                               <p> For more information please visit: https://www.gov.il/he/departments/publications/?OfficeId=75d0cbd7-46cf-487b-930c-2e7b12d7f846&limit=10&publicationType=7159e036-77d5-44f9-a1bf-4500e6125bf1</p> 
                                                               <br>
                                                               {}
                                                             </body>
                                                           </html>
                                                           """.format(calls, signature)

                            response = {'Success': 'Finished building Proposal Calls Alert.'}

                            content = MIMEText(html, 'html')
                            body.attach(content)
                            body['Subject'] = 'MST Proposal Calls Alert'
                            email_processing(receiver_email=email, message=body)

                        else:
                            response = {'Error': 'NO calls is open in MST right now '}


                    if 'Technion' in organization:

                        try:

                            technion_calls = TechnionCalls.objects.filter(open=True)
                            calls_list = []
                            deadline_list = []

                            for value in technion_calls:
                                calls_list.append(value.organizationName)
                                temp_date = value.deadlineDate
                                str_date = temp_date.strftime("%d/%m/%Y")
                                deadline_list.append(str_date)

                        except:
                            calls_list = []
                            deadline_list = []
                            response = {'Error': 'Error while Getting Technion available call'}

                        if len(calls_list) != 0:

                            body = MIMEMultipart('alternative')

                            calls = ''
                            for i,item in enumerate(calls_list):
                                calls += '<li>' + item + '<br>' +'<b>' +' Deadline: (' + deadline_list[i] + ')' + '</b>' + '.</li>'
                                calls += '<br>'

                            signature = 'Sincerely,<br>Research Funding Portal Proposal Calls Alerts'
                            html = """\
                                                       <html>
                                                         <head><h3>You have new Technion proposal calls that might interest you</h3></head>
                                                         <body>
                                                           <ol>
                                                           {}
                                                           </ol>
                                                           <br>
                                                           <p> For more information please visit: https://www.trdf.co.il/eng/Current_Calls_for_Proposals/</p> 
                                                           <br>
                                                           {}
                                                         </body>
                                                       </html>
                                                       """.format(calls, signature)

                            response = {'Success': 'Finished building Proposal Calls Alert.'}

                            content = MIMEText(html, 'html')
                            body.attach(content)
                            body['Subject'] = 'Technion Proposal Calls Alert'
                            email_processing(receiver_email=email, message=body)

                        else:
                            response = {'Error': 'NO calls is open in Technion right now '}


                    if 'EU' in organization:

                        try:

                            eu_calls = EuCalls.objects.filter(open=True)
                            calls_list = []
                            deadline_list = []

                            for value in eu_calls:
                                calls_list.append(value.information)
                                temp_date = value.deadlineDate
                                str_date = temp_date.strftime("%d/%m/%Y")
                                deadline_list.append(str_date)

                        except:
                            calls_list = []
                            deadline_list = []
                            response = {'Error': 'Error while Getting EU available call'}

                        if len(calls_list) != 0:

                            body = MIMEMultipart('alternative')

                            calls = ''
                            for i,item in enumerate(calls_list):
                                calls += '<li>' + item + '<br>' +'<b>' +' Deadline: (' + deadline_list[i] + ')' + '</b>' + '.</li>'
                                calls += '<br>'

                            signature = 'Sincerely,<br>Research Funding Portal Proposal Calls Alerts'
                            html = """\
                                                       <html>
                                                         <head><h3>You have new EU proposal calls that might interest you</h3></head>
                                                         <body>
                                                           <ol>
                                                           {}
                                                           </ol>
                                                           <br>
                                                           <p> For more information please visit: https://ec.europa.eu/info/funding-tenders/opportunities/portal/screen/opportunities/topic-search</p> 
                                                           <br>
                                                           {}
                                                         </body>
                                                       </html>
                                                       """.format(calls, signature)

                            response = {'Success': 'Finished building Proposal Calls Alert.'}

                            content = MIMEText(html, 'html')
                            body.attach(content)
                            body['Subject'] = 'EU Proposal Calls Alert'
                            email_processing(receiver_email=email, message=body)

                        else:
                            response = {'Error': 'NO calls is open in EU right now '}

            except Exception as e:
                print(e)

        except Exception as e:
            print(e)
            response = {'Error': 'Error while building Proposal Calls Alerts.'}

        response = {'Success': 'Email alerts sent successfully'}

        return Response(response, status=status.HTTP_200_OK)


class UpdateCallsViewSet(viewsets.ModelViewSet):

    queryset = bsfCalls.objects.all()
    permission_classes = [
        permissions.AllowAny
    ]
    serializer_class = BsfCallsSerializer

    @action(detail=False, methods=['POST'])
    def call_update(self, request):

        """
       Method to define API to Update the organizations and add it into the local DB directly
       :param request: HTTP request
       :return: HTTP Response
        """

        try:

            data = request.query_params['data']
            print("This is the data:", data)
            data = json.loads(data)
            organizations = data['organizations']


            if not organizations:
                organizations = 'BSF, ISF, INNOVATION, MST, Technion, EU'

            if 'BSF' in organizations:


                try:
                    bsf_update_task.apply_async(countdown=10)

                except Exception as e:
                    print(e)
                    raise Exception

            if 'ISF' in organizations:

                try:

                    isf_update_task.apply_async(countdown=10)

                except Exception as e:
                    print(e)
                    raise Exception


            if 'INNOVATION' in organizations:

                try:

                    innovation_update_task.apply_async(countdown=10)

                except Exception as e:
                    print(e)
                    raise Exception


            if 'MST' in organizations:

                try:
                    mst_update_task.apply_async(countdown=15)

                except Exception as e:
                    print(e)
                    raise Exception

            if 'Technion' in organizations:

                try:
                    technion_update_task.apply_async(countdown=15)

                except Exception as e:
                    print(e)
                    raise Exception

            if 'EU' in organizations:

                try:
                    eu_update_task.apply_async(countdown=10)

                except Exception as e:
                    print(e)
                    raise Exception

            response = {'Success':'Proposal calls updated successfully.'}

        except Exception as e:
            print(e)
            response = {'Error': 'Error while updating the organization data'}

        return Response(response, status=status.HTTP_200_OK)



class UpdateTimeViewSet(viewsets.ModelViewSet):
    queryset = UpdateTime.objects.all()
    permission_classes = [
        permissions.AllowAny
    ]
    serializer_class = UpdateTimeSerializer

    @action(detail=False, methods=['GET'])
    def get_updateTime(self, request):
        """
        method to define API to get last update times
        :param request: HTTP request
        :return: HTTP Response
        """
        try:
            updated = UpdateTime.objects.all()[0]
            response = {'EU': updated.eu_update,
                        'Technion': updated.technion_update,
                        'BSF': updated.bsf_update,
                        'ISF':updated.isf_update,
                        'MST':updated.mst_update,
                        'INNOVATION':updated.innovation_update}

        except:
            response = {'BSF': '', 'ISF': '' , 'MST': '', 'INNOVATION': '', 'Technion': '', 'EU': '', 'error': 'Error while uploading updates settings'}

        return Response(response, status=status.HTTP_200_OK)



