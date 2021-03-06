import os
from datetime import datetime

import requests

from .Utils import setUpdateTime
from ..models import IsfCalls, MapIdsISF, UpdateTime, IsfCalls1

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup as soup, element
from .QueryProcess import *
import time


def get_calls_status(_url, click):

    """
   Method to fetch (scrape) all the calls data from ISF website
   :param : website proposal calls url
   :return: proposal calls information
   """

    # please change this PATH to open chromedriver from your device
    try:
        options = webdriver.ChromeOptions()
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        driver = webdriver.Chrome(executable_path='C:\Program Files (x86)\chromedriver.exe', options=options)
        driver.maximize_window()
        driver.get(_url)


    except Exception as e:
        print(e)
        return

    status, inst_type, num_partners, period, budget, general_info, deadline, reg_deadline, sub_deadline, link= '', '', '', '', '', '', '', '', '',''

    try:
        english = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.LINK_TEXT, "English"))
        )
        english.click()
        time.sleep(1)

        prg = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.LINK_TEXT, click))
        )
        prg.click()
        time.sleep(1)

        page_html = driver.page_source
        page_soup = soup(page_html, "html.parser")

        link = driver.current_url

        grant_tbl = page_soup.find_all("div", {"class": "grantInfoCell"})

        for item in grant_tbl:
            if item.h3.text == "Current status":
                status = item.p.text
            if item.h3.text == "Institute types":
                inst_type = item.p.text
            if item.h3.text == "Number of partners":
                num_partners = item.p.text
            if item.h3.text == "Grant period":
                period = item.p.text
            if item.h3.text == "Grant Budget":
                budget = item.p.text

        try:
            submission_tools = page_soup.find_all("span", {"class": "newlines"})
            if len(submission_tools) == 0:
                submission_tools = page_soup.find("div", {"class": "toolInfo"})
                temp_deadline = submission_tools.p.span.text
                reg_deadline = temp_deadline.split(' ', 1)
                reg_deadline = reg_deadline[0]
                deadline = datetime.strptime(reg_deadline, "%d/%m/%Y")
                sub_deadline = 'Open'

            else:
                deadline = None
                reg_deadline = 'Closed'
                sub_deadline = 'Closed'

        except:
            submission_tools = page_soup.find("div", {"class": "toolInfo"})
            reg_deadline = submission_tools.p.span.text
            submission_tools = submission_tools.find_all("span", {"class": ""})
            sub_deadline = submission_tools[1].text
            deadline = datetime.strptime(reg_deadline, "%d/%m/%Y")

        about = page_soup.find("div", {"class": "grantdataText"})
        text_clean = about.div.p.text[:-1]
        general_info = text_clean.rstrip("\n")

        time.sleep(1)

    except Exception as e:
        print(e)
        time.sleep(5)

    driver.quit()

    return status, inst_type, num_partners, period, budget, general_info, deadline, reg_deadline, sub_deadline,link

def get_proposal_names_links(_url, click):

    """
    Method to fetch (scrape) all the calls links from MST website
    :param : website proposal calls url
    :return: proposal calls links
    """

    # please change this PATH to open chromedriver from your device
    try:
        options = webdriver.ChromeOptions()
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        driver = webdriver.Chrome(executable_path='C:\Program Files (x86)\chromedriver.exe', options=options)
        driver.maximize_window()
        driver.get(_url)

    except Exception as e:
        print(e)
        return

    calls_name, links = [], []
    try:

        english = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.LINK_TEXT, "English"))
        )
        english.click()
        time.sleep(1)

        prg = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.LINK_TEXT, click))
        )
        prg.click()
        time.sleep(1)
        page_html = driver.execute_script(
            'return document.getElementsByClassName("panel-group")[0].innerHTML')
        # page_html = driver.page_source
        page_soup = soup(page_html, "html.parser")

        calls = page_soup.find_all("h4", {"class": "panel-title"})

        elements = driver.find_elements_by_css_selector(".accordion-toggle [href]")
        links = [elem.get_attribute('href') for elem in elements]

        calls_name = []

        for item in calls:
            calls_name.append(item.a.text.strip())

    except Exception as e:
        print(e)
        time.sleep(5)

    driver.quit()

    return calls_name, links


def get_Isf_call_by(tags, first_date, second_date, call_status):

    """
     Method to return all the relevant calls by tags and dates
     :param : tags, date
     :return: related calls
     """

    tags_call = get_Isf_call_by_tags(tags)

    dates_call = get_Isf_call_by_dates(first_date, second_date)

    result = get_Isf_call_intersection(tags_call, dates_call, call_status)

    return result


def get_Isf_call_by_tags(tags):

    """
     Method to get all calls with at least one tag from the list of tags.
     :param tags: list of tags
     :return: list of organizations objects
     """
    finalRes = []
    calls = IsfCalls.objects.all()

    if not tags:
        for call in calls:
            finalRes.append(call)

    else:

        if len(tags) == 1:

            tags = ' '.join(tags)
            index = reload_index('C:/Users/FinalProject/Desktop/PartnerFinder/Backend/src/Index/IsfIndex')
            corpus = NLP_processor([tags], 'ISF')
            res = index[corpus]
            res = process_query_result(res)

            res = [pair for pair in res if pair[1] > 0.3]
            res = sorted(res, key=lambda pair: pair[1], reverse=True)
            temp = []

            for pair in res:
                try:

                    temp.append(MapIdsISF.objects.get(indexID=pair[0]))

                except:
                    pass

            res = temp

        else:

            index = reload_index('C:/Users/FinalProject/Desktop/PartnerFinder/Backend/src/Index/IsfIndex')
            temp = []
            res = ''
            for tag in tags:
                corpus = NLP_processor([tag], 'ISF')
                res = index[corpus]
                res = process_query_result(res)

                res = [pair for pair in res if pair[1] > 0.3]
                res = sorted(res, key=lambda pair: pair[1], reverse=True)

                for pair in res:

                    try:

                        temp.append(MapIdsISF.objects.get(indexID=pair[0]))

                    except:
                        pass

                res = temp

        for mapId in res:
            finalRes.append(IsfCalls.objects.get(CallID=mapId.originalID))


    return finalRes


def get_Isf_call_by_dates(first_date, second_date):

    """
      Method to return all the calls between dates
      :param : dates
      :return: calls that have deadline between this range
      """

    calls = IsfCalls.objects.all()

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


def get_Isf_call_intersection(tags_call, dates_call, status):

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

def updateISF():

    """
       Method to update all the calls, and delete the old ones
       :return: nothing, only changing the data inside the DB
       """

    updated = False
    IsfCalls1.objects.all().delete()

    _url = 'https://www.isf.org.il/#/support-channels/1/10'
    name = 'Personal Research Grants'

    call_names, call_links = [], []

    try:
        call_names, call_links = get_proposal_names_links(_url, name)

    except Exception as e:
        print(e)

    try:

        for i, item in enumerate(call_names):
            call_info = get_calls_status(call_links[i], item)

            if call_info[7] == 'Closed':

                call = IsfCalls1(CallID=i, organizationName=item, status=call_info[0]
                                , registrationDeadline=call_info[7], submissionDeadline=call_info[8],
                                institutionType=call_info[1], numberOfPartners=call_info[2],
                                grantPeriod=call_info[3], budget=call_info[4],
                                information=call_info[5], deadlineDate=call_info[6], link=call_links[i], open=False)
            else:

                call = IsfCalls1(CallID=i, organizationName=item, status=call_info[0]
                                , registrationDeadline=call_info[7], submissionDeadline=call_info[8],
                                institutionType=call_info[1], numberOfPartners=call_info[2],
                                grantPeriod=call_info[3], budget=call_info[4],
                                information=call_info[5], deadlineDate=call_info[6], link=call_links[i], open=True)

            call.save()
        updated = True

    except Exception as e:
        print(e)
        updated = False

    if updated == True:
        copy_to_original_ISF()




def copy_to_original_ISF():

    IsfCalls.objects.all().delete()
    MapIdsISF.objects.all().delete()

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
        all_new_calls = IsfCalls1.objects.all()
        for i, item in enumerate(all_new_calls):

            new_call = IsfCalls(CallID=item.CallID, deadlineDate=item.deadlineDate, organizationName=item.organizationName,
                                information=item.information, status=item.status,registrationDeadline=item.registrationDeadline,
                                submissionDeadline=item.submissionDeadline,institutionType=item.institutionType,
                                numberOfPartners=item.numberOfPartners, grantPeriod=item.grantPeriod, budget=item.budget,
                                link=item.link, open=item.open)
            new_call.save()

            originalID = i
            indexID = len(index)
            document = get_document_from_isf_call(item.organizationName, item.information)
            newMap = MapIdsISF(originalID=originalID, indexID=indexID)
            newMap.save()
            index = add_document_to_curr_index(index, [document], 'ISF')

    except Exception as e:
        print(e)

    try:
        if not setUpdateTime(isfDate=time.mktime(datetime.now().timetuple())):
            raise

    except Exception as e:
        print(e)
        setUpdateTime(isfDate=time.mktime(datetime.now().timetuple()))

