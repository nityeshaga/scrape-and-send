import mechanicalsoup as msoup
import pandas as pd
import os.path
import smtplib
from getpass import getpass

SEARCH_QUERIES = ['pp bag', 'fibc bag', 'jumbo bag', 'leno bag']

def setup_server():
    '''
    Sets up an SMTP server.

    Returns the SMTP object and sender's email id
    '''
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.ehlo()
    server.starttls()
    server.ehlo()
    sender_email_id = input("Enter the serder's email id: ").strip()
    sender_pwd = getpass()
    server.login(sender_email_id, sender_pwd)

    return server, sender_email_id

def create_msg_content(query, results_df):
    '''
    Constructs an appropriate email using the search query and the
    results present in results_df

    :param query: The search query.
    :param results_df: DataFrame object that stores the results of query

    Returns the message as a string
    '''
    return "This query has new results " + query
    
def update_with_email(query, results_df):
    '''
    Sends email to the client_email_id notifying about the results
    found for query.

    :param query: The search query
    :param results_df: DataFrame object that stores the results of query
    '''
    server, sender_email_id = setup_server()
    client_email_id = input("Enter the client's email id: ")
    content = create_msg_content(query, results_df)
    server.sendmail(sender_email_id, client_email_id, content)
    server.quit()
        
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
    
    # set row indices
    subject_df.set_index('Sl.No.', inplace=True)

    return subject_df

def update_results(query, results_df):
    '''
    Updates the datebase related to the query with the entries in results_df

    :param query: The search query entered on the website
    :param tender_df: A pandas DataFrame that stores the results returned by 
                      the website 
    '''

    filename = query.replace(' ', '_') + '_tenders.csv'

    if os.path.isfile('./'+filename):
        database_df = pd.read_csv(filename, index_col='Sl.No.')
        if database_df.equals(results_df):
            print("No new entries found for query -", query)
        else:
            print("Updating database for query -", query)
            database_df = results_df.copy(deep=True)
            database_df.to_csv(filename)
            update_with_email(query, results_df)
    else:
        results_df.to_csv(filename)
        update_with_email(query, results_df)

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

        if 'No Records Found' not in tender_df_preprocessed.index:
            update_results(query, tender_df_preprocessed)
