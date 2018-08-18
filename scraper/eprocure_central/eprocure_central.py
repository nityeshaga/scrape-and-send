import mechanicalsoup as msoup
import pandas as pd

class EprocureCentral():

    URL = "https://eprocure.gov.in/cppp/tendersearch"

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

        return tender_df[0], browser.get_url()
