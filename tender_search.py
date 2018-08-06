import mechanicalsoup as msoup
import pandas as pd
from tabulate import tabulate

if __name__ == '__main__':
    browser = msoup.StatefulBrowser()
    browser.open("https://eprocure.gov.in/cppp/tendersearch")
    browser.select_form()
    #browser.get_current_form().print_summary()
    browser.select_form('form[id="tendersearch-form"]')
    #browser.get_current_form().print_summary()
    browser["s_keyword"] = "pp bag"
    response = browser.submit_selected()
    #print(response.text)
    result_page = browser.get_current_page()
    #type(result_page)
    tender_table = result_page.find('table', attrs={'id': 'table'})
    #print(tender_table)
    tender_rows = tender_table.find_all('tr')
    #type(tender_rows)
    #for row in tender_rows:
        #print(row)
    tender_df = pd.read_html(str(tender_table))
    print(tender_df)
    print( tabulate(tender_df[0], headers='keys', tablefmt='psql') )
