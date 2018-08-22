import mechanicalsoup as msoup
import pandas as pd

class EprocureCentral():

    URL = "https://eprocure.gov.in/cppp/tendersearch"

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
        results_df.set_index('Sl.No.', inplace=True)

        return results_df[['e-Published Date', 'Title and Ref.No./Tender Id', 'Organisation Name']]

    @classmethod
    def check_empty(cls, results_df):
        if 'No Records Found' in results_df.index:
            return True
        else:
            return False

    @classmethod
    def scrape(cls, query):

        browser = msoup.StatefulBrowser()

        browser.open(cls.URL)
        browser.select_form()
        browser.select_form('form[id="tendersearch-form"]')
        browser["s_keyword"] = query
        response = browser.submit_selected()

        # get results
        result_page = browser.get_current_page()
        tender_table = result_page.find('table', attrs={'id': 'table'})
        tender_df = pd.read_html(str(tender_table))

        results_df = cls.preprocess(tender_df[0])
        
        if cls.check_empty(results_df):
            return None, None
        else:
            return results_df, browser.get_url()
