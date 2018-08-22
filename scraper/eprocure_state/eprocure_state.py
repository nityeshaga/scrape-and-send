import pandas as pd
from bs4 import BeautifulSoup
from urllib.request import urlopen
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

class EprocureState():

    URL = "https://eprocure.gov.in/mmp/latestactivetenders"

    @classmethod
    def preprocess(cls, results_df):
        '''
        Preprocesses the given DataFrame object by setting appropriate row
        and column headers

        :param subject_df: pandas DataFrame object
        '''

        # set column headers
        headers = results_df.iloc[0]
        results_df = results_df.iloc[1:].copy(deep=True)
        results_df.rename(columns=headers, inplace=True)
        
        # set row indices
        results_df.set_index('S.No.', inplace=True)
        results_df.index.names = ['Sl.No.']

        return results_df[['e-Published Date', 
            'Title and Ref.No./Tender Id', 'State Name']]

    @classmethod
    def scrape(cls, query):

        chrome_options = Options()
        chrome_options.add_argument("--headless")
        driver = webdriver.Chrome(executable_path='/home/nityeshaga/Downloads/chromedriver', chrome_options=chrome_options)

        driver.get("https://eprocure.gov.in/mmp/latestactivetenders")
        search_element = driver.find_element_by_id("edit-s-keyword")
        search_button = driver.find_element_by_id("edit-save")
        search_element.send_keys(query)
        search_button.click()

        soup = BeautifulSoup(driver.page_source, 'lxml')
        tender_table = soup.find('table', attrs={'id': 'table'})
        tender_df = pd.read_html(str(tender_table))

        return cls.preprocess(tender_df[0]), driver.current_url
