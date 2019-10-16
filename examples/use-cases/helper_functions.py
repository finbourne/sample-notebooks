import lusid.models as models
import lusid_sample_data as import_data

# Import Libraries
import pprint
from datetime import datetime, timedelta, time
import pytz
import printer as prettyprint
import pandas as pd

def delete_all_current_instruments(client):
    response = client.instruments.list_instruments()
    if len(response.values) == 0:
        print('No previous existing instruments')
        return None
    for ii in range(len(response.values)):
        identifierTypes=[]
        identifier=[]
        IDs = response.values[ii].identifiers.keys()
        for key in IDs:
            identifierTypes.append(key)
            identifier.append(response.values[ii].identifiers[key])
        print(identifierTypes)
        print(identifier)
        deleted = client.instruments.delete_instrument(identifierTypes[0], identifier[0])
        print(deleted)

def delete_all_current_portfolios(client):
    # delete ALL existing scopes
    response = client.portfolios.list_portfolios()
    if len(response.values) == 0:
        print('No previous existing portfolios')
        return None
    for ii in range(len(response.values)):
        code = response.values[ii].id.code
        scope = response.values[ii].id.scope 
        print('Deleting:')
        print('Code: {} \nScope: {}'.format(code, scope))
        client.portfolios.delete_portfolio(scope, code)
        print('All scopes deleted')

def create_analyst_scope():
    # Fetch our scopes
    scope_id = import_data.create_scope_id()
    analyst_scope_code = 'analyst-paper-{}'.format(scope_id)
    prettyprint.heading('Analyst Scope Code', analyst_scope_code)
    return analyst_scope_code

def batch_upsert(instrument_universe, client):
    # Initialise our batch upsert request
    batch_upsert_request = {}
    # Iterate over our instrument universe
    for row, instrument in instrument_universe.iterrows():

        # Set our identifier columns
        identifier_columns = [
                ('isin', 'Isin'), 
                ('figi', 'Figi'), 
                ('ticker', 'Ticker'),
                ('sedol', 'Sedol'),
                ('client_internal', 'ClientInternal')
        ]

        # Create our identifiers
        identifiers = {}
        for identifier in identifier_columns:
            identifiers[identifier[1]] = models.InstrumentIdValue(
                value=instrument[identifier[0]])

        # Add the instrument to our batch request using the FIGI as the main unique identifier
        batch_upsert_request[instrument['instrument_name']] = models.InstrumentDefinition(
            name=instrument['instrument_name'],
            identifiers=identifiers)

    # Call LUSID to upsert our batch
    instrument_response = client.instruments.upsert_instruments(
        instruments=batch_upsert_request)

    # Pretty print the response from LUSID
    prettyprint.instrument_response(instrument_response, identifier='Figi')
    return batch_upsert_request
        
        
def request_transaction_portfolio_creation(portfolio_code, portfolio_creation_date, analyst_scope_code, description, client):
    
        # Create the request to add our portfolio
    transaction_portfolio_request = models.CreateTransactionPortfolioRequest(
        display_name=portfolio_code,
        code=portfolio_code,
        base_currency='GBP',
        description = 'Paper transaction portfolio',
        created=portfolio_creation_date)

    # Call LUSID to create our portfolio
    portfolio_response = client.transaction_portfolios.create_portfolio(
        scope=analyst_scope_code,
        transaction_portfolio=transaction_portfolio_request)

    # Pretty print the response from LUSID
    prettyprint.portfolio_response(portfolio_response)
    

def request_reference_portfolio_creation(reference_portfolio_code, portfolio_creation_date, analyst_scope_code, client):
    
    # Create the request to add our portfolio
    reference_portfolio_request = models.CreateReferencePortfolioRequest(
        display_name=reference_portfolio_code,
        code=reference_portfolio_code,
        description='Paper reference portfolio',
        created=portfolio_creation_date)

    # Call LUSID to create our reference portfolio
    portfolio_response = client.reference_portfolios.create_reference_portfolio(
        scope=analyst_scope_code,
        reference_portfolio=reference_portfolio_request)

    # Pretty print our response from LUSID
    prettyprint.portfolio_response(portfolio_response)


def populate_with_cash(holdings_effective_date, initial_cash_balance, analyst_scope_code, transaction_portfolio_code, client):
    # Create a holding adjustment to set our initial cash balance
    holding_adjustment = [
        models.AdjustHoldingRequest(
            instrument_identifiers={
                'Instrument/default/Currency': 'GBP'},
            tax_lots=[
                models.TargetTaxLotRequest(
                    units=initial_cash_balance,
                    cost=models.CurrencyAndAmount(
                        amount=initial_cash_balance,
                        currency='GBP'),
                    portfolio_cost=initial_cash_balance,
                    price=1)
                    ]
        )
    ]

    # Call LUSID to set our initial cash balance
    set_holdings_response = client.transaction_portfolios.set_holdings(
        scope=analyst_scope_code,
        code=transaction_portfolio_code,
        effective_at=holdings_effective_date,
        holding_adjustments=holding_adjustment)

    # Pretty print our response from LUSID
    prettyprint.set_holdings_response(
        set_holdings_response, 
        analyst_scope_code, 
        transaction_portfolio_code)

def upsert_constituents(instrument_market_cap, holdings_effective_date, analyst_scope_code, reference_portfolio_code, client):
    # Initialise a list to hold our constituents
    constituents = []
    # Work out the total market capitalisation of the entire index
    total = instrument_market_cap['marketcap'].sum()

    # Iterate over instrument unvierse to add each constituent to our list
    for row in instrument_market_cap.iterrows():
        # Collect our instrument
        instrument = row[1]
        # Calculate our constituents weight based on market cap and add it to our list
        constituents.append(models.ReferencePortfolioConstituentRequest(
            instrument_identifiers={
                'Instrument/default/Figi': instrument['figi']},
            weight=instrument['marketcap']/total,
            currency=instrument['currency']))

    # Create our request to add our constituents
    constituents_request = models.UpsertReferencePortfolioConstituentsRequest(
        effective_from=holdings_effective_date,
        weight_type="Periodical",
        period_type="Quarterly",
        period_count=4,
        constituents=constituents)

    # Call LUSID to upsert our constituents into our reference portfolio
    response = client.reference_portfolios.upsert_reference_portfolio_constituents(
        scope=analyst_scope_code,
        code=reference_portfolio_code,
        constituents=constituents_request)

    print ('Constituents Upserted')
def request_define_property(domain, scope, code, display_name, client):
    # Create a request to define our strategy property
    property_request = models.CreatePropertyDefinitionRequest(
        domain='Transaction',
        scope=scope,
        code='strategy',
        value_required=False,
        display_name='strategy',
        data_type_id=models.ResourceId(
            scope='system',
            code='string')
    )

    # Call LUSID to create our new property
    property_response = client.property_definitions.create_property_definition(
        definition=property_request)

    # Grab the key off the response to use when referencing this property in other LUSID calls
    strategy_property_key = property_response.key

    # Pretty print our strategy property key
    prettyprint.heading('Strategy Property Key: ', strategy_property_key)
    return strategy_property_key
    
def upsert_trades(analyst_transactions, strategy_property_key, scope, portfolio_code, client):
    # Initialise a list to hold our transactions
    batch_transaction_requests = []

    # Iterate over the transactions for each portfolio
    for index, transaction in analyst_transactions.iterrows():

        if 'Cash' in transaction['instrument_name']:
            identifier_key = 'Instrument/default/Currency'
        else:
            identifier_key = 'Instrument/default/Figi'

        batch_transaction_requests.append(
            models.TransactionRequest(
                transaction_id=transaction['transaction_id'],
                type=transaction['type'],
                instrument_identifiers={
                    identifier_key: transaction['instrument_uid']},
                transaction_date=transaction['transaction_date'],
                settlement_date=transaction['settlement_date'],
                units=transaction['units'],
                transaction_price=models.TransactionPrice(
                    price=transaction['transaction_price'],
                    type='Price'),
                total_consideration=models.CurrencyAndAmount(
                    amount=transaction['total_cost'],
                    currency=transaction['transaction_currency']),
                source='Client',
                transaction_currency=transaction['transaction_currency'],
                properties={
                    strategy_property_key:
                        models.PerpetualProperty(
                            key=strategy_property_key,
                            value=models.PropertyValue(label_value=transaction['strategy']) 
                        )
                }
            )
        )

    # Call LUSID to upsert our transactions
    transaction_response = client.transaction_portfolios.upsert_transactions(
        scope=scope,
        code=portfolio_code,
        transactions=batch_transaction_requests)

    # Pretty print the response from LUSID
    prettyprint.transactions_response(
        transaction_response,
        scope, 
        portfolio_code)

def get_figi_LUID(instrument, client):
    luid = client.instruments.get_instrument(
        identifier_type='Figi',
        identifier=instrument['figi']).lusid_instrument_id
    return luid

def create_instrument_analytics(analytics_effective_date, today, analytics_store_dates, instrument_prices, analyst_scope_code, client):
    # Create prices via instrument, analytic
    instrument_analytics_inception = []
    instrument_analytics_today = []

    # Create dummy prices of 1 for all instruments except cash
    for row in instrument_prices.iterrows():

        instrument = row[1]

        if 'Cash' in instrument['instrument_name']:
            continue

        # Get our Lusid Instrument Id
        luid = client.instruments.get_instrument(
            identifier_type='Figi',
            identifier=instrument['figi']).lusid_instrument_id

        instrument_analytics_inception.append(models.InstrumentAnalytic(
            instrument_uid=luid,
            value=instrument['price_original']))

        instrument_analytics_today.append(models.InstrumentAnalytic(
            instrument_uid=luid,
            value=instrument['price_current']))

    instrument_analytics = [instrument_analytics_inception, instrument_analytics_today]

    for date, instrument_analytic_set in zip(analytics_store_dates, instrument_analytics):

        # Create analytics store request
        analytics_store_request = models.CreateAnalyticStoreRequest(
            scope=analyst_scope_code,
            date=date.isoformat())

        # Call LUSID to create our analytics store
        client.analytics_stores.create_analytic_store(
            request=analytics_store_request)

        # Call LUSID to set up our newly created analytics store with our prices
        client.analytics_stores.set_analytics(
            scope=analyst_scope_code,
            year=date.year,
            month=date.month,
            day=date.day,
            data=instrument_analytic_set)

    print ('Analytics Set')

def create_aggregation_request(analyst_scope_code, today, transaction_portfolio_code, client):
    # Create our aggregation request
    aggregation_request = models.AggregationRequest(
        recipe_id=models.ResourceId(
            scope=analyst_scope_code,
            code='default'),
        effective_at=today,
        metrics=[
            models.AggregateSpec(
                key='Holding/default/SubHoldingKey',
                op='Value'),
            models.AggregateSpec(
                key='Holding/default/Units',
                op='Sum'),
            models.AggregateSpec(
                key='Holding/default/Cost',
                op='Sum'),
            models.AggregateSpec(
                key='Holding/default/PV',
                op='Sum'),
           models.AggregateSpec(
               key='Holding/default/Price',
               op='Sum') 
        ],
    group_by=[
        'Holding/default/SubHoldingKey'
    ])
    
    return aggregation_request
    
    # Call LUSID to aggregate across all of our portfolios
    aggregated_portfolio = client.aggregation.get_aggregation_by_portfolio(
        scope=analyst_scope_code,
        code=transaction_portfolio_code,
        request=aggregation_request)

    prettyprint.aggregation_response_paper(aggregated_portfolio)

def setup_index(analyst_scope_code, reference_portfolio_code, instrument_prices, client):
    # Set an arbitary index level to start our index with
    index_level = 1000
    # Call LUSID - get the constituents of our index from our reference portfolio
    constituents = client.reference_portfolios.get_reference_portfolio_constituents(
        scope=analyst_scope_code,
        code=reference_portfolio_code,
        effective_at=datetime.now(pytz.UTC))
    # Initialise our list to hold the adjustments we need to make to our index to set it up
    index_setup = []
    # Get our weights from the constituents into a better format to work with
    weights = {constituent.instrument_uid:constituent.weight for constituent in constituents.constituents}

    # Iterate over our pricing analytics
    for index, instrument in instrument_prices.iterrows():

        # Get our Lusid Instrument ID
        Luid = client.instruments.get_instrument(
            identifier_type='Figi',
            identifier=instrument['figi']).lusid_instrument_id
        # Get the initial price for each constituent of the index from our analytics store
        inception_price = instrument['price_original']
        # Work out how much of the index this constituent should make up using its w
        index_cost = weights[Luid] * index_level
        # Work out how many units we should therefore buy
        index_units = index_cost / inception_price
        # Create our request for this instrument 
        index_setup.append(
            models.AdjustHoldingRequest(
                instrument_identifiers={
                    'Instrument/default/Figi': instrument['figi']},
                tax_lots=[
                    models.TargetTaxLotRequest(
                    units=index_units,
                    cost=models.CurrencyAndAmount(
                        amount=index_cost,
                        currency='GBP'),
                    portfolio_cost=index_cost,
                    price=inception_price)
                ]
            )
        )
    return index_setup

def create_analytics_aggregation_request(analyst_scope_code, index_portfolio_code, today, client):
    aggregation_request = models.AggregationRequest(
        recipe_id=models.ResourceId(
            scope=analyst_scope_code,
            code='default'),
            effective_at=today,
            metrics=[
                models.AggregateSpec(
                    key='Holding/default/PV',
                    op='Sum'),
                models.AggregateSpec(
                    key='Holding/default/Cost',
                    op='Sum')
            ],
    group_by=['Portfolio/default/Name'])
    
    # Call LUSID to aggregate across all of our portfolios
    aggregated_portfolio = client.aggregation.get_aggregation_by_portfolio(
        scope=analyst_scope_code,
        code=index_portfolio_code,
        request=aggregation_request
    )

    # Pretty print the response from LUSID
    prettyprint.aggregation_response_index(aggregated_portfolio)

