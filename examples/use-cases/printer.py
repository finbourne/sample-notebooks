import pandas as pd

# Used to make our print functions a little prettier
class colours:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    end = '\033[0m'
    bold = '\033[1m'
    UNDERLINE = '\033[4m'
    
def heading(heading, text, newline=False):
    if newline == False:
        print (colours.bold + heading + ': ' + colours.end + text)
    else:
        print (colours.bold + heading + ': ' + colours.end + text + '\n')
    
def portfolios(client_portfolios):
    for portfolio_group_name, portfolio_group in client_portfolios.items():
        print (colours.bold + 'Portfolio group: ' + colours.end + portfolio_group_name)
        for portfolio_name in portfolio_group:
            print ('   ' + colours.bold + 'Portfolio: ' + colours.end + portfolio_name)
        print('\n')
        
def portfoliosint(internal_portfolios):
    for portfolio_group in internal_portfolios.values:
        print (colours.bold + 'Portfolio Group: ' + colours.end + portfolio_group.id.code)
        for portfolio in portfolio_group.portfolios:
            print (colours.bold + 'Portfolio: ' + colours.end + portfolio.code)
        print('\n')
        
def instruments(instrument_universe, identifier='LUID'):
    for instrument_name, instrument in instrument_universe.items():
        print (instrument_name + ': ' + colours.bold + identifier + ' - ' + instrument['identifiers'][identifier] + colours.end)
        
def instruments_market_cap(instrument_universe):
    for instrument_name, marketcap in instrument_universe.items():
        print (colours.bold + instrument_name + ': ' + colours.end + '£' + str(marketcap) + ' (millions)')
        
def instrumentspd(instrument_universe, identifier=['LUID']):
    identifier.append('currency')
    test1 = pd.DataFrame.from_dict(data=instrument_universe, orient='index')
    test2 = test1['identifiers'].apply(pd.Series)
    test1 = test1.drop(['identifiers'], axis=1)
    test = pd.concat([test1, test2], axis=1).loc[:, identifier]
    return (test.head(n=500))
        
def reconciliation(reconciled_portfolios, flag=False):
    if flag:
        print ('No reconciliation breaks')
    else:
        for portfolio_name, reconciliation_breaks in reconciled_portfolios.items():
            print (colours.bold + 'Portfolio: ' + colours.end + portfolio_name + '\n')
            for reconciliation_break in reconciliation_breaks.values:
                print (colours.bold + 'Reconciliation Break' + colours.end)
                print (colours.bold + 'Instrument: ' + colours.end + reconciliation_break.instrument_uid)
                print (colours.bold + 'Internal Units: ' + colours.end + str(reconciliation_break.left_units))
                print (colours.bold + 'Fund Accountant Units: ' + colours.end + str(reconciliation_break.right_units))
                print (colours.bold + 'Difference In Units: ' + colours.FAIL + str(reconciliation_break.difference_units) + colours.end)
                print (colours.bold + 'Internal Cost: ' + colours.end + str(reconciliation_break.left_cost.amount))
                print (colours.bold + 'Fund Accountant Cost: ' + colours.end + str(reconciliation_break.right_cost.amount))
                print (colours.bold + 'Difference In Cost: ' + colours.FAIL + str(reconciliation_break.difference_cost.amount) + colours.end)
                print (colours.bold + 'Currency: ' + colours.end + str(reconciliation_break.left_cost.currency))
                print('\n')
        print ('\n')
            
def trades(late_trades):

    for portfolio_name, late_trade in late_trades.items():
        print (colours.bold + 'Portfolio: ' + colours.end + portfolio_name + '\n')
        for trade in late_trade.values:
            print (colours.bold + 'Transaction: ' + colours.end + trade.transaction_id)
            print (colours.bold + 'Instrument: ' + colours.end + trade.instrument_uid)
            print (colours.bold + 'Type: ' + colours.end + trade.type)
            print (colours.bold + 'Units: ' + colours.end + str(trade.units))
            print (colours.bold + 'Price: ' + colours.end + str(trade.transaction_price.price))
            print (colours.bold + 'Currency: ' + colours.end + trade.transaction_currency)
            print (colours.bold + 'Transaction Date: ' + colours.end + str(trade.transaction_date))
            print ('\n')
                    
def exceptions(matched_exceptions):

    for exception in matched_exceptions:
        
        trade = exception[0]
        reconciliation_break = exception[1]
        
        print (colours.bold + 'Transaction: ' + colours.end + trade.transaction_id)
        print (colours.bold + 'Instrument: ' + colours.FAIL + trade.instrument_uid + colours.end)
        print (colours.bold + 'Type: ' + colours.end + trade.type)
        print (colours.bold + 'Units: ' + colours.FAIL + str(trade.units) + colours.end)
        print (colours.bold + 'Price: ' + colours.end + str(trade.transaction_price.price))
        print (colours.bold + 'Currency: ' + colours.end + trade.transaction_currency + '\n')
        
        print (colours.WARNING + 'MATCHES' + colours.end + '\n')
        
        print (colours.bold + 'Reconciliation Break' + colours.end)
        print (colours.bold + 'Instrument: ' + colours.FAIL + reconciliation_break.instrument_uid + colours.end)
        print (colours.bold + 'Internal Units: ' + colours.end + str(reconciliation_break.left_units))
        print (colours.bold + 'Fund Accountant Units: ' + colours.end + str(reconciliation_break.right_units))
        print (colours.bold + 'Difference In Units: ' + colours.FAIL + str(reconciliation_break.difference_units) + colours.end)
        print (colours.bold + 'Internal Cost: ' + colours.end + str(reconciliation_break.left_cost.amount))
        print (colours.bold + 'Fund Accountant Cost: ' + colours.end + str(reconciliation_break.right_cost.amount))
        print (colours.bold + 'Difference In Cost: ' + colours.end + str(reconciliation_break.difference_cost.amount))
        print (colours.bold + 'Currency: ' + colours.end + str(reconciliation_break.left_cost.currency))
        print('\n\n')
                
        
                
def holdings(client_holdings):

    for portfolio_name, holdings in client_holdings.items():
        print (colours.bold + 'Portfolio: ' + colours.end + portfolio_name + '\n')
        for holding_name, holding in holdings.items():
            print (colours.bold + 'Instrument Name: ' + colours.end + holding_name)
            print (colours.bold + 'Quantity: ' + colours.end + str(holding['quantity']))
            print (colours.bold + 'CostPrice: ' + colours.end + str(holding['price']) + '\n')
        print ('\n\n')
        
def transactions(transaction_list, strategy=False):

    for portfolio_name, transactions_list in transaction_list.items():
        print (colours.bold + 'Portfolio: ' + colours.end + portfolio_name + '\n')
        for transaction_id, transaction in transactions_list.items():
            print (colours.bold + 'Transaction: ' + colours.end + transaction_id)
            print (colours.bold + 'Instrument Name: ' + colours.end + transaction['instrument_name'])
            print (colours.bold + 'Instrument LUID: ' + colours.end + transaction['instrument_uid'])
            print (colours.bold + 'Type: ' + colours.end + transaction['type'])
            print (colours.bold + 'Units: ' + colours.end + str(transaction['units']))
            print (colours.bold + 'Price: ' + colours.end + str(transaction['transaction_price']))
            print (colours.bold + 'Currency: ' + colours.end + transaction['transaction_currency'])
            print (colours.bold + 'Transaction Date: ' + colours.end + transaction['transaction_date'])
            print (colours.bold + 'Settlement Date: ' + colours.end + transaction['settlement_date'] + '\n')
        print ('\n')
        
def transactions_strategy(transaction_list, portfolios=False):
    
    if portfolios:
        for portfolio_name, transactions_list in transaction_list.items():
            print (colours.bold + 'Portfolio: ' + colours.end + portfolio_name + '\n')
            for transaction_id, transaction in transactions_list.items():
                print (colours.bold + 'Transaction: ' + colours.end + transaction_id)
                print (colours.bold + 'Instrument Name: ' + colours.end + transaction['instrument_name'])
                print (colours.bold + 'Instrument Id: ' + colours.end + str(transaction['instrument_uid']))
                print (colours.bold + 'Type: ' + colours.end + transaction['type'])
                print (colours.bold + 'Units: ' + colours.end + str(transaction['units']))
                print (colours.bold + 'Price: ' + colours.end + str(transaction['transaction_price']))
                print (colours.bold + 'Total Cost: ' + colours.end + str(transaction['total_cost']))
                print (colours.bold + 'Currency: ' + colours.end + transaction['transaction_currency'])
                print (colours.bold + 'Transaction Date: ' + colours.end + transaction['transaction_date'])
                print (colours.bold + 'Settlement Date: ' + colours.end + transaction['settlement_date'])
                print (colours.bold + 'Description: ' + colours.end + transaction['description'])
                print (colours.bold + 'Strategy: ' + colours.end + transaction['strategy'] + '\n')
            print ('\n')
        
    else:
        for transaction_id, transaction in transaction_list.items():
            print (colours.bold + 'Transaction: ' + colours.end + transaction_id)
            print (colours.bold + 'Portfolio: ' + colours.end + transaction['portfolio'])
            print (colours.bold + 'Instrument Name: ' + colours.end + transaction['instrument_name'])
            print (colours.bold + 'Instrument Id: ' + colours.end + str(transaction['instrument_uid']))
            print (colours.bold + 'Type: ' + colours.end + transaction['type'])
            print (colours.bold + 'Units: ' + colours.end + str(transaction['units']))
            print (colours.bold + 'Price: ' + colours.end + str(transaction['transaction_price']))
            print (colours.bold + 'Total Cost: ' + colours.end + str(transaction['total_cost']))
            print (colours.bold + 'Currency: ' + colours.end + transaction['transaction_currency'])
            print (colours.bold + 'Transaction Date: ' + colours.end + transaction['transaction_date'])
            print (colours.bold + 'Settlement Date: ' + colours.end + transaction['settlement_date'])
            print (colours.bold + 'Description: ' + colours.end + transaction['description'])
            print (colours.bold + 'Strategy: ' + colours.end + transaction['strategy'] + '\n')
        print ('\n')
    
            
def portfolio_response(response):
    print (colours.bold + 'Portfolio Created' + colours.end)
    print (colours.bold + 'Scope: ' + colours.end + response.id.scope)
    print (colours.bold + 'Code: ' + colours.end + response.id.code)
    print (colours.bold + 'Portfolio Effective From: ' + colours.end + str(response.created))
    print (colours.bold + 'Portfolio Created On: ' + colours.end + str(response.version.as_at_date) + '\n')
    
def derived_portfolio_response(response):
    print (colours.bold + 'Portfolio Created' + colours.end)
    print (colours.bold + 'Scope: ' + colours.end + response.id.scope)
    print (colours.bold + 'Code: ' + colours.end + response.id.code)
    print (colours.bold + 'Parent Portfolio Scope: '  + colours.end + response.parent_portfolio_id.scope)
    print (colours.bold + 'Parent Portfolio Code: '  + colours.end + response.parent_portfolio_id.code)
    print (colours.bold + 'Portfolio Effective From: ' + colours.end + str(response.created))
    print (colours.bold + 'Portfolio Created On: ' + colours.end + str(response.version.as_at_date) + '\n')
    
def portfolio_group_response(response):
    print (colours.FAIL + colours.bold + 'Portfolio Group Created' + colours.end)
    print (colours.bold + 'Scope: ' + colours.end + response.id.scope)
    print (colours.bold + 'Code: ' + colours.end + response.id.code)
    print (colours.bold + 'Portfolios Inside Group: ' + colours.end)
    for portfolios in response.portfolios:
        
        print (portfolios.code)
    print ('\n')
    
    
def instrument_response(response, identifier='ClientInternal'):
    
    for instrument_name, instrument in response.values.items():
        print (colours.bold + 'Instrument Successfully Upserted: ' + colours.end + instrument_name)
        print (colours.bold + '{} ID: '.format(identifier) + colours.end + instrument.identifiers[identifier])
        print (colours.bold + 'LUSID Instrument ID: ' + colours.end + instrument.lusid_instrument_id)
        print ('\n')
    
    print (len(response.values), ' instruments upserted successfully')
    print (len(response.failed), ' instrument upsert failures') 
    
def set_holdings_response(response, scope, portfolio_name):
    
    print (colours.bold + 'Holdings Successfully Set for Portfolio' + colours.end)
    print (colours.bold + 'Scope: ' + colours.end + scope)
    print (colours.bold + 'Code: ' + colours.end + portfolio_name)
    print (colours.bold + 'Holdings Effective From: ' + colours.end + str(response.version.effective_from))
    print (colours.bold + 'Holdings Created On: ' + colours.end + str(response.version.as_at_date) + '\n')
    
def transactions_response(response, scope, portfolio_name):
    
    print (colours.bold + 'Transactions Successfully Upserted into Portfolio' + colours.end)
    print (colours.bold + 'Scope: ' + colours.end + scope)
    print (colours.bold + 'Code: ' + colours.end + portfolio_name)
    print (colours.bold + 'Transactions Effective From: ' + colours.end + str(response.version.effective_from))
    print (colours.bold + 'Transactions Created On: ' + colours.end + str(response.version.as_at_date) + '\n')

def adjust_holdings_response(response, scope, portfolio_name):
    
    print (colours.bold + 'Holdings Successfully Adjusted for Portfolio' + colours.end)
    print (colours.bold + 'Scope: ' + colours.end + scope)
    print (colours.bold + 'Code: ' + colours.end + portfolio_name)
    print (colours.bold + 'Adjusted Holdings Effective From: ' + colours.end + str(response.version.effective_from))
    print (colours.bold + 'Adjusted Holdings Created On: ' + colours.end + str(response.version.as_at_date) + '\n')
    
def add_property_response(response, scope, portfolio_name, transaction_id):
    
    print (colours.bold + 'Property Successfully Added On Transaction in Portfolio' + colours.end)
    print (colours.bold + 'Transaction: ' + colours.end + transaction_id)
    print (colours.bold + 'Scope: ' + colours.end + scope)
    print (colours.bold + 'Code: ' + colours.end + portfolio_name)
    print (colours.bold + 'Property Effective From: ' + colours.end + str(response.version.effective_from))
    print (colours.bold + 'Property Created On: ' + colours.end + str(response.version.as_at_date) + '\n')

def holdings_response(response, scope, code):
    print (colours.bold + 'Holdings in Portfolio' + colours.end)
    print (colours.bold + 'Scope: ' + colours.end, scope)
    print (colours.bold + 'Code: ' + colours.end, code, '\n')
    for holding in response.values:
        print ('Instrument Name: ', holding.properties[0].value)
        print ('Units: ', holding.units)
        print ('Cost: ', round(holding.cost.amount,2))
        print ('Currency: ', holding.cost.currency +'\n')
        
def get_transactions_response(response, scope, code):
    print (colours.bold + 'Transactions Retrieved from Portfolio' + colours.end)
    print (colours.bold + 'Scope: ' + colours.end, scope)
    print (colours.bold + 'Code: ' + colours.end, code, '\n')
    for transaction in response.values:
        print ('Transaction Id: ', transaction.transaction_id)
        print ('Transaction Type: ', transaction.type)
        print ('Instrument Name :', transaction.properties[2].value)
        print ('Units: ', transaction.units)
        print ('Price: ', transaction.transaction_price.price)
        print ('Currency: ', transaction.transaction_currency)
        print ('Transaction Date: ', transaction.transaction_date, '\n')
            

def aggregation_response_paper(response):
    total_cost = 0
    total_pv = 0
    
    for result in response.data:
        if 'Currency' in result['Holding/default/SubHoldingKey']:
            continue
        sign = result['Sum(Holding/default/Units)'] / abs(result['Sum(Holding/default/Units)'])
        print (colours.bold + 'Instrument :' + colours.end + result['Holding/default/SubHoldingKey'])
        print (colours.bold + 'Units :' + colours.end + str(round(result['Sum(Holding/default/Units)'],0)))
        print (colours.bold + 'Current Price :' + '£' + colours.end + str(round(result['Sum(Holding/default/Price)'], 2)))
        print (colours.bold + 'Present Value :' + colours.end + '£' + str(round(result['Sum(Holding/default/PV)'],2)))
        print (colours.bold + 'Cost :' + colours.end + '£' + str(round(result['Sum(Holding/default/Cost)'], 2)))
        print (colours.bold + 'Return :' + colours.end + str(round(((result['Sum(Holding/default/PV)']-result['Sum(Holding/default/Cost)'])/result['Sum(Holding/default/Cost)'])*100*sign,4)) + '%' + '\n')
        
        total_cost += result['Sum(Holding/default/Cost)']
        total_pv += result['Sum(Holding/default/PV)']
        
    print (colours.bold + 'TOTAL RETURN: ' + colours.end + str(round(((total_pv-total_cost)/total_cost)*100,4)) + '%')
        
def instrument_prices(instrument_analytics):
    for instrument_name, prices in instrument_analytics.items():
        print (colours.bold + 'Instrument :' + colours.end + instrument_name)
        print (colours.bold + 'Price 3 Days Ago :' + colours.end + '£' + str(round(prices[0],2)))
        print (colours.bold + 'Price Today :' + colours.end + '£' + str(round(prices[1],2)) + '\n')

def analytic_store(analytic_store_response, analytics=False):
    if analytics:
        print (colours.bold + 'Analytics Set' + colours.end)
    else:
        print (colours.bold + 'Analytic Store Created' + colours.end)
    print (colours.bold + 'Scope: ' + colours.end + analytic_store_response.key.scope)
    print (colours.bold + 'Effective From: ' + colours.end + analytic_store_response.key.date_property.isoformat())

def aggregation_response(agg_response):
    for agg_holding in agg_response.data:

        if agg_holding['Instrument/default/Name'] == '<Unknown>':
            instrument_name = 'Cash'
            Luid = 'CCY_' + agg_holding['Holding/default/SubHoldingKey'].split('=')[1].split('/')[0]
            currency = agg_holding['Holding/default/SubHoldingKey'].split('=')[1]
        else:
            instrument_name = agg_holding['Instrument/default/Name']
            Luid = agg_holding['Holding/default/SubHoldingKey'].split('=')[1].split('/')[0]
            currency = agg_holding['Holding/default/SubHoldingKey'].split('=')[1].split('/')[1]
            
        print (colours.bold + 'LUSID Instrument Id: ' + colours.end + Luid)
        print (colours.bold + 'Instrument Name: ' + colours.end + instrument_name)
        print (colours.bold + 'Instrument Units: ' + colours.end + str(round(agg_holding['Sum(Holding/default/Units)'],2)))
        print (colours.bold + 'Instrument Cost: ' + colours.end + str(round(agg_holding['Sum(Holding/default/Cost)'],2)))
        print (colours.bold + 'Instrument Currency: ' + colours.end + currency + '\n')
        
def aggregation_response_strategy(agg_response, strategy_key):
    for agg_holding in agg_response.data:

        strategy = agg_holding[strategy_key]
        print (colours.bold + 'Strategy: ' + colours.end + strategy)
        print (colours.bold + 'Strategy Cost: ' + colours.end + str(round(agg_holding['Sum(Holding/default/Cost)'],2)) + '\n')
    
def aggregation_response_index(agg_response):
    base = 0
    present = 0

    for d in agg_response.data:
        base += d['Sum(Holding/default/Cost)']
        present += d['Sum(Holding/default/PV)']
    total_return = (present-base)/base

    print (colours.bold + 'Initial Index Level :' + colours.end + str(round(base,2)))
    print (colours.bold + 'Current Index Level :' + colours.end + str(round(present,2)))
    print (colours.bold + 'Return :' + colours.end + str(round(total_return*100,4)) + '%')