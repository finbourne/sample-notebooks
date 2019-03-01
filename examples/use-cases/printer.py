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
                rec_properties = {rec_prop.key: rec_prop.value for rec_prop in reconciliation_break.instrument_properties}
                print (colours.bold + 'Reconciliation Break' + colours.end)
                print (colours.bold + 'Instrument: ' + colours.end + reconciliation_break.instrument_uid)
                print (colours.bold + 'Internal Units: ' + colours.end + str(reconciliation_break.left_units))
                print (colours.bold + 'Fund Accountant Units: ' + colours.end + str(reconciliation_break.right_units))
                print (colours.bold + 'Difference In Units: ' + colours.FAIL + str(reconciliation_break.difference_units) + colours.end)
                print (colours.bold + 'Internal Cost: ' + colours.end + str(reconciliation_break.left_cost.amount))
                print (colours.bold + 'Fund Accountant Cost: ' + colours.end + str(reconciliation_break.right_cost.amount))
                print (colours.bold + 'Difference In Cost: ' + colours.FAIL + str(reconciliation_break.difference_cost.amount) + colours.end)
                print (colours.bold + 'Currency: ' + colours.end + str(reconciliation_break.left_cost.currency))
                for key, value in rec_properties.items():
                    print (colours.bold + '{}: '.format(key) + colours.end + str(value))
                print('\n')
        print ('\n')

def reconciliation_response(response, scope, code):
    print (colours.bold + 'Reconciliation Breaks for Portfolio' + colours.end)
    print (colours.bold + 'Scope: ' + colours.end + scope)
    print (colours.bold + 'Code: ' + colours.end + code + '\n')
    if len(response.values) == 0:
        print (colours.bold + 'No Reconciliation Breaks' + colours.end)
    for reconciliation_break in response.values:
        rec_properties = {rec_prop.key: rec_prop.value for rec_prop in reconciliation_break.instrument_properties}
        print (colours.bold + 'Reconciliation Break' + colours.end)
        print (colours.bold + 'Instrument LUID: ' + colours.end + reconciliation_break.instrument_uid)
        print (colours.bold + 'Left Units: ' + colours.end + str(round(reconciliation_break.left_units,0)))
        print (colours.bold + 'Right Units: ' + colours.end + str(round(reconciliation_break.right_units,0)))
        print (colours.bold + 'Difference In Units: ' + colours.FAIL + str(round(reconciliation_break.difference_units,0)) + colours.end)
        print (colours.bold + 'Left Cost: ' + colours.end + str(round(reconciliation_break.left_cost.amount,2)))
        print (colours.bold + 'Right Cost: ' + colours.end + str(round(reconciliation_break.right_cost.amount,2)))
        print (colours.bold + 'Difference In Cost: ' + colours.FAIL + str(round(reconciliation_break.difference_cost.amount,2)) + colours.end)
        print (colours.bold + 'Currency: ' + colours.end + str(reconciliation_break.left_cost.currency))
        for key, value in rec_properties.items():
            print (colours.bold + '{}: '.format(key) + colours.end + str(value))
        print('\n')

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

def derived_portfolio_response(response):
    print (colours.bold + 'Portfolio Created' + colours.end)
    print (colours.bold + 'Scope: ' + colours.end + response.id.scope)
    print (colours.bold + 'Code: ' + colours.end + response.id.code)
    print (colours.bold + 'Parent Portfolio Scope: '  + colours.end + response.parent_portfolio_id.scope)
    print (colours.bold + 'Parent Portfolio Code: '  + colours.end + response.parent_portfolio_id.code)
    print (colours.bold + 'Portfolio Effective From: ' + colours.end + str(response.created))
    print (colours.bold + 'Portfolio Created On: ' + colours.end + str(response.version.as_at_date) + '\n')

def portfolio_response(response):
    if response.is_derived:
        print (colours.bold + 'Derived Portfolio Created' + colours.end)
        print (colours.bold + 'Scope: ' + colours.end + response.id.scope)
        print (colours.bold + 'Code: ' + colours.end + response.id.code)
        print (colours.bold + 'Portfolio Effective From: ' + colours.end + str(response.created))
        print (colours.bold + 'Portfolio Created On: ' + colours.end + str(response.version.as_at_date) + '\n')
        print (colours.bold + '   Parent Portfolio Details' + colours.end)
        print (colours.bold + '   Scope: ' + colours.end + response.parent_portfolio_id.scope)
        print (colours.bold + '   Code: ' + colours.end + response.parent_portfolio_id.code + '\n')
    else:
        print (colours.bold + 'Portfolio Created' + colours.end)
        print (colours.bold + 'Scope: ' + colours.end + response.id.scope)
        print (colours.bold + 'Code: ' + colours.end + response.id.code)
        print (colours.bold + 'Portfolio Effective From: ' + colours.end + str(response.created))
        print (colours.bold + 'Portfolio Created On: ' + colours.end + str(response.version.as_at_date) + '\n')

def portfolio_group_response(response, operation):
    if operation == 'created':
        print (colours.FAIL + colours.bold + 'Portfolio Group Created' + colours.end)
    elif operation == 'updated':
        print (colours.FAIL + colours.bold + 'Portfolio Group Updated' + colours.end)
    else:
        print (colours.FAIL + colours.bold + 'Portfolio Group' + colours.end)
    print (colours.bold + 'Name: ' + colours.end + response.display_name)
    print (colours.bold + 'Scope: ' + colours.end + response.id.scope)
    print (colours.bold + 'Code: ' + colours.end + response.id.code)
    print (colours.bold + 'Portfolios Inside Group: ' + colours.end)
    for portfolios in response.portfolios:
        print (portfolios.code)
    print ('\n')

def expansion_portfolio_response(response):
    if response.is_derived:
        print (colours.bold + 'Derived Portfolio ' + colours.end)
        print (colours.bold + 'Scope: ' + colours.end + response.id.scope)
        print (colours.bold + 'Code: ' + colours.end + response.id.code)
        print (colours.bold + 'Portfolio Effective From: ' + colours.end + str(response.created))
        print (colours.bold + 'Portfolio Created On: ' + colours.end + str(response.version.as_at_date) + '\n')
        print (colours.bold + '   Parent Portfolio Details' + colours.end)
        print (colours.bold + '   Scope: ' + colours.end + response.parent_portfolio_id.scope)
        print (colours.bold + '   Code: ' + colours.end + response.parent_portfolio_id.code + '\n')
    else:
        print (colours.bold + 'Portfolio ' + colours.end)
        print (colours.bold + 'Scope: ' + colours.end + response.id.scope)
        print (colours.bold + 'Code: ' + colours.end + response.id.code)
        print (colours.bold + 'Portfolio Effective From: ' + colours.end + str(response.created))
        print (colours.bold + 'Portfolio Created On: ' + colours.end + str(response.version.as_at_date) + '\n')


def expanded_portfolio_group_response(response):
    print (colours.FAIL + colours.bold + 'Portfolio Group Full Details : ' + colours.end)
    print (colours.bold + 'Scope: ' + colours.end + response.id.scope)
    print (colours.bold + 'Code: ' + colours.end + response.id.code)
    print (colours.OKBLUE + colours.bold + 'Portfolios Inside Group: ' + colours.end)
    for folio in response.values:
        expansion_portfolio_response(folio)
    print (colours.OKBLUE + colours.bold + 'Subgroups Inside Group: ' + colours.end)
    for sub in response.sub_groups:
        print (colours.bold + 'Name: ' + colours.end + sub.name)
        print (colours.bold + 'Scope: ' + colours.end + sub.id.scope)
        print (colours.bold + 'Code: ' + colours.end + sub.id.code)
        print (colours.OKBLUE + colours.bold + 'Portfolios Inside SubGroup: ' + colours.end)
        for folio in sub.values:
            expansion_portfolio_response(folio)
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

def output_transactions(response, scope, code, property_keys=[]):
    print (colours.bold + 'Output Transactions for Portfolio' + colours.end)
    print (colours.bold + 'Scope: ' + colours.end + scope)
    print (colours.bold + 'Code: ' + colours.end + code + '\n')
    for transaction in response.values:
        print (colours.bold + 'Transaction Id: ' + colours.end + transaction.transaction_id)
        print (colours.bold + 'Transaction Type: ' + colours.end + transaction.type)
        transaction_properties = {t_property.key: t_property.value for t_property in transaction.properties}
        for key, value in transaction_properties.items():
            if len(property_keys) > 0 and key not in property_keys:
                continue
            print (colours.bold + '{}: '.format(key) + colours.end + str(value))
        print (colours.bold + 'Units: ' + colours.end + str(transaction.units))
        print (colours.bold + 'Price: ' + colours.end + str(transaction.transaction_price.price))
        print (colours.bold + 'Currency: ' + colours.end + transaction.transaction_currency)
        print (colours.bold + 'Transaction Date: ' + colours.end + str(transaction.transaction_date))
        print (colours.bold + 'Settlement Date: ' + colours.end + str(transaction.settlement_date) + '\n')

def add_property_response(response, scope, portfolio_name, transaction_id):

    print (colours.bold + 'Property Successfully Added On Transaction in Portfolio' + colours.end)
    print (colours.bold + 'Transaction: ' + colours.end + transaction_id)
    print (colours.bold + 'Scope: ' + colours.end + scope)
    print (colours.bold + 'Code: ' + colours.end + portfolio_name)
    print (colours.bold + 'Property Effective From: ' + colours.end + str(response.version.effective_from))
    print (colours.bold + 'Property Created On: ' + colours.end + str(response.version.as_at_date) + '\n')

def holdings_response(response, scope, code):
    print (colours.bold + 'Holdings for Portfolio' + colours.end)
    print (colours.bold + 'Scope: ' + colours.end + scope)
    print (colours.bold + 'Code: ' + colours.end + code + '\n')
    for holding in response.values:
        holding_properties = {
            k: p.value.label_value if p.value.label_value is not None else p.value.metric_value.value
            for (k, p) in holding.properties.items()
        }
        for key, value in holding_properties.items():
            print (colours.bold + '{}: '.format(key) + colours.end + str(value))
        print (colours.bold + 'Units: ' + colours.end + str(holding.units))
        print (colours.bold + 'Cost: ' + colours.end + str(holding.cost.amount))
        print (colours.bold + 'Currency: ' + colours.end + holding.cost.currency)
        if holding.transaction is not None:
            print (colours.bold + 'Unsettled Transaction Id: ' + colours.end + str(holding.transaction.transaction_id))
            print (colours.bold + 'Settlement Date: ' + colours.end + str(holding.transaction.settlement_date))
        print ('\n')
            

def get_transactions_response(response, scope, code, property_keys=[]):
    print (colours.bold + 'Transactions Retrieved from Portfolio' + colours.end)
    print (colours.bold + 'Scope: ' + colours.end, scope)
    print (colours.bold + 'Code: ' + colours.end, code, '\n')
    for transaction in response.values:
        print ('Transaction Id: ', transaction.transaction_id)
        print ('Transaction Type: ', transaction.type)
        print ('Units: ', transaction.units)
        print ('Price: ', transaction.transaction_price.price)
        print ('Currency: ', transaction.transaction_currency)
        transaction_properties = {t_property.key: t_property.value for t_property in transaction.properties}
        for key, value in transaction_properties.items():
            if len(property_keys) > 0 and key not in property_keys:
                continue 
            print ('{}: '.format(key) + str(value))
        print ('Transaction Date: ', transaction.transaction_date, '\n')

def portfolio_properties_response(response):
    print (colours.bold + 'Properties Sucessfully Updated for Portfolio' + colours.end)
    print (colours.bold + 'Scope: ' + colours.end, response.origin_portfolio_id.scope)
    print (colours.bold + 'Code: ' + colours.end, response.origin_portfolio_id.code, '\n')
    for _property_key, _property_value in response.properties.items():
        print (colours.bold + 'Property key: ' + colours.end + _property_key)
        print (colours.bold + 'Value: ' + colours.end + _property_value.value.label_value + '\n')

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
        print (colours.bold + 'Return :' + colours.end + str(round(((result['Sum(Holding/default/PV)']-result['Sum(Holding/default/Cost)'])/result['Sum(Holding/default/Cost)'])*100*sign, 4)) + '%' + '\n')

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
    print (colours.bold + 'Effective From: ' + colours.end + analytic_store_response.key.date.isoformat())

def aggregation_response(agg_response):
    for agg_holding in agg_response.data:

        if agg_holding['Holding/default/SubHoldingKey'].split('=')[0] == 'Currency':
            currency = agg_holding['Holding/default/SubHoldingKey'].split('=')[1]
            
        else:
            currency = agg_holding['Holding/default/SubHoldingKey'].split('=')[1].split('/')[1]
            
        instrument_name = agg_holding['Instrument/default/Name']
        Luid = agg_holding['Holding/default/SubHoldingKey'].split('=')[1].split('/')[0]

        print (colours.bold + 'LUSID Instrument Id / Currency: ' + colours.end + Luid)
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

def aggregation_response_generic(response):
    print(colours.bold + 'Aggregation Results: ' + colours.end)
    
    for agg_result in response.data:
        for key, value in agg_result.items():
            print ('{}: {}'.format(key, value))
        print ('\n')

def transaction_type_response(response, filters=[]):
    i = 0
    j = 0
    for mapping in response.values:
        i += 1
        aliases = [alias.type for alias in mapping.aliases]
        matches = [value for value in aliases if value in filters]
        if len(matches) == 0 and len(filters)>=1:
            continue
        j += 1
        print (colours.bold + colours.UNDERLINE + 'Transaction Configuration #{}'.format(i) + colours.end + '\n')

        print (colours.bold + colours.FAIL + 'Transaction Type Aliases' + colours.end)
        for alias in mapping.aliases:
            if alias.type not in matches and len(filters)>=1:
                continue
            print (colours.bold + 'Transaction Type: ' + colours.end + colours.FAIL + alias.type + colours.end)
            print (colours.bold + 'Alias Description: ' + colours.end + alias.description)
            print (colours.bold + 'Transaction Class: ' + colours.end + alias.transaction_class)
            print (colours.bold + 'Transaction Group: ' + colours.end + alias.transaction_group)
            print (colours.bold + 'Transaction Roles: ' + colours.end + alias.transaction_roles + '\n' + '\n')

        print (colours.bold + colours.FAIL + 'Transaction Movements' + colours.end)
        for movement in mapping.movements:
            print (colours.bold + 'Movement Types: ' + colours.end + movement.movement_types)
            print (colours.bold + 'Side: ' + colours.end + movement.side)
            print (colours.bold + 'Direction: ' + colours.end + str(movement.direction))
            if len(movement.properties) > 0:
                for property_pair in movement.properties:
                    key = property_pair.key
                    value = property_pair.value
                    print (colours.bold + 'Properties: ' + colours.end + key + ': ' + value + '\n')
        print ('\n\n')
    if j == 0:
        print ('No matching transaction types in the configuration')


def group_commands(response, group_name):
    print (colours.bold + 'Commands Applied To Group ' + group_name + colours.end)
    print (colours.bold + 'Number of commands : ' + colours.end + str(len(response.links)))
    for command in response.values:
        print (colours.bold + 'Description : ' + colours.end + command.description)
        print (colours.bold + 'At Time : ' + colours.end + str(command.processed_time))
        print('\n')

# The following function prints the details obtained from 'GetPortfolioGroup'
def get_portfolio_group_response(response):
    print(colours.FAIL + colours.bold + 'Portfolio Group: ' + colours.end)
    print(colours.bold + 'Name: ' + colours.end + response.display_name)
    print(colours.bold + 'Scope: ' + colours.end + response.id.scope)
    print(colours.bold + 'Code: ' + colours.end + response.id.code)
    print(colours.bold + 'Portfolios Inside Group: ' + colours.end)
    for portfolios in response.portfolios:
        print(portfolios.code)
    print(colours.OKBLUE + colours.bold + 'Subgroups Inside Group: ' + colours.end)
    for subgroup in response.sub_groups:
        print(subgroup.code)
    print('\n')
# The following function prints the details obtained from 'GetPortfolioDetails'
def portfolio_details_response(response):
    print(colours.FAIL + colours.bold + 'Portfolio Details: ' + colours.end)
    print(colours.bold + 'Detail Origin Portfolio Scope: ' + colours.end + response.origin_portfolio_id.scope)
    print(colours.bold + 'Detail Origin Portfolio Code: ' + colours.end + response.origin_portfolio_id.code)
    print(colours.bold + 'Base Currency: ' + colours.end + response.base_currency)
    if hasattr(response, 'accounting_method'):
        print(colours.bold + 'Accounting Method: ' + colours.end + str(response.accounting_method))
    if hasattr(response, 'corporate_action_source_id'):
        print(colours.bold + 'Corporate Action Source Id: ' + colours.end + str(response.corporate_action_source_id))
    print('\n')


def groups_in_scope(response):
    print(colours.FAIL + colours.bold + 'Groups in Scope: ' + colours.end)
    for group in response.values:
        print(colours.bold + 'Scope : ' + colours.end + group.id.scope)
        print(colours.bold + 'Code : ' + colours.end + group.id.code)


def portfolio_filtering(parents_to_keep, derived_to_keep, parents_to_delete, derived_to_delete):
    print(colours.FAIL + colours.bold + 'Keeping : ' + colours.end)
    print(colours.OKBLUE + colours.bold + '    Parents: ' + colours.end)
    for p in [parents_to_keep]:
        print(colours.bold + '    Scope : ' + colours.end + p[0])
        print(colours.bold + '    Code : ' + colours.end + p[1] + '\n')
    print(colours.OKBLUE + colours.bold + '    Derived: ' + colours.end)
    for p in [derived_to_keep]:
        print(colours.bold + '    Scope : ' + colours.end + p[0])
        print(colours.bold + '    Code : ' + colours.end + p[1] + '\n')
    print(colours.FAIL + colours.bold + 'Deleting : ' + colours.end)
    print(colours.OKBLUE + colours.bold + '    Parents: ' + colours.end)
    for p in parents_to_delete:
        print(colours.bold + '    Scope : ' + colours.end + p[0])
        print(colours.bold + '    Code : ' + colours.end + p[1] + '\n')
    print(colours.OKBLUE + colours.bold + '    Derived: ' + colours.end)
    for p in derived_to_delete:
        print(colours.bold + '    Scope : ' + colours.end + p[0])
        print(colours.bold + '    Code : ' + colours.end + p[1] + '\n')


def remaining_portfolios(response, scope):
    print(colours.FAIL + colours.bold + 'Portfolios remaining in scope: ' + colours.end + scope + ':')
    for portfolio in response.values:
        portfolio_response(portfolio)


def get_identifiers(response, unique=False):
    for identifier in response.values:
        if identifier.is_unique_identifier == unique:
            print(colours.bold + '    Identifier Name : ' + colours.end + identifier.id_name)
            print(colours.bold + '    Is Unique Identifier : ' + colours.end + str(identifier.is_unique_identifier))
            print(colours.bold + '    Identifier Property Key Value : ' + colours.end + identifier.property_key_value)
            print ('\n')

            
def upsert_quotes_response(response):
    print (colours.bold + 'Quotes Successfully Upserted At: ' + colours.end + str(response.values.popitem()[1].as_at))


def corporate_action_response(response):
    print (colours.bold + 'Corporate Actions Source Successfully Created' + colours.end)
    print (colours.bold + 'Scope: ' + colours.end + response.id.scope)
    print (colours.bold + 'Code: ' + colours.end + response.id.code)

