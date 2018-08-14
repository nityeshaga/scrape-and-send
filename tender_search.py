import mechanicalsoup as msoup
import pandas as pd
import os.path
import smtplib
from getpass import getpass
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from tabulate import tabulate

SEARCH_QUERIES = ['pp bag', 'fibc bag', 'jumbo bag', 'leno bag', 'bopp bag', 'hdpe bag', 'tarpaulin']

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

def create_msg_content(query, results_df, result_url, 
                       sender_email_id, client_email_id):
    '''
    Constructs an appropriate email using the search query and the
    results present in results_df

    :param query: The search query.
    :param results_df: DataFrame object that stores the results of query
    :param result_url: URL pointing to the search results
    :param sender_email_id: Email address of the sender
    :param client_email_id: Email address of the client

    Returns the message as a string
    '''
    message = MIMEMultipart()
    message['From'] = sender_email_id
    message['To'] = client_email_id
    message['Subject'] = "New search results for \"" + query + "\" on eprocure.gov.in"

    body = tabulate(results_df[['e-Published Date', 'Title and Ref.No./Tender Id', 
        'Organisation Name']], tablefmt='grid')
    message.attach(MIMEText(body, 'plain'))
    message.attach(MIMEText('\n\n URL:'+result_url, 'plain'))

    return message.as_string()
    
def update_with_email(query, results_df, result_url):
    '''
    Sends email to the client_email_id notifying about the results
    found for query.

    :param query: The search query
    :param results_df: DataFrame object that stores the results of query
    :param result_url: URL pointing to the search results
    '''
    server, sender_email_id = setup_server()
    client_email_id = input("Enter the client's email id: ")
    content = create_msg_content(query, results_df, result_url, 
                                 sender_email_id, client_email_id)
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

def update_results(query, results_df, result_url):
    '''
    Updates the datebase related to the query with the entries in results_df

    :param query: The search query entered on the website
    :param tender_df: A pandas DataFrame that stores the results returned by 
                      the website 
    :param result_url: URL pointing to the search results
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
            update_with_email(query, results_df, result_url)
    else:
        results_df.to_csv(filename)
        update_with_email(query, results_df, result_url)

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
            update_results(query, tender_df_preprocessed, browser.get_url())
