import time

import pandas as pd
from bs4 import BeautifulSoup
from urllib.request import urlopen
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class SAIL():

    URL = "https://sailtenders.co.in/"

    @classmethod
    def preprocess(cls, results_df):
        '''
        Preprocesses the given DataFrame object by setting appropriate row
        and column headers

        :param subject_df: pandas DataFrame object
        '''
        results_df.index.names = ['Sl.No.']
        results_df.index = results_df.index + 1

        return results_df[['Tender issue date and time', 'Tender Title', 'Plant/Unit']]

    @classmethod
    def check_empty(cls, results_df):
        '''
        Checks if the results_df is empty or not

        :param results_df: Pandas DataFrame object containing the
            scraping results

        Returns: True if empty, False otherwise
        '''

        if list(results_df.iloc[:1]['Tender Title'] == 'No data available in table')[0]:
            return True
        else:
            return False

    @classmethod
    def scrape(cls, query):
        '''
        Method that actually scrapes the website and returns results if relevant.

        :param query: The search query to be entered in the search box

        Returns: A pandas DataFrame object containing the results of the scraping
        '''

        chrome_options = Options()
        chrome_options.add_argument("--headless")
        driver = webdriver.Chrome(executable_path='/home/nityeshaga/Downloads/chromedriver', chrome_options=chrome_options)

        driver.get(cls.URL)
        search_element = driver.find_element_by_id("txtSearchKeyword")
        search_button = driver.find_element_by_xpath('//*[@id="div_scroll"]/div[2]/div[5]/button')
        search_element.send_keys(query)
        search_button.click()

        time.sleep(5)
        
        soup = BeautifulSoup(driver.page_source, 'lxml')
        tender_table = soup.find('table', attrs={'id': 'tblTendet'})
        tender_df = pd.read_html(str(tender_table))

        results_df = cls.preprocess(tender_df[0])
        results_url = driver.current_url

        driver.quit()
        
        if cls.check_empty(results_df):
            return None, None
        else:
            return results_df, results_url
