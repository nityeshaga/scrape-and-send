import pandas as pd
import os.path

from sender.sender import update_with_email

from scraper.eprocure_central.eprocure_central import EprocureCentral
from scraper.eprocure_state.eprocure_state import EprocureState
from scraper.SAIL.SAIL import SAIL

SEARCH_QUERIES = ['pp bag', 'fibc bag', 'jumbo bag', 'leno bag', 'bopp bag', 'hdpe bag', 'tarpaulin']

SCRAPERS = {'eprocure central': EprocureCentral,
            'eprocure state': EprocureState,
            'SAIL': SAIL}

def new_results(results_df, database_df):
    '''
    Checks if results_df contains results that are not present
    in database_df.
    
    :param results_df: Pandas DataFrame object that contains results
        from web scraping
    :param database_df: Pandas DataFrame object that contain the
        entries stored in the database

    Returns: True if new results present, False otherwise
    '''
    merge_df = results_df.merge(database_df, on=list(database_df.columns),
                                how='left', indicator=True)
    return not merge_df.loc[merge_df['_merge']=='left_only', 
                            list(database_df.columns)].empty

def update_results(scraper, query, results_df, result_url):
    '''
    Updates the datebase of scraper related to the query with the 
    results in results_df.

    :param scraper: The web scraper corresponding to the results
    :param query: The search query entered on the website
    :param tender_df: A pandas DataFrame that stores the results returned by 
                      the website 
    :param result_url: URL pointing to the search results
    '''

    filename = query.replace(' ', '_') + '_tenders.csv'
    filepath = './scraper/' + \
               scraper.replace(' ', '_') + '/' + \
               filename

    if os.path.isfile(filepath):
        database_df = pd.read_csv(filepath, index_col='Sl.No.')
        if new_results(results_df, database_df):
            print("Updating database for query ")
            database_df = results_df.copy(deep=True)
            database_df.to_csv(filepath)
            update_with_email(scraper, query, results_df, result_url)
        else:
            print("No new entries found for query ")
    else:
        print("Creating new database for query ")
        results_df.to_csv(filepath)
        update_with_email(scraper, query, results_df, result_url)

if __name__ == '__main__':

    for scraper in SCRAPERS:
        print("Analysing " + scraper + "...")
        for query in SEARCH_QUERIES:
            print("Processing query - " + query + " ...")

            tender_df, url = SCRAPERS[scraper].scrape(query)

            if tender_df is None:
                print("Search returned no results")
            else:
                update_results(scraper, query, tender_df, url)
