#!/usr/bin/env python3
# coding: utf-8

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.select import Select
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.firefox.options import Options
from datetime import datetime
from zoneinfo import ZoneInfo
import send_mail
import time


def site(url, browser, results=None):
    if results is None:
        results = []
    browser.get(url)
    delay = 10  # seconds
    WebDriverWait(browser, delay).until(ec.presence_of_element_located((By.ID, 'agreement_accept')))
    browser.find_element_by_id('agreement_accept').click()
    click_next(browser, 'action_infopage_next')
    WebDriverWait(browser, delay).until(ec.presence_of_element_located((By.CLASS_NAME, 'buttonTreeviewExpand')))
    list_of_web_elements = browser.find_elements_by_class_name('buttonTreeviewExpand')
    for button in list_of_web_elements:
        button_text = str(button.text)
        if button_text.startswith('Bürgeramt') and str(button.text) not in [x[0] for x in results]:
            button.click()
            WebDriverWait(browser, delay).until(
                ec.presence_of_element_located((By.CLASS_NAME, 'class_BuergerAuswahlDienststelle_office-button')))
            browser.find_element_by_class_name('class_BuergerAuswahlDienststelle_office-button').click()
            WebDriverWait(browser, delay).until(
                ec.presence_of_element_located((By.ID, 'id_abstractcontexttnv_mdg-input-anliegen-ohne-dauer')))
            list_of_web_elements = browser.find_elements_by_class_name(
                'CLASS_METADATAGRIDENTRY_LABELCONTAINER_OF_INPUT')
            correct_id = ""
            for web_element in list_of_web_elements:
                label_element = web_element.find_element_by_tag_name('label')
                if str(label_element.text) == SEARCH_FOR:
                    correct_id = label_element.get_attribute("for")
                    break
            if correct_id == "":
                raise Exception("problem with getting correct_id")
            Select(browser.find_element_by_id(correct_id)).select_by_value('1')
            click_next(browser, 'action_concernselect_next')
            click_next(browser, 'action_concerncomments_next')
            result = calendar(browser)
            results.append((button_text,) + result)
            return site(url, browser, results)
    return results


def click_next(browser, click_id):
    delay = 10  # seconds
    WebDriverWait(browser, delay).until(ec.presence_of_element_located((By.ID, click_id)))
    browser.find_element_by_id(click_id).click()
    return True


def calendar(browser):
    delay = 10  # seconds
    WebDriverWait(browser, delay).until(ec.presence_of_element_located((By.CLASS_NAME, 'ekolCalendarContainer')))
    slot_list = [(n, int(str(n.get_attribute("name")).split("||DAY_SELECT||")[1])) for n in
                 browser.find_elements_by_class_name('eKOLCalendarButtonDayFreeX')]
    if len(slot_list) == 0:
        return 0, None
    slot_list = sorted(slot_list, key=lambda x: x[1])
    open_slots = slot_list[0][0].find_element_by_class_name('ekolCalendarFreeTimeContainer').text
    open_slots = int(open_slots.split(" frei")[0])
    slot_time = slot_list[0][1]
    return open_slots, slot_time


def find(best_option):
    options = Options()
    options.headless = True
    web = webdriver.Firefox(options=options, executable_path='geckodriver.exe')
    results = site(URL, web)
    web.quit()
    results = sorted(results, key=lambda x: (x[2] is None, x[2]))
    found = False
    print("\n*** Ergebnisse sortiert nach Datum (Stand " + datetime.now().strftime('%d.%m.%Y %H:%M Uhr') + ") ***\n")
    for item in results:
        if item[1] > 0:
            print(place(item) + " hat " + str(item[1]) + " " + ("freie Slots" if item[1] > 1 else "freien Slot") +
                  " am " + datetime.fromtimestamp(item[2] / 1000, ZoneInfo('Europe/Berlin')).strftime('%d.%m.%Y'))
            if time_window(item) and not found and not \
                    (best_option and best_option[0] == item[0] and best_option[2] == item[2]):
                sendmail(item)
                found = item
        else:
            print(place(item) + " hat aktuell keinen freien Slot")
    return found


def time_window(item):
    timestamp = item[2]
    return int(STOP_TIME_WINDOW_EXCLUDED.timestamp()) > timestamp / 1000 > int(START_TIME_WINDOW_EXCLUDED.timestamp())


def place(item):
    return str(item[0]).replace("Bürgeramt", "BA")


def sendmail(item):
    msg = item[0] + " hat " + str(item[1]) + " " + ("freie Slots" if item[1] > 1 else "freien Slot") + \
          " am " + datetime.fromtimestamp(item[2] / 1000, ZoneInfo('Europe/Berlin')).strftime('%d.%m.%Y')
    msg += "\n Clicke hier: " + URL
    send_mail.send_email("Termin gefunden!", msg, SEND_TO)


URL = 'https://tnv.leipzig.de/tnv/'
SEARCH_FOR = "Anmeldung Wohnsitz bei Zuzug nach Leipzig"
START_TIME_WINDOW_EXCLUDED = datetime(2021, 10, 1, 0, 0)
STOP_TIME_WINDOW_EXCLUDED = datetime(2021, 10, 7, 0, 0)
SEND_TO = ["lukaswestholt@yahoo.de"]
SEARCH_INTERVAL = 60

best = False
while True:
    best = find(best)
    time.sleep(SEARCH_INTERVAL)
