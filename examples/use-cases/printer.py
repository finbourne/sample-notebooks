import pandas as pd
import lusid
import numpy as np
pd.set_option('display.float_format', lambda x: '%.2f' % x)

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

    if isinstance(response, lusid.models.PortfolioDetails):
        portfolio_details_response(response)

    else:
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
        print (colours.bold + 'Name: ' + colours.end + sub.display_name)
        print (colours.bold + 'Scope: ' + colours.end + sub.id.scope)
        print (colours.bold + 'Code: ' + colours.end + sub.id.code)
        print (colours.OKBLUE + colours.bold + 'Portfolios Inside SubGroup: ' + colours.end)
        for folio in sub.values:
            expansion_portfolio_response(folio)
    print ('\n')

def instrument_response(response, identifier='ClientInternal'):
    print(colours.FAIL + colours.bold + 'Instruments Successfully Upserted: ' + colours.end)
  
    values = []
    for instrument_name, instrument in response.values.items():
        nested_values = []
        nested_values.append(instrument_name)
        nested_values.append(instrument.identifiers[identifier])
        nested_values.append(instrument.lusid_instrument_id)
        values.append(nested_values)

    return pd.DataFrame(values, columns = ["Instrument",'{} ID'.format(identifier),"LUSID Instrument ID"])

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

def cancel_adjust_holdings_response(response, scope, portfolio_name):

    print (colours.bold + 'Holdings Adjustment Cancelled for Portfolio' + colours.end)
    print (colours.bold + 'Scope: ' + colours.end + scope)
    print (colours.bold + 'Code: ' + colours.end + portfolio_name)
    print (colours.bold + 'Adjusted Holdings Effective From: ' + colours.end + str(response.effective_from))
    print (colours.bold + 'Adjusted Holdings Created On: ' + colours.end + str(response.as_at) + '\n')    
    
def list_holdings_adjustments_response(response, scope, portfolio_name):
    print (colours.bold + "Holding Adjustments for Portfolio:" + colours.end)
    print (colours.bold + 'Scope: ' + colours.end + scope)
    print (colours.bold + 'Code: ' + colours.end + portfolio_name + '\n')
    
    values = []
    for value in response.values:
        nested_values = []
        nested_values.append(value.unmatched_holding_method)
        nested_values.append(value.version.effective_from)
        nested_values.append(value.version.as_at_date)
        values.append(nested_values)

    columns = ["Unmatched Holding Method","Adjustment Effective From","Adjustment Created On"]
    return pd.DataFrame(values, columns = columns)
    
def get_holdings_adjustment_response(response, scope, portfolio_name):
    print(colours.FAIL + colours.bold + "Holdings Adjustment in Portfolio: " + colours.end)
    print (colours.bold + 'Scope: ' + colours.end + scope)
    print (colours.bold + 'Code: ' + colours.end + portfolio_name + '\n')
    
    identifiers = []
    values = []   
    for holding in response.adjustments:
        for key, value in holding.instrument_identifiers.items():
            if key not in identifiers:
                identifiers.append(key)           

    for holding in response.adjustments:
        nested_values = []
        for identifier in identifiers:
            for key, value in holding.instrument_identifiers.items():
                if key == identifier:
                    nested_values.append(value)
                else:
                    nested_values.append("-")
        nested_values.append(holding.tax_lots[0].units)
        nested_values.append(holding.tax_lots[0].cost.amount)
        nested_values.append(holding.tax_lots[0].cost.currency)
        nested_values.append(response.version.effective_from)
        nested_values.append(response.version.as_at_date)
        values.append(nested_values)

    columns = identifiers
    columns.extend(["Units", "Cost", "Currency", "Adjustment Effective From", "Adjustment Created On"])

    return pd.DataFrame(values, columns = columns)
    
def output_transactions(response, scope, code, property_keys=[]):
    print (colours.FAIL + colours.bold + 'Output Transactions for Portfolio' + colours.end)
    print (colours.bold + 'Scope: ' + colours.end + scope)
    print (colours.bold + 'Code: ' + colours.end + code + '\n')
    
    identifiers = []
    for transaction in response.values:
        for key, value in transaction.properties.items():
            if len(property_keys) > 0:
                if key not in identifiers and key in property_keys:
                    identifiers.append(key)
            else:
                if key not in identifiers :
                    identifiers.append(key)

    values = []
    for transaction in response.values:
            nested_values = []
            nested_values.append(transaction.transaction_id)
            nested_values.append(transaction.type)
            for identifier in identifiers:
                for key, value in transaction.properties.items():
                    if key == identifier:
                        nested_values.append(value.value.label_value)
            nested_values.append(transaction.units)
            nested_values.append(transaction.transaction_price.price)
            nested_values.append(transaction.transaction_currency)
            nested_values.append(transaction.transaction_date)
            nested_values.append(transaction.settlement_date)
            if len(transaction.realised_gain_loss) > 0:
                nested_values.append(
                    sum(
                        transaction.realised_gain_loss[i].realised_trade_ccy.amount for i in range(len(transaction.realised_gain_loss))
                    )
                )
            else:
                nested_values.append(np.NaN)
            values.append(nested_values)
    columns = ["Transaction ID", "Transaction Type"]
    columns.extend(identifiers)
    columns.extend(["Units", "Price", "Currency", "Transaction Date", "Settlement Date"])
    columns.extend(["Realised Gain Loss"])

    df = pd.DataFrame(values, columns = columns)
    df = df.sort_values("Realised Gain Loss")
    df = df.append(df.sum(numeric_only=True), ignore_index=True)
    return df

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
    
    identifiers = []
    for transaction in response.values:
        for key, value in transaction.properties.items():
            if key not in identifiers:
                identifiers.append(key)

    values = []
    for holding in response.values:
        if holding.transaction is not None:
            nested_values = []
            for identifier in identifiers:
                for key, value in holding.properties.items():
                    if key == identifier:
                        nested_values.append(value.value.label_value)
            nested_values.append(holding.units)
            nested_values.append(holding.cost.amount)
            nested_values.append(holding.cost.currency)
            nested_values.append(holding.transaction.transaction_id)
            nested_values.append(holding.transaction.settlement_date)
            values.append(nested_values)
        else:
            nested_values = []
            for identifier in identifiers:
                for key, value in holding.properties.items():
                    if key == identifier:
                        nested_values.append(value.value.label_value)
            nested_values.append(holding.units)
            nested_values.append(holding.cost.amount)
            nested_values.append(holding.cost.currency)
            nested_values.append("-")
            nested_values.append("-")
            values.append(nested_values)
    columns = identifiers
    columns.extend(["Units","Cost","Currency","Unsettled Transaction Id","Settlement Date"])


    return pd.DataFrame(values, columns = columns)

def get_transactions_response(response, scope, code, property_keys=[]):
    print (colours.FAIL + colours.bold + 'Transactions Retrieved from Portfolio' + colours.end)
    print (colours.bold + 'Scope: ' + colours.end, scope)
    print (colours.bold + 'Code: ' + colours.end, code, '\n')
    
    identifiers = []
    for transaction in response.values:
        for key, value in transaction.properties.items():
            if len(property_keys) > 0:
                if key not in identifiers and key in property_keys:
                    identifiers.append(key)
            else:
                if key not in identifiers :
                    identifiers.append(key)

    values = []
    for transaction in response.values:
            nested_values = []
            nested_values.append(transaction.transaction_id)
            nested_values.append(transaction.type)
            for identifier in identifiers:
                for key, value in transaction.properties.items():
                    if key == identifier:
                        nested_values.append(value.value.label_value)
            nested_values.append(transaction.units)
            nested_values.append(transaction.transaction_price.price)
            nested_values.append(transaction.transaction_currency)
            nested_values.append(transaction.transaction_date)
            values.append(nested_values)
    columns = ["Transaction ID", "Transaction Type"]
    columns.extend(identifiers)
    columns.extend(["Units", "Price", "Currency", "Transaction Date"])

    return pd.DataFrame(values, columns = columns)
    
def portfolio_properties_response(response):
    print (colours.bold + 'Properties Sucessfully Updated for Portfolio' + colours.end)
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

def aggregation_responses_generic_df(responses):
    
    dfs = []
    
    for response in responses:
        
        aggregation_currency = response.aggregation_currency
        data_response_rows = []
        for aggregation in response.data:
            data_row = {}
            data_row.update(aggregation)
            data_row['currency'] = aggregation_currency
            data_response_rows.append(data_row)
        
        df = pd.DataFrame(data_response_rows)
        dfs.append(df)
    
    pd.options.display.float_format = '{:,.2f}'.format
    df_concat = pd.concat(dfs, ignore_index=True)
    return df_concat


def aggregation_response_households_generic_df(response, index_key, name):
    df = pd.DataFrame(response.data)
    # Replace <Unknown> as the name for cash instruments with Cash
    if "Instrument/default/Name" in df.columns:
        df["Instrument/default/Name"] = df["Instrument/default/Name"].apply(lambda x: "Cash" if x == '<Unknown>' else x)
    df.sort_values(index_key, inplace=True, ascending=True)
    df = df.append(df.sum(numeric_only=True), ignore_index=True)
    df.at[len(df)-1, index_key] = "TOTAL"
    df.name = name
    df.set_index(index_key, drop=True, inplace=True)
    df.round(2)
    pd.options.display.float_format = '{:,}'.format
    return df

def transaction_type_response(txnResponse, filters=[]):
    i = 0
    j = 0
    for mapping in txnResponse.transaction_configs:
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
                for key, value in movement.properties.items():
                    print (f"{colours.bold}Properties: {colours.end}key: {value}\n")
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
        if identifier.is_unique_identifier_type == unique:
            print(colours.bold + '    Identifier Name : ' + colours.end + identifier.identifier_type)
            print(colours.bold + '    Is Unique Identifier : ' + colours.end + str(identifier.is_unique_identifier_type))
            print(colours.bold + '    Identifier Property Key Value : ' + colours.end + identifier.property_key)
            print ('\n')

def corporate_action_response(response):
    print (colours.bold + 'Corporate Actions Source Successfully Created' + colours.end)
    print (colours.bold + 'Scope: ' + colours.end + response.id.scope)
    print (colours.bold + 'Code: ' + colours.end + response.id.code)

def corporate_actions_added_response(response):
    for action_id, action in response.values.items():
        print (colours.bold + 'Corporate Action Successfully Upserted' + colours.end)
        print (colours.bold + 'Code: ' + colours.end + action.corporate_action_code)
        print (colours.bold + 'Announcement Date: ' + colours.end + str(action.announcement_date))
        print (colours.bold + 'Ex Date: ' + colours.end + str(action.ex_date) + '\n')
        
def upsert_quotes_response(response):
    response_df_data = []
    
    for quote_correlation_id, quote in response.values.items():
        row_data = {}
        row_data.update(vars(quote))
        del row_data['_metric_value']
        del row_data['_quote_id']
        row_data.update(vars(quote.quote_id.quote_series_id))
        row_data.update(vars(quote.metric_value))  
        row_data['status'] = 'Success'
        response_df_data.append(row_data)


    response_df = pd.DataFrame.from_dict(response_df_data)

    return response_df


def get_holdings_df(response):
    rows = []
    nested_fields = ['cost', 'cost_portfolio_ccy', 'properties', 'sub_holding_keys']

    for holding in response.values:
        current_row = {}
        current_row.update(vars(holding))
        for field in nested_fields:
            del current_row["_" + field]
        current_row['cost.amount'] = holding.cost.amount
        current_row['cost.currency'] = holding.cost.currency
        current_row['cost_portfolio_ccy.amount'] = holding.cost.amount

        for sub_holding_key_key, sub_holding_key in holding.sub_holding_keys.items():

            if sub_holding_key.value.label_value is None:
                value = sub_holding_key.value.metric_value.value
            else:
                value = sub_holding_key.value.label_value

            current_row[sub_holding_key_key] = value

        for _property_key, _property in holding.properties.items():

            if _property.value.label_value is None:
                value = _property.value.metric_value.value
            else:
                value = _property.value.label_value

            current_row[_property_key] = value

        rows.append(current_row)

    df = pd.DataFrame(rows)
    return df
        
def cut_label_response(response):
    print(colours.FAIL + colours.bold + "Cut Label Created" + colours.end)
    print(colours.bold + "Display Name: " + colours.end + response.display_name)
    print(colours.bold + "Code: " + colours.end + response.code)
    if response.cut_local_time.minutes and response.cut_local_time.hours < 10:
        print(colours.bold + "Local Time: " + colours.end + "0" + str(response.cut_local_time.hours) + ":0" + 
              str(response.cut_local_time.minutes))
    elif response.cut_local_time.minutes < 10:
        print(colours.bold + "Local Time: " + colours.end + str(response.cut_local_time.hours) + ":0" + 
              str(response.cut_local_time.minutes))
    elif response.cut_local_time.hours < 10:
        print(colours.bold + "Local Time: " + colours.end + "0" + str(response.cut_local_time.hours) + ":" + 
              str(response.cut_local_time.minutes))
    else:
        print(colours.bold + "Local Time: " + colours.end + str(response.cut_local_time.hours) + ":" + 
              str(response.cut_local_time.minutes))
    print(colours.bold + "Timezone: " + colours.end + response.time_zone)
    print(colours.bold + "Description: " + colours.end + response.description + "\n")
    
def get_cut_label(response):
    print (colours.FAIL + colours.bold + "Cut Label Details:" + colours.end)
    print(colours.bold + "Display Name: " + colours.end + response.display_name)
    print(colours.bold + "Code: " + colours.end + response.code)
    if response.cut_local_time.minutes and response.cut_local_time.hours < 10:
        print(colours.bold + "Local Time: " + colours.end + "0" + str(response.cut_local_time.hours) + ":0" + 
              str(response.cut_local_time.minutes))
    elif response.cut_local_time.minutes < 10:
        print(colours.bold + "Local Time: " + colours.end + str(response.cut_local_time.hours) + ":0" + 
              str(response.cut_local_time.minutes))
    elif response.cut_local_time.hours < 10:
        print(colours.bold + "Local Time: " + colours.end + "0" + str(response.cut_local_time.hours) + ":" + 
              str(response.cut_local_time.minutes))
    else:
        print(colours.bold + "Local Time: " + colours.end + str(response.cut_local_time.hours) + ":" + 
              str(response.cut_local_time.minutes))
    print(colours.bold + "Timezone: " + colours.end + response.time_zone)
    print(colours.bold + "Description: " + colours.end + response.description + "\n")
        
def list_cut_label_details(response):
    print(colours.FAIL+ colours.bold + "Existing Cut Labels:" + colours.end)
    
    values = []
    for body in response.values:
        nested_values = []
        if body.cut_local_time.minutes < 10 and body.cut_local_time.hours < 10:
                my_date = "0" + str(body.cut_local_time.hours) + ":0" + str(body.cut_local_time.minutes)
        elif body.cut_local_time.minutes < 10 :
                my_date = str(body.cut_local_time.hours) + ":0" + str(body.cut_local_time.minutes)
        elif body.cut_local_time.hours < 10:
                my_date = "0" + str(body.cut_local_time.hours) + ":" + str(body.cut_local_time.minutes)
        else:
                my_date = str(body.cut_local_time.hours) + ":" + str(body.cut_local_time.minutes)
        nested_values.append(body.display_name)
        nested_values.append(body.code)
        nested_values.append(my_date)
        nested_values.append(body.time_zone)
        nested_values.append(body.description)
        values.append(nested_values)

    return pd.DataFrame(values, columns = ["Display Name", "Code", "Local Time", "Timezone", "Description"])
        
def list_cut_labels(response):
    print(colours.FAIL+ colours.bold + "Existing Cut Labels:" + colours.end)
    for body in response.values:
        print(body.display_name)
        
def update_cut_label(response):
    print(colours.FAIL + colours.bold + "Updated Cut Label:" + colours.end)
    print(colours.bold + "Display Name: " + colours.end + response.display_name)
    print(colours.bold + "Code: " + colours.end + response.code)
    if response.cut_local_time.minutes and response.cut_local_time.hours < 10:
        print(colours.bold + "Local Time: " + colours.end + "0" + str(response.cut_local_time.hours) + ":0" + 
              str(response.cut_local_time.minutes))
    elif response.cut_local_time.minutes < 10:
        print(colours.bold + "Local Time: " + colours.end + str(response.cut_local_time.hours) + ":0" + 
              str(response.cut_local_time.minutes))
    elif response.cut_local_time.hours < 10:
        print(colours.bold + "Local Time: " + colours.end + "0" + str(response.cut_local_time.hours) + ":" + 
              str(response.cut_local_time.minutes))
    else:
        print(colours.bold + "Local Time: " + colours.end + str(response.cut_local_time.hours) + ":" + 
              str(response.cut_local_time.minutes))
    print(colours.bold + "Timezone: " + colours.end + response.time_zone)
    print(colours.bold + "Description: " + colours.end + response.description + "\n")

def aggregation_response_generic_df(response, index_key, name):
    df = pd.DataFrame(response.data)
    # Replace <Unknown> as the name for cash instruments with Cash
    if "Instrument/default/Name" in df.columns:
        df["Instrument/default/Name"] = df["Instrument/default/Name"].apply(lambda x: "Cash" if x == '<Unknown>' else x)
    df.sort_values(index_key, inplace=True, ascending=True)
    df = df.append(df.sum(numeric_only=True), ignore_index=True)
    df.at[len(df)-1, index_key] = "TOTAL"
    df.columns.name = name
    df.set_index(index_key, drop=True, inplace=True)
    df = df.round(2)
    pd.options.display.float_format = '{:,}'.format
    return df


def corporate_action_request_details(ca):
    print(colours.bold + 'CA Code and Type: ' + colours.end + str(ca['code']) + str(ca['action_description']))
    print(colours.bold + 'Announcement Date : ' + colours.end + str(ca['announcement_date']))
    print(colours.bold + 'Ex Date : ' + colours.end + str(ca['ex_date']))
    print(colours.bold + 'Record Date : ' + colours.end + str(ca['record_date']))
    print(colours.bold + 'Payment Date : ' + colours.end + str(ca['payment_date']))
    print(colours.bold + 'input instrument : ' + colours.end + str(ca['input_instrument_luid']))
    print(colours.bold + 'Units in : ' + colours.end + str(ca['input_units_factor']) + colours.bold + ' Cost in : ' + colours.end + str(ca['input_cost_factor']))
    print(colours.bold + 'output instrument : ' + colours.end + str(ca['output_instrument_luid']))
    print(colours.bold + 'output internal : ' + colours.end + str(ca['output_instrument_internal']))
    print(colours.bold + 'Units out : ' + colours.end + str(ca['output_units_factor']) + colours.bold + ' Cost out : ' + colours.end + str(ca['output_cost_factor']))
    print('')

def batch_upsert_corporate_actions_response(response):
    if response.failed:
        print(colours.bold + colours.FAIL + "One or more corporate actions failed to upsert"+ colours.end )
    for value in response.values:
        print(colours.bold + colours.OKBLUE + 'Corporate Action Id : ' + colours.end + value)
        ca = response.values[value]
        print(colours.bold + 'Announcement Date : ' + colours.end + str(ca.announcement_date))
        print(colours.bold + 'Ex Date : ' + colours.end + str(ca.ex_date))
        print(colours.bold + 'Payment Date : ' + colours.end + str(ca.payment_date))
        print(colours.bold + 'Record Date : ' + colours.end + str(ca.record_date))
        print(colours.bold + colours.OKBLUE + '   Transitions : ' + colours.end)
        for t in ca.transitions:
            print(colours.bold + 'Input LUID: ' + colours.end + t.input_transition.instrument_uid +
                  colours.bold + ' with Cost factor: ' + colours.end + str(t.input_transition.cost_factor),
                  colours.bold + ' and Unit Factor: ' + colours.end + str(t.input_transition.units_factor))
            for o in t.output_transitions:
                print(colours.bold + 'Output LUID: ' + colours.end + o.instrument_uid,
                      colours.bold + ' with Cost Factor: ' + colours.end + str(o.cost_factor),
                      colours.bold + ' and Unit Factor: ' + colours.end + str(o.units_factor))
        print('')

def get_corporate_actions_response(scope, code, response):
    for ca in response.values:
        print(colours.bold + colours.OKBLUE + 'Corporate Action Id : ' + colours.end + ca.corporate_action_code)
        print(colours.bold + 'Source Id : ' + colours.end)
        print(colours.bold + '    Scope : ' + colours.end + scope)
        print(colours.bold + '    Code : ' + colours.end + code)
        print(colours.bold + 'Announcement Date : ' + colours.end + str(ca.announcement_date))
        print(colours.bold + 'Ex Date : ' + colours.end + str(ca.ex_date))
        print(colours.bold + 'Payment Date : ' + colours.end + str(ca.payment_date))
        print(colours.bold + 'Record Date : ' + colours.end + str(ca.record_date))
        print(colours.bold + colours.OKBLUE + '   Transitions : ' + colours.end)
        for t in ca.transitions:
            print(colours.bold + 'Input LUID: ' + colours.end + t.input_transition.instrument_uid +
                  colours.bold + ' with Cost factor: ' + colours.end + str(t.input_transition.cost_factor),
                  colours.bold + ' and Unit Factor: ' + colours.end + str(t.input_transition.units_factor))
            for o in t.output_transitions:
                print(colours.bold + 'Output LUID: ' + colours.end + o.instrument_uid,
                      colours.bold + ' with Cost Factor: ' + colours.end + str(o.cost_factor),
                      colours.bold + ' and Unit Factor: ' + colours.end + str(o.units_factor))
        print('')


def sub_holdings(response):
    rows = []

    for sub_holding in response.values:

        row = {}

        row['Lusid Unique Instrument Id'] = sub_holding.instrument_uid
        row['Units'] = sub_holding.units

        for sub_holding_key, sub_holding_value in sub_holding.sub_holding_keys.items():
            row["/".join(sub_holding_key.split('/')[::2])] = sub_holding_value.value.label_value

        for transaction_property_key, transaction_property_value in sub_holding.properties.items():
            row["_".join(transaction_property_key.split('/')[::2])] = transaction_property_value.value.label_value

        row['Total Cost'] = sub_holding.cost.amount
        row['Currency'] = sub_holding.cost.currency

        rows.append(row)

    dataframe = pd.DataFrame(rows)

    if 'InvestorId' in dataframe.columns:
        dataframe = dataframe.sort_values(['InvestorId', 'SubscriptionType'], ascending=False)
    return dataframe

def add_transaction_property(response):
    print(colours.bold + "Added transaction properties asAt: " + colours.end + str(response.version.as_at_date))