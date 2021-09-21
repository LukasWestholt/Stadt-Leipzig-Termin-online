#!/usr/bin/env python3
# coding: utf-8

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.select import Select
from selenium.webdriver.support import expected_conditions as ec
from datetime import datetime
from zoneinfo import ZoneInfo


def site(url, browser):
    browser.get(url)
    delay = 10  # seconds
    WebDriverWait(browser, delay).until(ec.presence_of_element_located((By.ID, 'agreement_accept')))
    browser.find_element_by_id('agreement_accept').click()
    click_next(browser, 'action_infopage_next')
    WebDriverWait(browser, delay).until(ec.presence_of_element_located((By.CLASS_NAME, 'buttonTreeviewExpand')))
    list_of_web_elements = browser.find_elements_by_class_name('buttonTreeviewExpand')
    for button in list_of_web_elements:
        button_text = str(button.text)
        if button_text.startswith('Bürgeramt') and str(button.text) not in [x[0] for x in RESULTS]:
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
                if str(label_element.text) == "Anmeldung Wohnsitz bei Zuzug nach Leipzig":
                    correct_id = label_element.get_attribute("for")
                    break
            if correct_id == "":
                raise Exception("problem with getting correct_id")
            Select(browser.find_element_by_id(correct_id)).select_by_value('1')
            click_next(browser, 'action_concernselect_next')
            click_next(browser, 'action_concerncomments_next')
            result = calendar(browser)
            RESULTS.append((button_text,) + result)
            return site(url, browser)
    return True


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
    slot_list = sorted(slot_list, key=lambda x: x[1])
    open_slots = slot_list[0][0].find_element_by_class_name('ekolCalendarFreeTimeContainer').text
    open_slots = int(open_slots.split(" frei")[0])
    time = slot_list[0][1]
    return open_slots, time


RESULTS = []
web = webdriver.Firefox(executable_path='geckodriver.exe')
site('https://tnv.leipzig.de/tnv/', web)
RESULTS = sorted(RESULTS, key=lambda x: x[2])

print("*** Ergebnisse sortiert nach Datum (Stand " + datetime.now().strftime('%d.%m.%Y') + ") ***\n")
for item in RESULTS:
    print(item[0] + " hat noch " + str(item[1]) + " freie Plätze am " +
          datetime.fromtimestamp(item[2] / 1000, ZoneInfo('Europe/Berlin')).strftime('%d.%m.%Y'))
web.quit()
