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
import numpy as np
import hashlib
import time as default_time
from collections import UserString

class RefreshingToken(UserString):

    def __init__(self):

        token_data = {
            "expires": datetime.now(),
            "current_access_token": ''
        }

        current_access_token = ''

        def get_token():
            if token_data['expires'] <= datetime.now():
                with open("./../access_token.txt", "r") as access_token_file:
                    token_data['current_access_token'] = access_token_file.read()

                token_data['expires'] = datetime.now() + timedelta(seconds=120)

            return token_data['current_access_token']

        self.access_token = get_token

    def __getattribute__(self, name):
        token = object.__getattribute__(self, 'access_token')()
        if name == 'data':
            return token
        return token.__getattribute__(name)


def authenticate_secrets():
    
    class LusidApi():

        def __init__(self, client):
            self.aggregation = lusid.AggregationApi(client)
            self.metadata = lusid.ApplicationMetadataApi(client)
            self.corporate_action_sources = lusid.CorporateActionSourcesApi(client)
            self.data_types = lusid.DataTypesApi(client)
            self.derived_transaction_portfolios = lusid.DerivedTransactionPortfoliosApi(client)
            self.instruments = lusid.InstrumentsApi(client)
            self.login = lusid.InstrumentsApi(client)
            self.portfolio_groups = lusid.PortfolioGroupsApi(client)
            self.portfolios = lusid.PortfoliosApi(client)
            self.property_definitions = lusid.PropertyDefinitionsApi(client)
            self.quotes = lusid.QuotesApi(client)
            self.reconciliations = lusid.ReconciliationsApi(client)
            self.reference_portfolios = lusid.ReferencePortfolioApi(client)
            self.results = lusid.ResultsApi(client)
            self.schemas = lusid.SchemasApi(client)
            self.scopes = lusid.ScopesApi(client)
            self.search = lusid.SearchApi(client)
            self.system_configuration = lusid.SystemConfigurationApi(client)
            self.transaction_portfolios = lusid.TransactionPortfoliosApi(client)
            self.cut_labels = lusid.CutLabelDefinitionsApi(client)

    environment = os.getenv("FBN_DEPLOYMENT_ENVIRONMENT", None)

    if environment == "JupyterNotebook":
        api_url = os.getenv("FBN_LUSID_API_URL", None)
        if api_url is None:
            raise KeyError("Missing FBN_LUSID_API_URL environment variable, please set it to the LUSID base API url")
        api_factory = lusid.utilities.ApiClientFactory(
            token=RefreshingToken(),
            api_url=api_url,
            app_name="LusidJupyterNotebook")
        return api_factory

    dir_path = os.path.dirname(os.path.realpath(__file__))
    secrets_path = os.path.join(dir_path, "../secrets.json")

    api_factory = lusid.utilities.ApiClientFactory(api_secrets_filename=secrets_path)

    return api_factory

def authenticate():
    api_url = os.getenv("FBN_LUSID_API_URL")
    api_token = {"access_token": os.environ["ACCESS_TOKEN"]}
    credentials = BasicTokenAuthentication(api_token)
    client = lusid.LUSIDAPI(credentials, api_url)
    return client

def create_scope_id():
    """
    This function creates a unique ID based on the time since epoch for use 
    as a scope id.
    
    Output
    scopes: Scope identifier
    """ 
    # Get the current time since epoch
    test = default_time.time()
    # Multiply by 7 to get value to 100s of nano seconds
    timestamp = hex(int(test*10000000.0))
    # Create the scope id by joining the hex representation with dashes every 4 charachters
    scope_id = '-'.join(timestamp[i:i+4] for i in range(2, len(timestamp), 4))
    return scope_id

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
        instruments = instruments.loc[:, ['instrument_name', 'currency', 'figi', 'ticker','isin','sedol']]
        for index, instrument_name, currency, figi, ticker, isin, sedol in instruments.itertuples():
            instrument_universe[instrument_name] = {'identifiers': {'Figi': figi,
                                                                    'Isin': isin,
                                                                    'Sedol': sedol,
                                                                    'Ticker': ticker,
                                                                    'LUID': ''},
                                                    'currency': currency}
        
    else:
        instruments = instruments.loc[:, ['instrument_name', 'client_internal', 'currency']]
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

def fetch_client_transactions(csv_file, days_back):
    """
    This function loads the data from our daily accountant report and writes it to a dictionary,
    the logic is exactly the same as fetch_client_take_on_balances so we just use that.
    
    Input
    csv_file: The name of the csv file including the extension i.e. .csv
    
    Output
    _client_transactions: Dictionary containing the client transactions
    """
        
    days_ago = datetime.now(pytz.UTC) - timedelta(days=days_back)
    t = time(hour=8, minute=0)
    days_ago_trade_open = pytz.utc.localize(datetime.combine(days_ago, t))
    
    transactions = import_file(csv_file)
    
    _client_transactions = []
            
    for index, transaction in transactions.iterrows():
        
        day = randint(0,days_back-1)
        hour = randint(0,8)
        minute = randint(0,59)
        second = randint(0,59)
        microsecond = randint(0, 999999)
        
        transaction_date = days_ago_trade_open + timedelta(days=day, hours=hour, minutes=minute, seconds=second, microseconds=microsecond)
        
        if transaction['figi'] is not np.nan:
            identifier = transaction['figi']
        else:
            identifier = transaction['currency']
        
        _client_transactions.append(
            {'transaction_id': transaction['transaction_id'],
            'type':  transaction['transaction_type'],
            'portfolio':  transaction['portfolio_name'],
            'instrument_name':  transaction['instrument_name'],
            'instrument_uid': identifier,
            'transaction_date': transaction_date.isoformat(),
            'settlement_date': (transaction_date + timedelta(days=2)).isoformat(),
            'units':  transaction['transaction_units'],
            'transaction_price':  transaction['transaction_price'],
            'transaction_currency':  transaction['transaction_currency'],
            'total_cost':  transaction['transaction_cost'],
            'strategy':  transaction['transaction_strategy'],
            'description':  transaction['transaction_description'],
            'portfolio': transaction['portfolio_name']}
        )
        

    __client_transactions = pd.DataFrame(data=_client_transactions)
                                                                       
    return __client_transactions