import smtplib
from getpass import getpass
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from tabulate import tabulate
from functools import wraps

def try_until_success(func):
    '''
    Function decorator to repeatedly call func in case of 
    smtplib.SMTPAuthenticationError
    '''
    def wrapper(*args, **kwargs):
        for i in range(5):
            try:
                return func(*args, **kwargs)
            except smtplib.SMTPAuthenticationError:
                pass
        raise smtplib.SMTPAuthenticationError
    return wrapper

@try_until_success
def login_user(server):
    '''
    Asks the user for email id / password and logs in the server

    :param server: smtplib.SMTP object

    Returns: The email id entered by the user
    '''
    sender_email_id = input("Enter the serder's email id: ").strip()
    sender_pwd = getpass()
    server.login(sender_email_id, sender_pwd)
    return sender_email_id

def setup_server():
    '''
    Sets up an SMTP server.

    Returns the SMTP object and sender's email id
    '''
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.ehlo()
    server.starttls()
    server.ehlo()
    sender_email_id = login_user(server)

    return server, sender_email_id

def create_msg_content(scraper_name, query, results_df, result_url, 
                       sender_email_id, client_email_id):
    '''
    Constructs an appropriate email using the search query and the
    results present in results_df

    :param scraper_name: The name of the scraper corresponding to the 
        search results
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
    message['Subject'] = "New search results for \"" + query + \
                         "\" on " + scraper_name

    body = tabulate(results_df, tablefmt='grid')
    message.attach(MIMEText(body, 'plain'))
    message.attach(MIMEText('\n\n URL:'+result_url, 'plain'))

    return message.as_string()

def update_with_email(scraper_name, query, results_df, result_url):
    '''
    Sends email to the client_email_id notifying about the results
    found for query.

    :param scraper_name: The name of the scraper corresponding to the 
        search results
    :param query: The search query
    :param results_df: DataFrame object that stores the results of query
    :param result_url: URL pointing to the search results
    '''
    server, sender_email_id = setup_server()
    client_email_id = input("Enter the client's email id: ")
    content = create_msg_content(scraper_name, query, results_df, 
                                 result_url, sender_email_id, 
                                 client_email_id)
    server.sendmail(sender_email_id, client_email_id, content)
    server.quit()
