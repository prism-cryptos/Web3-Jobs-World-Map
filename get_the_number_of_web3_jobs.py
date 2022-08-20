import time
import warnings
import os
import sys
import re
import codecs
import requests
import json
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys  ##Importing Keys is essential to work this script
from selenium.webdriver.support.ui import Select
import pandas as pd
import numpy as np
import pycountry
from datetime import date
from gspread_dataframe import set_with_dataframe

import gspread
from oauth2client.service_account import ServiceAccountCredentials 

warnings.simplefilter("ignore")
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--disable-extensions')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--disable-gpu')
options.add_argument('--blink-settings=imagesEnabled=false')
options.add_argument('--no-sandbox')
options.add_argument('--log-level=3')
options.page_load_strategy = 'eager' #https://www.selenium.dev/ja/documentation/webdriver/capabilities/shared/

#####each_country
def each_country():
    global all_country_data

    driver = webdriver.Chrome('./chromedriver.exe', options=options)
    driver.implicitly_wait(10)
    driver.get("https://cryptocurrencyjobs.co/")
    #time.sleep(2)

    while len(driver.find_elements_by_css_selector('ol.ais-Hits-list > li.ais-Hits-item')) == 0:
        print("reload")
        driver.refresh()
        #time.sleep(2)
    else:

        the_number_list = list()

        for i in range(0, len(pycountry.countries)):
            
            country_name = all_country_data[i,1]
            
            country_search_box = driver.find_element_by_xpath('//div[@id="aa-search-input"]/div/div/span/input')
            #time.sleep(5) ##This buffer time is essential.
            country_search_box.send_keys(str(country_name))
            print(country_name)
            time.sleep(3) ##This buffer time is essential.
            
            
            search_country = driver.find_elements_by_xpath('//div[@id="aa-search-input"]/div/div/span/span/div[@class="aa-dataset-2"]/span/div') #caution: "elements"
            
            if len(search_country) > 0:  ##https://qiita.com/captainUmaru/items/1d9c1c5e37da986404f1
                search_each_country = driver.find_element_by_xpath('//div[@id="aa-search-input"]/div/div/span/span/div[@class="aa-dataset-2"]/span/div') #caution: "element"
                search_each_country.click()
                time.sleep(3)  ##This buffer time is essential.
                
                text = driver.find_element_by_xpath('//div[@id="stats"]/div/span').text
                the_data = re.sub(r"\D", "", text)
                the_number_list.append(int(the_data))
                print(the_number_list)

                country_search_box.send_keys(Keys.CONTROL + "a")
                country_search_box.send_keys(Keys.DELETE)
            else:
                print("not found jobs")
                the_number_list.append(int(0))
                print(the_number_list)

                country_search_box.send_keys(Keys.CONTROL + "a")
                country_search_box.send_keys(Keys.DELETE)

    from_list_to_array = np.array([the_number_list])
    print(all_country_data)
    all_country_data = np.insert(all_country_data, 2, from_list_to_array, axis=1)
    print(all_country_data)

    #driver.quit()

def get_country_code_and_name_list():
    ###COMPLETED
    global all_country_data

    for i in range(0, len(pycountry.countries)-1):
        one_country_info = list(pycountry.countries)[i]
        one_country_code = one_country_info.alpha_2
        one_country_name = one_country_info.name
        one_country_data = np.array([one_country_code, one_country_name])
        
        all_country_data = np.vstack((all_country_data, one_country_data))

def each_country_to_google_sheet():
    
    SCOPE = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
    SERVICE_ACCOUNT_FILE = 'web3-jobs-world-map-359908-f8a8ff341f06.json'
    credentials = ServiceAccountCredentials.from_json_keyfile_name(SERVICE_ACCOUNT_FILE, SCOPE)
    gc = gspread.authorize(credentials)

    SPREADSHEET_KEY = '1QFrs12Rkdi1dMHX8Wki1f3BsPM4MY2mT1v_ro21TjOI'
    each_country_ws = gc.open_by_key(SPREADSHEET_KEY).worksheet('each country')

    #set values in "each country" spreadsheet
    code_name_number_df = pd.DataFrame(all_country_data).transpose()

    str_list = list(filter(None, each_country_ws.col_values(2))) #set 2(column B) to get the row that data is filled in it. 
    Last_row = len(str_list)+1

    today = date.today()
    today = today.strftime("%d/%m/%Y")

    each_country_ws.update_cell(Last_row, 1, today)
    set_with_dataframe(each_country_ws, pd.DataFrame(code_name_number_df[2:3]),  row = Last_row, col = 2, include_index = False, include_column_header = False)

#####total_remote_region
def total_remote_region():
    ###COMPLETED
    global total_remote_region_list

    driver = webdriver.Chrome('./chromedriver.exe', options=options)
    driver.implicitly_wait(10)
    driver.get("https://cryptocurrencyjobs.co/")
    time.sleep(2)

    while len(driver.find_elements_by_css_selector('ol.ais-Hits-list > li.ais-Hits-item')) == 0:
        print("reload")
        driver.refresh()
        time.sleep(2)
    else:
        #total number
        total_number = driver.find_element_by_xpath('//div[@id="stats"]/div/span').text  ##caution :write element. If I write elements, the error "'list' object has no attribute 'text'" appears.
        total_number = re.sub(r"\D", "", total_number)
        total_remote_region_list.append(total_number)
        
        search_list = ["Remote", "Asia", "Europe", "Africa", "US" , "Canada", "Latin America"]
        country_search_box = driver.find_element_by_xpath('//div[@id="aa-search-input"]/div/div/span/input')
        time.sleep(2)

        for i in range(0, len(search_list)):
            country_search_box.send_keys(str(search_list[i]))
            time.sleep(5)  ##This buffer time is essential.
            search_content = driver.find_element_by_xpath('//div[@id="aa-search-input"]/div/div/span/span/div[@class="aa-dataset-3"]/span/div') #caution: "element"
            search_content.click()
            time.sleep(5)  ##This buffer time is essential.
            text = driver.find_element_by_xpath('//div[@id="stats"]/div/span').text
            the_data = re.sub(r"\D", "", text)
            print(the_data)
            total_remote_region_list.append(the_data)

            country_search_box.send_keys(Keys.CONTROL + "a")
            country_search_box.send_keys(Keys.DELETE)

        driver.quit()

def total_remote_region_to_google_sheet():
    ###COMPLETED

    SCOPE = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
    SERVICE_ACCOUNT_FILE = 'web3-jobs-world-map-359908-f8a8ff341f06.json'
    credentials = ServiceAccountCredentials.from_json_keyfile_name(SERVICE_ACCOUNT_FILE, SCOPE)
    gc = gspread.authorize(credentials)

    SPREADSHEET_KEY = '1QFrs12Rkdi1dMHX8Wki1f3BsPM4MY2mT1v_ro21TjOI'
    total_remote_region_ws = gc.open_by_key(SPREADSHEET_KEY).worksheet('Total, Remote, Region')

    #set values in "remote & Total" spreadsheet
    str_list = list(filter(None, total_remote_region_ws.col_values(2))) #set 2(column B) to get the row that data is filled in it. 
    Last_row = len(str_list)+1

    today = date.today()
    today = today.strftime("%d/%m/%Y")

    total_remote_region_ws.update_cell(Last_row, 1, today)  ##caution: gspread accepts row and column values that start at 1, not 0.
    total_remote_region_ws.update_cell(Last_row, 2, int(total_remote_region_list[0])) #Total
    total_remote_region_ws.update_cell(Last_row, 3, int(total_remote_region_list[1])) #Remote
    total_remote_region_ws.update_cell(Last_row, 4, int(total_remote_region_list[2])) #Asia
    total_remote_region_ws.update_cell(Last_row, 5, int(total_remote_region_list[3])) #Europe
    total_remote_region_ws.update_cell(Last_row, 6, int(total_remote_region_list[4])) #Africa
    total_remote_region_ws.update_cell(Last_row, 7, int(total_remote_region_list[5]) + int(total_remote_region_list[6])) #North America
    total_remote_region_ws.update_cell(Last_row, 8, int(total_remote_region_list[7])) #Latin America



#####RUN
def run_the_scraper_total_remote_region():
    ##### get and write data of total_remote_region 
    global total_remote_region_list

    total_remote_region_list = []
    total_remote_region()
    total_remote_region_to_google_sheet()

def run_the_scraper_each_country():
    ##### get and write data of each_country 
    global all_country_data

    all_country_data = np.empty((0,2),int)
    get_country_code_and_name_list()
    each_country()
    each_country_to_google_sheet()

#run_the_scraper_each_country()
#run_the_scraper_total_remote_region()
