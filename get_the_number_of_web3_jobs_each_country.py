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
import pycountry

import gspread
from gspread_dataframe import set_with_dataframe
from oauth2client.service_account import ServiceAccountCredentials 


options = webdriver.ChromeOptions()

warnings.simplefilter("ignore")
#options.add_argument('--headless')
options.add_argument('--disable-extensions')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--disable-gpu')
options.add_argument('--blink-settings=imagesEnabled=false')
options.add_argument('--no-sandbox')
options.add_argument('--log-level=3')
options.page_load_strategy = 'eager' #https://www.selenium.dev/ja/documentation/webdriver/capabilities/shared/

#####each_country
def each_country():

    global driver

    driver = webdriver.Chrome(os.getcwd() + './chromedriver.exe', options=options)
    driver.implicitly_wait(5)
    driver.get("https://cryptocurrencyjobs.co/")

    while len(driver.find_elements_by_css_selector('ol.ais-Hits-list > li.ais-Hits-item')) == 0:
        print("reload")
        driver.refresh()
    else:
        loop_process()
        driver.quit()

def loop_process():

    global all_country_data
    global the_number_in_each_country
    the_number_in_each_country = []

    for i in range(0, len(pycountry.countries)):
        
        country_name = all_country_data[i,1]
        country_search_box = driver.find_element_by_xpath('//div[@id="aa-search-input"]/div/div/span/input')
        country_search_box.send_keys(str(country_name))
        time.sleep(1.5)

        count = len(driver.find_elements_by_xpath('//div[@id="aa-search-input"]/div/div/span/span/div[@class="aa-dataset-2"]/span/div')) #to check the existence of the element
        
        if count == 0:
            the_number_in_each_country.append(None)
            print(the_number_in_each_country)

            country_search_box.send_keys(Keys.CONTROL + "a")
            country_search_box.send_keys(Keys.DELETE)

            print("count 0")

        else:
            while count != 1:
                count = len(driver.find_elements_by_xpath('//div[@id="aa-search-input"]/div/div/span/span/div[@class="aa-dataset-2"]/span/div'))
                
                #correction processing(if the variable "count" become more than 1 temporally bacause of bad internet connection, this process can adjust them.)
                if count == 0:
                    the_number_in_each_country.append(None)
                    country_search_box.send_keys(Keys.CONTROL + "a")
                    country_search_box.send_keys(Keys.DELETE)
                    break
                else:
                    pass

            else:
                print("count 1")
                search_country = driver.find_element_by_xpath('//div[@id="aa-search-input"]/div/div/span/span/div[@class="aa-dataset-2"]/span/div')

                #checking the correspondence between the country name got and the target country
                while search_country.text == str(search_list[i]):  ##https://qiita.com/captainUmaru/items/1d9c1c5e37da986404f1
                    search_each_country = driver.find_element_by_xpath('//div[@id="aa-search-input"]/div/div/span/span/div[@class="aa-dataset-2"]/span/div')
                    search_each_country.click()
                    time.sleep(1)

                    #judging whether loading is done or not
                    while str(driver.find_element_by_xpath('//div[@id="searchbox"]/div/form/span').get_attribute('hidden')) != 'true':
                        time.sleep(0.1)
                        print('wait loading...')

                    else:
                        text = driver.find_element_by_xpath('//div[@id="stats"]/div/span').text
                        the_data = re.sub(r"\D", "", text)
                        the_number_in_each_country.append(int(the_data))
                        print(the_number_list)

                        country_search_box.send_keys(Keys.CONTROL + "a")
                        country_search_box.send_keys(Keys.DELETE)
                else:
                    #If there is no correspondence, proceed next country. 
                    the_number_in_each_country.append(None)
                    country_search_box.send_keys(Keys.CONTROL + "a")
                    country_search_box.send_keys(Keys.DELETE)
                    break

    from_list_to_array = np.array([the_number_in_each_country])
    all_country_data = np.insert(all_country_data, 2, from_list_to_array, axis=1)
    print(all_country_data)

def get_country_code_and_name_list():
    global all_country_data

    for i in range(0, len(pycountry.countries)-1):
        one_country_info = list(pycountry.countries)[i]
        one_country_code = one_country_info.alpha_2
        one_country_name = one_country_info.name
        one_country_data = np.array([one_country_code, one_country_name])
        
        all_country_data = np.vstack((all_country_data, one_country_data))

def each_country_to_google_sheet():
    
    SCOPE = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
    SERVICE_ACCOUNT_FILE = 'web3-jobs-world-map-360023-da7008191ded.json'
    credentials = ServiceAccountCredentials.from_json_keyfile_name(SERVICE_ACCOUNT_FILE, SCOPE)
    gc = gspread.authorize(credentials)

    SPREADSHEET_KEY = '1QFrs12Rkdi1dMHX8Wki1f3BsPM4MY2mT1v_ro21TjOI'
    each_country_ws = gc.open_by_key(SPREADSHEET_KEY).worksheet('each country')

    #set values in "each country" spreadsheet
    code_name_number_df = pd.DataFrame(all_country_data).transpose()

    str_list = list(filter(None, each_country_ws.col_values(1))) #set 1(column A) to get the row that data is filled in it. 
    Last_row = len(str_list)+1

    today = datetime.now(timezone.utc)
    today = today.strftime("%d/%m/%Y")

    each_country_ws.update_cell(Last_row, 1, today)
    set_with_dataframe(each_country_ws, pd.DataFrame(code_name_number_df[2:3]),  row = Last_row, col = 2, include_index = False, include_column_header = False)

    
def scrape_each_country():
    ##### get and write data of each_country 
    global all_country_data

    all_country_data = np.empty((0,2),int)
    get_country_code_and_name_list()
    each_country()
    each_country_to_google_sheet()

scrape_each_country()

