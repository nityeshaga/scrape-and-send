import mechanicalsoup as msoup
import pandas as pd
import os.path

SEARCH_QUERIES = ['pp bag', 'fibc bag', 'jumbo bag', 'leno bag']

def preprocess(subject_df):
    '''
    Preprocesses the given DataFrame object by setting appropriate row
    and column headers

    :param subject_df: pandas DataFrame object
    '''

    # set column headers
    headers = subject_df.iloc[0]
    subject_df = subject_df.iloc[1:].copy(deep=True)
    subject_df.rename(columns=headers, inplace=True)
    
    subject_df.set_index('Sl.No.', inplace=True)

    return subject_df

def update_results(query, tender_df):
    '''
    Updates the datebase related to the query with the entries in tender_df

    :param query: The search query entered on the website
    :param tender_df: A pandas DataFrame that stores the results returned by 
                      the website 
    '''

    filename = query.replace(' ', '_') + '_tenders.csv'

    if os.path.isfile('./'+filename):
        database_df = pd.read_csv(filename, index_col='Sl.No.')
        if database_df.equals(tender_df):
            print("No new entries found for query -", query)
        else:
            print("Updating database for query -", query)
            database_df = tender_df.copy(deep=True)
            database_df.to_csv(filename)
    else:
        tender_df.to_csv(filename)

if __name__ == '__main__':

    browser = msoup.StatefulBrowser()

    for query in SEARCH_QUERIES:
        browser.open("https://eprocure.gov.in/cppp/tendersearch")
        browser.select_form()
        browser.select_form('form[id="tendersearch-form"]')
        browser["s_keyword"] = query
        response = browser.submit_selected()

        # get results
        result_page = browser.get_current_page()
        tender_table = result_page.find('table', attrs={'id': 'table'})
        tender_df = pd.read_html(str(tender_table))

        tender_df_preprocessed = preprocess(tender_df[0])

        #print('*'*10, query, '*'*10)
        #print(tender_df_preprocessed)

        update_results(query, tender_df_preprocessed)
