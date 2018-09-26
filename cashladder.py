import lusid
import lusid.models as models
from datetime import datetime
import pandas as pd
import numpy as np
import os
from msrest.authentication import BasicTokenAuthentication

api_url = os.getenv("FBN_LUSID_API_URL")
api_token = {"access_token": os.environ["ACCESS_TOKEN"]}
credentials = BasicTokenAuthentication(api_token)
client = lusid.LUSIDAPI(credentials, api_url)

#create a DataFrame from an array of objects
def arrayToDf(data,columns,*args):
    def to_record(obj):
        record = {col : getattr(obj,col) for col in columns}
        props = getattr(obj,"properties",None)
        if props:
            record.update({"P:" + p.key : p.value for p in props})
        for f in args:
           f(record,obj)
        return record

    df = pd.DataFrame.from_records([to_record(o) for o in data])

    return df[sorted(df.columns.values)]

def qry_holdings(date,scope,portfolio):
    qry_date = pd.to_datetime(date,utc=True)
    def getTxnDetails(record,src):
        t = src.transaction
        if(t):
            txn_data = {'commitment': t.type,
                        'commitment_instrument_uid': t.instrument_uid,
                        'settlement_date': t.settlement_date}
            record.update(txn_data)
             
    holdings = client.get_holdings(scope,portfolio,qry_date)

    columns = ['holding_type','instrument_uid','units']
    df =  arrayToDf(holdings.values, columns, getTxnDetails)
    #Add in empty transaction details if they are missing
    if 'commitment' not in df.columns.values:
        for col in ['commitment','commitment_instrument_uid','settlement_date']:
           df[col] = np.nan;
    return df;

def qry_transactions(scope,id):
    txn_columns = ['trade_id', 'type', 'instrument_uid', 'trade_date', 'settlement_date', 'units',
               'trade_price', 'total_consideration', 'exchange_rate', 'settlement_currency',
               'trade_currency', 'counterparty_id', 'source', 'dividend_state',
               'trade_price_type', 'unit_type', 'netting_set']
    transactions = client.get_trades(scope, id)
    return arrayToDf(transactions.values,txn_columns)
        
def cash_ladder(date,scope,portfolio):
    SDATE='settlement_date'
    CCY='instrument_uid'
    QTY='units'
    TYPE='holding_type'
    CUM='cum'
    ORDER='sort'
    JOIN='join'
    qry_date = pd.to_datetime(date,utc=True)
    def check_contents(df):
        if len(df) == 0:
            print("Portfolio {} in scope {} contains no cash on {:%Y-%m-%d}".format(portfolio,scope,start_date))

    # Run one-day earlier, this gives us the beginning of day for the 
    # required qry_date
    start_date = qry_date +  pd.DateOffset(days=-1)
    df = qry_holdings(start_date,scope,portfolio)
    check_contents(df)

    # To convert holdings data frame into cash ladder
    # we need to filter out Position types
    df = df[df[TYPE] != 'P'].copy()
    check_contents(df)

    #Set date for current balances
    df[SDATE] = pd.to_datetime(df[SDATE].fillna(start_date),utc=True).dt.date

    #Consolidate
    df = df[[CCY,SDATE,TYPE,QTY]].groupby([CCY,SDATE,TYPE],as_index=False).sum()

    #Populate BOD/EOD records

    start_date = start_date.date() # change form for working with frame data
    #Get unique list of dates, but make sure it includes the qry_date
    dates=pd.concat([df[[SDATE]], pd.DataFrame({SDATE:[qry_date.date()]})],ignore_index=True).drop_duplicates()
    dates=dates[dates[SDATE]>start_date]
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

    df = pd.concat([bod,eod,df],ignore_index=True).sort_values([CCY,SDATE,ORDER]).reset_index(drop=True)

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
