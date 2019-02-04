import uuid
import lusid
import pytz
from datetime import datetime, timedelta, time
import pandas as pd
import numpy as np
import os
import requests
from urllib.request import pathname2url
import json
from random import shuffle, randint
from msrest.authentication import BasicTokenAuthentication

def authenticate_secrets():
    # Load our configuration details from the environment variables
    token_url = os.getenv("FBN_TOKEN_URL", None)
    api_url = os.getenv("FBN_LUSID_API_URL", None)
    username = os.getenv("FBN_USERNAME", None)
    password_raw = os.getenv("FBN_PASSWORD", None)
    client_id_raw = os.getenv("FBN_CLIENT_ID", None)
    client_secret_raw = os.getenv("FBN_CLIENT_SECRET", None)

    # If any of the environmental variables are missing use a local secrets file
    if token_url is None or username is None or password_raw is None or client_id_raw is None \
            or client_secret_raw is None or api_url is None:

        dir_path = os.path.dirname(os.path.realpath(__file__))
        with open(os.path.join(dir_path, "../secrets.json"), "r") as secrets:
            config = json.load(secrets)

        token_url = os.getenv("FBN_TOKEN_URL", config["api"]["tokenUrl"])
        username = os.getenv("FBN_USERNAME", config["api"]["username"])
        password = pathname2url(os.getenv("FBN_PASSWORD", config["api"]["password"]))
        client_id = pathname2url(os.getenv("FBN_CLIENT_ID", config["api"]["clientId"]))
        client_secret = pathname2url(os.getenv("FBN_CLIENT_SECRET", config["api"]["clientSecret"]))
        api_url = os.getenv("FBN_LUSID_API_URL", config["api"]["apiUrl"])

    else:
        password = pathname2url(password_raw)
        client_id = pathname2url(client_id_raw)
        client_secret = pathname2url(client_secret_raw)

    # Prepare our authentication request
    token_request_body = ("grant_type=password&username={0}".format(username) +
                          "&password={0}&scope=openid client groups".format(password) +
                          "&client_id={0}&client_secret={1}".format(client_id, client_secret))
    headers = {"Accept": "application/json", "Content-Type": "application/x-www-form-urlencoded"}

    # Make our authentication request
    okta_response = requests.post(token_url, data=token_request_body, headers=headers)

    # Ensure that we have a 200 response code
    assert okta_response.status_code == 200

    # Retrieve our api token from the authentication response
    api_token = {"access_token": okta_response.json()["access_token"]}

    # Initialise our API client using our token so that we can include it in all future requests
    credentials = BasicTokenAuthentication(api_token)
    client = lusid.LUSIDAPI(credentials, api_url)
    return client

def authenticate():
    api_url = os.getenv("FBN_LUSID_API_URL")
    api_token = {"access_token": os.environ["ACCESS_TOKEN"]}
    credentials = BasicTokenAuthentication(api_token)
    client = lusid.LUSIDAPI(credentials, api_url)
    return client

def create_scope_ids(num_scopes):
    """
    This function creates unique IDs for as many scopes as we need. There
    is a 1 in 36**4 = 1,679,616 chance of a collision. 
    
    Input
    num_scopes: Integer value for the number of identifiers that we need
    
    Output
    scopes: List of scope identifiers
    """ 
    scopes = [str(uuid.uuid4())[:4] for i in range(num_scopes)]
    
    return scopes


def import_file(csv_file):
    """
    This function is used to import data form our files
    """
    
    data = pd.read_csv('./data/{}'.format(csv_file))
    
    return data


def fetch_portfolio_names(csv_file):
    """
    This function loads the data from our portfolio names file and writes it to a dictionary
    
    Input
    csv_file: The name of the csv file including the extension i.e. .csv
    
    Output
    client_portfolios: Dictionary containing the client portfolios
    """
    
    portfolios = import_file(csv_file)
                
    client_portfolios = {}

    for index, portfolio_group, portfolio in portfolios.itertuples():
        
        client_portfolios.setdefault(portfolio_group, []).append(portfolio)
    
    return client_portfolios


def fetch_instrument_universe(csv_file, paper=False):
    """
    This function loads the data from our instruments file and writes it to a dictionary
    
    Input
    csv_file: The name of the csv file including the extension i.e. .csv
    paper: Whether or not this is for the paper portfolios use case
    
    Output
    instrument_universe: Dictionary containing the instrument universe
    """
    
    instruments = import_file(csv_file)
    
    instrument_universe = {}
    
    if paper:
        for index, instrument_name, currency, figi, ticker, isin, sedol in instruments.itertuples():
            instrument_universe[instrument_name] = {'identifiers': {'Figi': figi,
                                                                    'Isin': isin,
                                                                    'Sedol': sedol,
                                                                    'Ticker': ticker,
                                                                    'LUID': ''},
                                                    'currency': currency}
        
    else:
        for index, instrument_name, client_internal, currency in instruments.itertuples():
            instrument_universe[instrument_name] = {'identifiers': {'ClientInternal': client_internal,
                                                                    'LUID': ''},
                                                    'currency': currency}
    
    return instrument_universe


def fetch_instrument_market_cap(csv_file):
    """
    This function loads the data from our instruments market cap file and writes it to a dictionary
    
    Input
    csv_file: The name of the csv file including the extension i.e. .csv
    
    Output
    instrument_market_cap: Dictionary containing the market capitalisations
    """
    
    instruments = import_file(csv_file)
    
    
    instrument_market_cap = {}
    
    instruments = instruments.loc[:, ['instrument_name', 'marketcap']]
    
    for index, instrument_name, marketcap in instruments.itertuples():
        instrument_market_cap[instrument_name] = marketcap
        
    return instrument_market_cap


def fetch_instrument_analytics(csv_file):
    """
    This function loads the data from our instruments market cap file and writes it to a dictionary
    
    Input
    csv_file: The name of the csv file including the extension i.e. .csv
    
    Output
    instrument_market_cap: Dictionary containing the market capitalisations
    """
    
    instruments = import_file(csv_file)
    
    
    instrument_analytics = {}
    
    instruments = instruments.loc[:, ['instrument_name', 'price_original', 'price_current']]
    
    for index, instrument_name, price_original, price_current in instruments.itertuples():
        instrument_analytics[instrument_name] = (price_original, price_current)
        
    return instrument_analytics
    

def fetch_client_take_on_balances(csv_file):
    """
    This function loads the data from our take on balances file and writes it to a dictionary
    
    Input
    csv_file: The name of the csv file including the extension i.e. .csv
    
    Output
    client_holdings: Dictionary containing the client holdings
    """
    
    holdings = import_file(csv_file)
    
    client_holdings = {}
        
    for portfolio in holdings.loc[:, 'portfolio_name'].unique():
        client_holdings[portfolio] = {}
            
    for index, portfolio_group, portfolio, instrument_name, quantity, price in holdings.itertuples():
        client_holdings[portfolio][instrument_name] = {'quantity': quantity,
                                                       'price':price} 
    
    return client_holdings


def fetch_fund_accountant_daily_holdings_report(csv_file):
    """
    This function loads the data from our daily accountant report and writes it to a dictionary,
    the logic is exactly the same as fetch_client_take_on_balances so we just use that.
    
    Input
    csv_file: The name of the csv file including the extension i.e. .csv
    
    Output
    fund_accountant_daily_holdings_report: Dictionary containing the client holdings
    """
    
    fund_accountant_daily_holdings_report = fetch_client_take_on_balances(csv_file)
    
    return fund_accountant_daily_holdings_report



def client_transactions(csv_file, instrument_universe):
    """
    This function loads our transactions for our transactions export
    
    Input
    csv_file: The name of the csv file including the extension i.e. .csv
    instrument_universe: The instrument universe
    
    Output
    _client_transactions: Dictionary containing the client transactions
    """
        
    yesterday = datetime.now(pytz.UTC) - timedelta(days=1)
    t = time(hour=8, minute=0)
    yesterday_trade_open = pytz.utc.localize(datetime.combine(yesterday, t))
    transactions = import_file(csv_file)
    
    hours = [1,5,3,8.2,4,2,6,8.3]
    
    _client_transactions = {}
          
    for portfolio in transactions.loc[:, 'portfolio_name'].unique():
        _client_transactions[portfolio] = {}
            
    for index, portfolio_group, portfolio, trans_id, instr_id, ttype, units, tprice, tcurrency in transactions.itertuples():
        
        hour = hours[0]
        hours.pop(0)
        
        _client_transactions[portfolio][trans_id] = {'type': ttype,
                                                     'instrument_name': instr_id,
                                                     'instrument_uid': instrument_universe[instr_id]['identifiers']['LUID'],
                                                     'transaction_date': (yesterday_trade_open + timedelta(hours=hour)).isoformat(),
                                                     'settlement_date': (yesterday_trade_open + timedelta(days=hour)).isoformat(),
                                                     'units': units,
                                                     'transaction_price': tprice,
                                                     'transaction_currency': tcurrency}
                                                                       
    return _client_transactions, yesterday_trade_open

def fetch_client_transactions(csv_file, instrument_universe, days_back, portfolios=False):
    """
    This function loads the data from our daily accountant report and writes it to a dictionary,
    the logic is exactly the same as fetch_client_take_on_balances so we just use that.
    
    Input
    csv_file: The name of the csv file including the extension i.e. .csv
    instrument_universe: The instrument universe
    
    Output
    _client_transactions: Dictionary containing the client transactions
    """
        
    days_ago = datetime.now(pytz.UTC) - timedelta(days=days_back)
    t = time(hour=8, minute=0)
    days_ago_trade_open = pytz.utc.localize(datetime.combine(days_ago, t))
    
    transactions = import_file(csv_file)
    
    _client_transactions = {}
            
    for index, portfolio, trans_id, instr_name, trans_desc, trans_type, trans_units, trans_price, trans_currency, trans_strategy, trans_cost in transactions.itertuples():
        
        day = randint(0,days_back-1)
        hour = randint(0,8)
        minute = randint(0,59)
        second = randint(0,59)
        microsecond = randint(0, 999999)
        
        transaction_date = days_ago_trade_open + timedelta(days=day, hours=hour, minutes=minute, seconds=second, microseconds=microsecond)
        
        _client_transactions[trans_id] = {'type': trans_type,
                                          'portfolio': portfolio,
                                          'instrument_name': instr_name,
                                          'instrument_uid': instrument_universe[instr_name]['identifiers']['LUID'],
                                          'transaction_date': transaction_date.isoformat(),
                                          'settlement_date': (transaction_date + timedelta(days=2)).isoformat(),
                                          'units': trans_units,
                                          'transaction_price': trans_price,
                                          'transaction_currency': trans_currency,
                                          'total_cost': trans_cost,
                                          'strategy': trans_strategy}
        
    
    if portfolios:
        __client_transactions = {}
        for trans_id, transaction in _client_transactions.items():
            __client_transactions.setdefault(transaction['portfolio'], {})[trans_id] = transaction
    else:
        __client_transactions = _client_transactions
            

                                                                       
    return __client_transactions