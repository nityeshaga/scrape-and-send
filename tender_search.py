import mechanicalsoup as msoup
import pandas as pd

if __name__ == '__main__':
    browser = msoup.StatefulBrowser()
    browser.open("https://eprocure.gov.in/cppp/tendersearch")
    browser.select_form()
    browser.select_form('form[id="tendersearch-form"]')
    browser["s_keyword"] = "pp bag"
    response = browser.submit_selected()
    result_page = browser.get_current_page()
    tender_table = result_page.find('table', attrs={'id': 'table'})
    tender_rows = tender_table.find_all('tr')
    tender_df = pd.read_html(str(tender_table))
    print(tender_df)
