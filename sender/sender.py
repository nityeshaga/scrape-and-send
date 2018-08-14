import smtplib
from getpass import getpass
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from tabulate import tabulate

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
