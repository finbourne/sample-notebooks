import lusid
import lusid.models as models
import lusid_sample_data as import_data

# Import Libraries
import pprint
from datetime import datetime, timedelta, time
import pytz
import printer as prettyprint
import pandas as pd

def delete_all_current_instruments(api_factory):
    response = api_factory.build(lusid.api.InstrumentsApi).list_instruments()
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
        deleted = api_factory.build(lusid.api.InstrumentsApi).delete_instrument(identifierTypes[0], identifier[0])
        print(deleted)

def delete_all_current_portfolios(api_factory):
    # delete ALL existing scopes
    response = api_factory.build(lusid.api.PortfoliosApi).list_portfolios()
    if len(response.values) == 0:
        print('No previous existing portfolios')
        return None
    for ii in range(len(response.values)):
        code = response.values[ii].id.code
        scope = response.values[ii].id.scope 
        print('Deleting:')
        print('Code: {} \nScope: {}'.format(code, scope))
        api_factory.build(lusid.api.PortfoliosApi).delete_portfolio(scope, code)
        print('All scopes deleted')

def create_analyst_scope():
    # Fetch our scopes
    scope_id = import_data.create_scope_id()
    analyst_scope_code = 'analyst-paper-{}'.format(scope_id)
    prettyprint.heading('Analyst Scope Code', analyst_scope_code)
    return analyst_scope_code

def batch_upsert(instrument_universe, api_factory):
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
    instrument_response = api_factory.build(lusid.api.InstrumentsApi).upsert_instruments(request_body=batch_upsert_request)

    # Pretty print the response from LUSID
    prettyprint.instrument_response(instrument_response, identifier='Figi')
    return batch_upsert_request
        
        
def request_transaction_portfolio_creation(portfolio_code, portfolio_creation_date, analyst_scope_code, description, api_factory):
    
        # Create the request to add our portfolio
    transaction_portfolio_request = models.CreateTransactionPortfolioRequest(
        display_name=portfolio_code,
        code=portfolio_code,
        base_currency='GBP',
        description = 'Paper transaction portfolio',
        created=portfolio_creation_date)

    # Call LUSID to create our portfolio
    portfolio_response = api_factory.build(lusid.api.TransactionPortfoliosApi).create_portfolio(
        scope=analyst_scope_code,
        create_transaction_portfolio_request=transaction_portfolio_request)

    # Pretty print the response from LUSID
    prettyprint.portfolio_response(portfolio_response)
    

def request_reference_portfolio_creation(reference_portfolio_code, portfolio_creation_date, analyst_scope_code, api_factory):
    
    # Create the request to add our portfolio
    reference_portfolio_request = models.CreateReferencePortfolioRequest(
        display_name=reference_portfolio_code,
        code=reference_portfolio_code,
        description='Paper reference portfolio',
        created=portfolio_creation_date)

    # Call LUSID to create our reference portfolio
    portfolio_response = api_factory.build(lusid.api.ReferencePortfolioApi).create_reference_portfolio(
        scope=analyst_scope_code,
        create_reference_portfolio_request=reference_portfolio_request)

    # Pretty print our response from LUSID
    prettyprint.portfolio_response(portfolio_response)


def populate_with_cash(holdings_effective_date, initial_cash_balance, analyst_scope_code, transaction_portfolio_code, api_factory):
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
    set_holdings_response = api_factory.build(lusid.api.TransactionPortfoliosApi).set_holdings(
        scope=analyst_scope_code,
        code=transaction_portfolio_code,
        effective_at=holdings_effective_date,
        adjust_holding_request=holding_adjustment)

    # Pretty print our response from LUSID
    prettyprint.set_holdings_response(
        set_holdings_response, 
        analyst_scope_code, 
        transaction_portfolio_code)

def upsert_constituents(instrument_market_cap, holdings_effective_date, analyst_scope_code, reference_portfolio_code, api_factory):
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
    response = api_factory.build(lusid.api.ReferencePortfolioApi).upsert_reference_portfolio_constituents(
        scope=analyst_scope_code,
        code=reference_portfolio_code,
        upsert_reference_portfolio_constituents_request=constituents_request)

    print ('Constituents Upserted')
def request_define_property(domain, scope, code, display_name, api_factory):
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
    property_response = api_factory.build(lusid.api.PropertyDefinitionsApi).create_property_definition(
        create_property_definition_request=property_request)

    # Grab the key off the response to use when referencing this property in other LUSID calls
    strategy_property_key = property_response.key

    # Pretty print our strategy property key
    prettyprint.heading('Strategy Property Key: ', strategy_property_key)
    return strategy_property_key
    
def upsert_trades(analyst_transactions, strategy_property_key, scope, portfolio_code, api_factory):
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
    transaction_response = api_factory.build(lusid.api.TransactionPortfoliosApi).upsert_transactions(
        scope=scope,
        code=portfolio_code,
        transaction_request=batch_transaction_requests)

    # Pretty print the response from LUSID
    prettyprint.transactions_response(
        transaction_response,
        scope, 
        portfolio_code)

def get_figi_LUID(instrument, api_factory):
    luid = api_factory.build(lusid.api.InstrumentsApi).get_instrument(
        identifier_type='Figi',
        identifier=instrument['figi']).lusid_instrument_id
    return luid

def create_instrument_quotes(quotes_effective_date, today, instrument_prices, analyst_scope_code, api_factory):
    # Create prices via instrument, analytic
    # Set our quotes effective dates
    now = datetime.now(pytz.UTC).replace(hour=0, minute=0, second=0, microsecond=0)
    quotes_effective_date = now - timedelta(days=3)
    today = now

    instrument_quotes = {}

    # Create prices for all instruments except cash
    for index, instrument in instrument_prices.iterrows():

        if 'Cash' in instrument['instrument_name']:
            continue

        # Get our Lusid Instrument Id
        luid = api_factory.build(lusid.api.InstrumentsApi).get_instrument(
            identifier_type='Figi',
            identifier=instrument['figi']).lusid_instrument_id

        instrument_quotes[luid + str(quotes_effective_date)] = models.UpsertQuoteRequest(
            quote_id=models.QuoteId(
                quote_series_id=models.QuoteSeriesId(
                    provider='DataScope',
                    instrument_id=luid,
                    instrument_id_type='LusidInstrumentId',
                    quote_type='Price',
                    field='Mid'
                ),
                effective_at=quotes_effective_date
            ),
            metric_value=models.MetricValue(
                value=instrument["price_original"],
                unit=instrument["currency"]),
            lineage='InternalSystem'
        )

        instrument_quotes[luid + str(today)] = models.UpsertQuoteRequest(
            quote_id=models.QuoteId(
                quote_series_id=models.QuoteSeriesId(
                    provider='DataScope',
                    instrument_id=luid,
                    instrument_id_type='LusidInstrumentId',
                    quote_type='Price',
                    field='Mid'
                ),
                effective_at=today
            ),
            metric_value=models.MetricValue(
                value=instrument["price_current"],
                unit=instrument["currency"]),
            lineage='InternalSystem'
        )

    response = api_factory.build(lusid.api.QuotesApi).upsert_quotes(
        scope=analyst_scope_code,
        request_body=instrument_quotes
    )

    prettyprint.upsert_quotes_response(response)

def create_aggregation_request(analyst_scope_code, today, quotes_date):

    # Create our aggregation request
    inline_recipe = models.ConfigurationRecipe(
        scope="User",
        code='quotes_recipe',
        market=models.MarketContext(
            market_rules=[
                models.MarketDataKeyRule(
                    key='Equity.LusidInstrumentId.*',
                    supplier='DataScope',
                    data_scope=analyst_scope_code,
                    quote_type='Price',
                    field='Mid',
                    quote_interval=quotes_date.strftime("%Y-%m-%d")
                )

            ],
            suppliers=models.MarketContextSuppliers(
                commodity='DataScope',
                credit='DataScope',
                equity='DataScope',
                fx='DataScope',
                rates='DataScope'),
            options=models.MarketOptions(
                default_supplier='DataScope',
                default_instrument_code_type='LusidInstrumentId',
                default_scope=analyst_scope_code)
        ),        

    )

    aggregation_request = models.AggregationRequest(
        inline_recipe=inline_recipe,
        effective_at=today,
        metrics=[
            models.AggregateSpec(
                key='Instrument/default/LusidInstrumentId',
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
            'Instrument/default/LusidInstrumentId'
        ])
    
    return aggregation_request


def setup_index(analyst_scope_code, reference_portfolio_code, instrument_prices, api_factory):
    # Set an arbitary index level to start our index with
    index_level = 1000
    # Call LUSID - get the constituents of our index from our reference portfolio
    constituents = api_factory.build(lusid.api.ReferencePortfolioApi).get_reference_portfolio_constituents(
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
        Luid = api_factory.build(lusid.api.InstrumentsApi).get_instrument(
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
