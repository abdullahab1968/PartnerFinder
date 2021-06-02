import os
from datetime import datetime
from ..models import MapIdsTechnion, TechnionCalls
import requests

import nltk
from nltk import tokenize
from operator import itemgetter
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

from bs4 import BeautifulSoup as soup, element
from urllib.request import urlopen as req
from time import sleep
import math
from orderedset import OrderedSet
from urllib.request import urlopen as req
from urllib.request import Request
import re
from selenium import webdriver
from .QueryProcess import *


def get_calls_data(_url):

    field, link, title, date = [], [], [], []
    data = {}

    try:

        PATH = '/Users/najeh/chromedriver'
        driver = webdriver.Chrome(PATH)
        driver.get(_url)

        page_html = driver.page_source
        page_soup = soup(page_html, "html.parser")

        sleep(1)

        field_element = page_soup.find_all("td", {"class": "three area"})
        for item in field_element:
            if len(item.text) != 0:
                field.append(item.text)
            else:
                field.append('Not Available')


        link_element = page_soup.find_all("td", {"class": "two kore"})
        for item in link_element:
            link.append(item.a['href'])


        title_element = page_soup.find_all("td", {"class": "two kore"})
        for item in title_element:
            if len(item.a.text) != 0:
                title.append(item.a.text)
            else:
               title.append('Not Available')


        date_element = page_soup.find_all("td", {"class": ""})
        for item in date_element:
            temp = item.text.strip()
            date.append(datetime.strptime(temp, "%d/%m/%y"))

        sleep(1)
        driver.quit()

    except Exception as e:
        print(e)


    data['title'] = title
    data['date'] = date
    data['field'] = field
    data['link'] = link

    return data

def get_call_information(links):


    information = ''

    try:
        PATH = '/Users/najeh/chromedriver'
        driver = webdriver.Chrome(PATH)
        driver.get(links)

        page_html = driver.page_source
        page_soup = soup(page_html, "html.parser")
        sleep(1)
        table_element = page_soup.find("table", {"class": "fund"})
        information = table_element.p.text

        driver.quit()

    except Exception as e:

        information = 'Please login to Technion website to see more information'
        driver.quit()

    if len(information) == 0 or len(information) == 1:
        information = 'Please login to Technion website to see more information'

    return information


def get_calls_num(_url):

    calls_number = 0

    try:

        PATH = '/Users/najeh/chromedriver'
        driver = webdriver.Chrome(PATH)
        driver.get(_url)

        page_html = driver.page_source
        page_soup = soup(page_html, "html.parser")

        number_element = page_soup.find_all("span", {"class": "bold"})
        calls_number = int(number_element[1].text)

        driver.quit()

    except Exception as e:
        print(e)

    return calls_number


def get_technion_call_by(tags, first_date, second_date, call_status):

    """
    Method to return all the relevant calls by tags and dates
    :param : tags, date
    :return: related calls
    """

    tags_call = get_technion_call_by_tags(tags)

    dates_call = get_technion_call_by_dates(first_date, second_date)

    result = get_technion_call_intersection(tags_call, dates_call, call_status)

    return result


def get_technion_call_by_tags(tags):

    """
       Method to get all calls with at least one tag from the list of tags.
       :param tags: list of tags
       :return: list of organizations objects
       """
    finalRes = []

    calls = TechnionCalls.objects.all()

    if not tags:
        for call in calls:
            finalRes.append(call)

    else:

        if len(tags) == 1:

            tags = ' '.join(tags)
            index = reload_index('TechnionIndex')
            corpus = NLP_processor([tags], 'Technion')
            res = index[corpus]
            res = process_query_result(res)

            res = [pair for pair in res if pair[1] > 0.2]
            res = sorted(res, key=lambda pair: pair[1], reverse=True)
            temp = []

            for pair in res:
                try:

                    temp.append(MapIdsTechnion.objects.get(indexID=pair[0]))

                except:
                    pass

            res = temp

        else:
            index = reload_index('BsfIndex')
            temp = []
            res = ''
            for tag in tags:
                corpus = NLP_processor([tag], 'BSF')
                res = index[corpus]
                res = process_query_result(res)

                res = [pair for pair in res if pair[1] > 0.3]
                res = sorted(res, key=lambda pair: pair[1], reverse=True)

                for pair in res:

                    try:
                        temp.append(MapIdsTechnion.objects.get(indexID=pair[0]))
                    except:
                        pass

                res = temp


        for mapId in res:
            finalRes.append(TechnionCalls.objects.get(CallID=mapId.originalID))

    return finalRes


def get_technion_call_by_dates(first_date, second_date):

    """
         Method to return all the calls between dates
         :param : dates
         :return: calls that have deadline between this range
         """

    calls = TechnionCalls.objects.all()

    if not first_date and not second_date:
        return calls

    elif not first_date and second_date:
        from_date = datetime.strptime(second_date, "%d/%m/%Y")
        return calls.filter(deadlineDate__lte = from_date)

    elif first_date and not second_date :
        to_date = datetime.strptime(first_date, "%d/%m/%Y")
        return calls.filter(deadlineDate__gte=to_date)

    else:

        from_date = datetime.strptime(first_date, "%d/%m/%Y")
        to_date = datetime.strptime(second_date, "%d/%m/%Y")
        return calls.filter(deadlineDate__gte=from_date, deadlineDate__lte=to_date)


def get_technion_call_intersection(tags_call, dates_call, status):

    """
      Method to intersect all the calls result together
      :param : tags results, date results calls
      :return: calls list
      """

    call_status = False

    if 'Open and Closed' in status:

        result = []
        already_taken = set()

        for call in tags_call:
            already_taken.add(call.CallID)

        not_taken = set()
        for call in dates_call:
            if call.CallID in already_taken and call.CallID not in not_taken:
                result.append(call)
                not_taken.add(call.CallID)

    else:

        if status == 'Open':
            call_status = True

        if status == 'Closed':
            call_status = False

        result = []
        already_taken = set()

        for call in tags_call:
            if call.open == call_status:
                already_taken.add(call.CallID)

            else:
                pass

        not_taken = set()
        for call in dates_call:
            if call.CallID in already_taken and call_status == call.open and call.CallID not in not_taken:
                result.append(call)
                not_taken.add(call.CallID)

    return result

# _url = 'https://www.trdf.co.il/eng/Current_Calls_for_Proposals.html?fund=allfunds&type=alltypes&ql=0'
# print(get_calls_data(_url))