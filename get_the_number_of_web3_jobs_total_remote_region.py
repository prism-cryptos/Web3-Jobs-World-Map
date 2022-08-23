import time
from datetime import datetime, timezone
import warnings
import os
import re
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
import pandas as pd
import numpy as np
from datetime import date

import gspread
from gspread_dataframe import set_with_dataframe
from oauth2client.service_account import ServiceAccountCredentials 

options = webdriver.ChromeOptions()

warnings.simplefilter("ignore")
options.add_argument('--headless')
options.add_argument('--disable-extensions')
options.add_argument('--disable-gpu')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--hide-scrollbars')
options.add_argument('--blink-settings=imagesEnabled=false')
options.add_argument('--no-sandbox')
options.add_argument('--log-level=3')
options.add_argument('--ignore-certificate-errors')
options.page_load_strategy = 'eager' #https://www.selenium.dev/ja/documentation/webdriver/capabilities/shared/

#####total_remote_region
def total_remote_region():

    global driver
    global total_remote_region_list

    driver = webdriver.Chrome(os.getcwd() + './chromedriver.exe', options = options)
    driver.implicitly_wait(10)
    driver.get("https://cryptocurrencyjobs.co/")

    while len(driver.find_elements_by_css_selector('ol.ais-Hits-list > li.ais-Hits-item')) == 0:
        print("reload")
        driver.refresh()
    else:
        #get the number of total jobs
        total_number = driver.find_element_by_xpath('//div[@id="stats"]/div/span').text  ##caution :write element. If I write elements, the error "'list' object has no attribute 'text'" appears.
        total_number = re.sub(r"\D", "", total_number)
        total_remote_region_list.append(total_number)

        #get the number of remote and each region
        loop_process(total_remote_region_list)
        driver.quit()    

def loop_process(total_remote_region_list):

    search_list = ["Remote", "Asia", "Europe", "Africa", "US" , "Canada", "Latin America"]
    country_search_box = driver.find_element_by_xpath('//div[@id="aa-search-input"]/div/div/span/input')

    for i in range(0, len(search_list)):
        country_search_box.send_keys(str(search_list[i]))
        count = len(driver.find_elements_by_xpath('//div[@id="aa-search-input"]/div/div/span/span/div[@class="aa-dataset-3"]/span/div'))

        #if only one element exists, continue the process(below else:)
        while count != 1:
            count = len(driver.find_elements_by_xpath('//div[@id="aa-search-input"]/div/div/span/span/div[@class="aa-dataset-3"]/span/div'))

        else:
            search_content = driver.find_element_by_xpath('//div[@id="aa-search-input"]/div/div/span/span/div[@class="aa-dataset-3"]/span/div') #caution: "element"
            
            #checking the correspondence between the country name got and the target country name
            while search_content.text == str(search_list[i]):
                search_content.click()
                time.sleep(1)

                #judging whether loading is done or not
                while str(driver.find_element_by_xpath('//div[@id="searchbox"]/div/form/span').get_attribute('hidden')) != 'true':
                    print('wait loading...')
                    time.sleep(1)
                else:
                    text = driver.find_element_by_xpath('//div[@id="stats"]/div/span').text
                    the_data = re.sub(r"\D", "", text)
                    print(the_data)
                    total_remote_region_list.append(the_data)

                    country_search_box.send_keys(Keys.CONTROL + "a")
                    country_search_box.send_keys(Keys.DELETE)

                    break

                break
                
            else:
               search_content = driver.find_element_by_xpath('//div[@id="aa-search-input"]/div/div/span/span/div[@class="aa-dataset-3"]/span/div') #caution: "element"
               print("error")


def total_remote_region_to_google_sheet():

    SCOPE = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
    SERVICE_ACCOUNT_FILE = 'web3-jobs-world-map-360023-da7008191ded.json'
    credentials = ServiceAccountCredentials.from_json_keyfile_name(SERVICE_ACCOUNT_FILE, SCOPE)
    gc = gspread.authorize(credentials)

    SPREADSHEET_KEY = '1QFrs12Rkdi1dMHX8Wki1f3BsPM4MY2mT1v_ro21TjOI'
    total_remote_region_ws = gc.open_by_key(SPREADSHEET_KEY).worksheet('Total, Remote, Region')

    #set values in "Total, Remote, Region" spreadsheet
    str_list = list(filter(None, total_remote_region_ws.col_values(2))) #set 2(column B) to get the row that data is filled in it. 
    Last_row = len(str_list)+1

    #today = date.today()
    today = datetime.now(timezone.utc)
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
def scrape_total_remote_region():
    ##### get and write data of total_remote_region 
    global total_remote_region_list

    total_remote_region_list = []
    total_remote_region()
    total_remote_region_to_google_sheet()

scrape_total_remote_region()