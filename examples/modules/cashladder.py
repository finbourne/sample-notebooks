import lusid
import lusid.models as models
from datetime import datetime
import pandas as pd
import numpy as np
import os
import sample_login
import pytz

# Authenticate our user and create our API client
secrets_path = os.getenv("FBN_SECRETS_PATH")

# Create API client
api_factory = lusid.utilities.ApiClientFactory(
    token=RefreshingToken(), 
    api_secrets_filename = secrets_path,
    app_name="cashladder"
)

def arrayToDf(data,columns,*args):
    """
    Create a DataFrame from an array of objects
    
    Inputs
    data (list) - A list of objects
    columns (list) - A list of columns to add to the DataFrame
    
    Returns
    df (DataFrame) - A DataFrame containing the data 
    """
    
    def to_record(obj):
        """
        Takes an object and maps the attributes that we are interested in
        to a dictionary with the attribute name as the key and the value as 
        the value
        
        Inputs
        obj (object) - The object to convert to a dictionary
        
        Returns
        record (dictionary) - A dictionary of attribute-value pairs
        """
        
        # pick the values for the required columns of the object
        record = {col : getattr(obj,col) for col in columns}
        # checks to see if any properties exist
        props = getattr(obj,"properties",None)
        # if there are properties
        if props:
            # add the property to our dictionary
            record.update({"P:" + p.key : p.value.label_value for p in props.values()})
        # for any functions in our arguments, call them
        for f in args:
           # provides the record and object to the function
           f(record,obj)
        return record
    
    # converts a list of dictionaries with column names as keys into a DataFrame
    df = pd.DataFrame.from_records([to_record(o) for o in data])
    
    # returns a dataframe with the columns in alphabetical order
    return df[sorted(df.columns.values)]

def qry_holdings(date,scope,portfolio):
    """
    This returns the positions of a portfolio as a DataFrame
    
    Inputs
    date (datetime) - The date to get the positions for
    scope (string) - The scope of the portfolio to get positions for
    portfolio (string) - The code of the portfolio to get positions for
    
    Returns
    df (Pandas DataFrame) - Contains the positions of the portfolio
    """
    
    # ensure the date is in datetime format and not a string
    qry_date = pd.to_datetime(date,utc=True)
    
    def getTxnDetails(record,src):
        """
        This function that takes a dictionary of 
        
        Inputs
        record (dictionary) - Dictionary of atttribute-value pairs generated
        from an object
        src (object) - The source object 
        
        Returns
        N/A
        """
        
        # see if there is a tansaction attached to this holding object
        t = src.transaction
        
        # if there is a transaction
        if(t):
            # create a dictionary with the transaction data
            txn_data = {'commitment': t.type,
                        'commitment_instrument_uid': t.instrument_uid,
                        'settlement_date': pd.to_datetime(t.settlement_date,utc=True)}
            # update our record with the transaction data
            record.update(txn_data)
    
    # call LUSID to get the portfolios holdings
    holdings = api_factory.build(lusid.api.TransactionPortfoliosApi).get_holdings(
        scope=scope,
        code=portfolio,
        effective_at=qry_date)

    # set the columns we are interested in from the holdings
    columns = ['holding_type','instrument_uid','units']
    
    # create a dataframe from the 
    df = arrayToDf(holdings.values, columns, getTxnDetails)
    
    #Add in empty transaction details if they are missing from all holdings
    if 'commitment' not in df.columns.values:
        for col in ['commitment','commitment_instrument_uid','settlement_date']:
           df[col] = np.nan;
    return df;

def qry_transactions(scope,id):
    txn_columns = ['trade_id', 'type', 'instrument_uid', 'trade_date', 'settlement_date', 'units',
               'trade_price', 'total_consideration', 'exchange_rate', 'settlement_currency',
               'trade_currency', 'counterparty_id', 'source', 'dividend_state',
               'trade_price_type', 'unit_type', 'netting_set']
    
    transactions = api_factory.build(lusid.api.TransactionPortfoliosApi).get_trades(
        scope=scope, 
        code=id)
    
    return arrayToDf(transactions.values,txn_columns)
        
def cash_ladder(date,scope,portfolio):
    """
    This function produces a cash ladder
    
    Inputs
    date (string) - The date to produce the cash ladder for 
    scope (string) - The scope of the portfolio to produce the cash ladder for
    portfolio (string) - The code of the portfolio to produce the cash ladder for
    
    Returns
    
    """
    
    # set some commonly used strings as variables for easier access
    SDATE='settlement_date'
    CCY='instrument_uid'
    QTY='units'
    TYPE='holding_type'
    CUM='cum'
    ORDER='sort'
    JOIN='join'
    
    # convert the date string to a datetime
    qry_date = pd.to_datetime(date,utc=True)
    
    def check_contents(df):
        """
        This function checks the length of a dataframe (no. rows) if it is 0 it
        returns a printed message noting that there is no holdings in the portfolio
        
        Inputs
        df (Pandas DataFrame) - The dataframe containing the portfolio positions
        """
        
        if len(df) == 0:
            print(
                "Portfolio {} in scope {} contains no cash on {:%Y-%m-%d}".format(
                    portfolio,scope,start_date)
            )

    # Run one-day earlier, this gives us the beginning of day for the 
    # required qry_date
    start_date = qry_date + pd.DateOffset(days=-1)

    # Generate a Pandas DataFrame with then holdings of the portfolio
    df = qry_holdings(start_date,scope,portfolio)
    
    # Check that the portfolio contains holdings
    check_contents(df)

    # To convert holdings data frame into cash ladder
    # we need to filter out Position types which hold instruments other than cash
    df = df[df[TYPE] != 'P'].copy()

    # Check that the portfolio contains cash after applying the filter
    check_contents(df)
    
    # Set start date for current balances
    df[SDATE] = df[SDATE].fillna(start_date).dt.date

    # Aggregate the cash balances 
    df = df[[CCY,SDATE,TYPE,QTY]].groupby([CCY,SDATE,TYPE],as_index=False).sum()

    #Populate BOD/EOD records

    start_date = start_date.date() # change form for working with frame data

    #Get unique list of dates, but make sure it includes the qry_date
    dates=pd.concat([
        df[[SDATE]], 
        pd.DataFrame(
            {
                SDATE:[qry_date.date()]
            }
        )
    ], ignore_index=True, sort=False).drop_duplicates()
    
    # Get all dates greater than the start date
    dates=dates[dates[SDATE]>start_date]
    
    # Get all currencies
    ccys =df[[CCY]].drop_duplicates()
    
    ccys[JOIN]=1
    dates[JOIN]=1
    dates[QTY]=0
    dates[ORDER]=1
    dates[TYPE]='Opening Cash Balance'
    bod = ccys.merge(dates,on=JOIN)
    eod = bod.copy()
    eod[ORDER]=5
    eod[TYPE]= eod[CCY].str.slice(4) + " Summary"

    df[ORDER] = df[TYPE].map({'C':2,'A':3,'R':4})
    df[TYPE] = df[TYPE].map({'C':'Trades to settle','R':'Estimated funding','A':'Dividend'})

    df = pd.concat([bod,eod,df],ignore_index=True, sort=False).sort_values([CCY,SDATE,ORDER]).reset_index(drop=True)

    #Calculate cumulative quantity
    df[CUM] = df[[CCY,QTY]].groupby([CCY],as_index=False).cumsum()[QTY]

    #Put cumulative balance onto BOD/EOD records
    subset = df[df[ORDER].isin([1,5])]
    df.loc[subset.index,QTY] = subset[CUM]

    #Filter out T-1 balances (just used to provide BOD balance)

    df = df[df[SDATE] > start_date]

    #Pivot the data
    data = df.set_index([CCY,ORDER,TYPE,SDATE],drop=True).unstack(fill_value=0)
    return data[QTY]

def alt_cash_ladder(date,scope,portfolio):
    qry_date = pd.to_datetime(date,utc=True)
    # Run one-day earlier, this gives us the beginning of day for the 
    # required qry_date
    start_date = qry_date +  pd.DateOffset(days=-1)
    df = qry_holdings(start_date,scope,portfolio)
 
    # filter out Position types
    df = df[df['holding_type'] != 'P']

    df['settlement_date'] = pd.to_datetime(df['settlement_date'].fillna(qry_date),utc=True).dt.date
    df = df.sort_values(['instrument_uid','settlement_date'])
    df['balance'] = df[['instrument_uid','units']].groupby(['instrument_uid'],as_index=False).cumsum()['units']

    columns = ['instrument_uid','settlement_date','commitment','holding_type','commitment_instrument_uid','units','balance']

    df = df[columns].rename(columns={'instrument_uid':'Currency',
                                'settlement_date':'Cash Date',
                                'commitment':'Transaction Type',
                                'holding_type':'Cash Type',
                                'units':'Local Cash Amount'})
    return df.fillna('')
