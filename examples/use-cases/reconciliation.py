# Import LUSID
import lusid.models as models
import lusid_sample_data as import_data

# Import Libraries
import printer as prettyprint
from datetime import datetime
import pytz

# Authenticate our user and create our API client
client = import_data.authenticate_secrets()

def fetch_scope(scope_name):
    scope_id = import_data.create_scope_id()
    return '{}-{}'.format(scope_name, scope_id)

def create_portfolio(scope, display_name, code, base_currency, description, created):
    # Create the request to add our portfolio
    portfolio_request = models.CreateTransactionPortfolioRequest(
        display_name=display_name,
        code=code,
        base_currency=base_currency,
        description=description,
        created=created)

    # Create our portfolio
    response = client.transaction_portfolios.create_portfolio(
        scope=scope,
        create_request=portfolio_request)

    prettyprint.portfolio_response(response)

def create_portfolio_group(scope, portfolio_group, portfolio_group_code):
    # inputs : scope, portfolio_group, portfolio_group_code
    
    # Prepare a list of ResourceIDs for our portfolios
    portfolio_resource_ids = [
        models.ResourceId(
            scope=scope,
            code=portfolio_code) for portfolio_code in portfolio_group]

    # Build our request
    portfolio_group_request = models.CreatePortfolioGroupRequest(
        code=portfolio_group_code,
        display_name=portfolio_group_code,
        values=portfolio_resource_ids,
        description=portfolio_group_code)

    # Create our portfolio group
    response = client.portfolio_groups.create_portfolio_group(
        scope=scope,
        request=portfolio_group_request)

    prettyprint.portfolio_group_response(response, 'created')

def create_portfolios_and_groups(scopes, client_portfolios, portfolio_creation_date):
    # Iterate over our two scopes, this will create our portfolios and portfolio groups in both scopes
    for scope in scopes:

        # Iterate over our portfolio groups selecting the name of the group and the list of portfolios
        for portfolio_group_code, portfolio_group in client_portfolios.items():

            # Loop over our list of portfolios selecting the portfolio code
            for portfolio_code in portfolio_group:

                # Create the request to add our portfolio
                portfolio_request = models.CreateTransactionPortfolioRequest(
                    display_name=portfolio_code,
                    code=portfolio_code,
                    base_currency='GBP',
                    description=portfolio_code,
                    created=portfolio_creation_date)

                # Create our portfolio
                response = client.transaction_portfolios.create_portfolio(
                    scope=scope,
                    create_request=portfolio_request)

                prettyprint.portfolio_response(response)


            '''
            Now that we have created all of the portfolios for this client we can create our portfolio group and add the
            portfolios to it. To add a portfolio to a group we refer to it by its LUSID ResourceId. This is simply the
            scope and code of the portfolio
            '''

            # Prepare a list of ResourceIDs for our portfolios
            portfolio_resource_ids = [
                models.ResourceId(
                    scope=scope,
                    code=portfolio_code) for portfolio_code in portfolio_group]

            # Build our request
            portfolio_group_request = models.CreatePortfolioGroupRequest(
                code=portfolio_group_code,
                display_name=portfolio_group_code,
                values=portfolio_resource_ids,
                description=portfolio_group_code)

            # Create our portfolio group
            response = client.portfolio_groups.create_portfolio_group(
                scope=scope,
                request=portfolio_group_request)

            prettyprint.portfolio_group_response(response, 'created')

    print ('All portfolios have been created')
    
def batch_upsert_instruments(instrument_universe):
    # Initialise our batch upsert request
    batch_upsert_request = {}
    # Using our instrument universe create our batch request
    for instrument_name, instrument in instrument_universe.items():
        batch_upsert_request[instrument_name] = models.InstrumentDefinition(
            name=instrument_name,
            identifiers={
                'ClientInternal': models.InstrumentIdValue(
                    value=instrument['identifiers']['ClientInternal'])
            }
        )

    # Upsert our batch
    instrument_response = client.instruments.upsert_instruments(
        requests=batch_upsert_request)

    return instrument_response

def add_luids(instrument_response, instrument_universe):
    # Loop over our recently upserted instruments
    for instrument_name, instrument in instrument_response.values.items():
        # Add our LUID as a new identifier so that we can use it in our calls later
        instrument_universe[instrument_name]['identifiers']['LUID'] = instrument.lusid_instrument_id
        
def add_cash_instrument(instrument_universe, currency):
    instrument_universe['{}_Cash'.format(currency)] = {
    'identifiers': {'LUID': '{}'.format(currency)},
    'currency': '{}'.format(currency)}
    
def adjust_holdings_request(portfolio, instrument_universe):
    # Initialise our list of holding adjustments
    holding_adjustments = []

    # Iterate over the holdings in each portfolio
    for instrument_name, holding in portfolio.items():
        # Get our Lusid Instrument ID
        if 'Cash' in instrument_name:
            identifier_key = 'Instrument/default/Currency'
        else:
            identifier_key = 'Instrument/default/LusidInstrumentId'
            
        Luid = instrument_universe[instrument_name]['identifiers']['LUID']
        # Create our adjust holdings request using our instrument universe to get the LUID identifier for the instrument
        holding_adjustments.append(
            models.AdjustHoldingRequest(
                instrument_identifiers={
                    identifier_key: Luid},
                tax_lots=[
                    models.TargetTaxLotRequest(
                        units=holding['quantity'],
                        cost=models.CurrencyAndAmount(
                           amount=holding['quantity'] *
                                  holding['price'],
                           currency=instrument_universe[instrument_name]['currency']),
                        portfolio_cost=holding['quantity'] *
                                      holding['price'],
                        price=holding['price'])
                ])
        )
        
    return holding_adjustments

def set_holdings_response(scope, portfolio_name, holdings_effective_date, holding_adjustments):
    # Set the holdings for our portfolios
    set_holdings_response = client.transaction_portfolios.set_holdings(
        scope=scope,
        code=portfolio_name,
        effective_at=holdings_effective_date,
        holding_adjustments=holding_adjustments)

    prettyprint.set_holdings_response(set_holdings_response, scope, portfolio_name)
        
def set_holdings(client_holdings, scopes, portfolio, instrument_universe, holdings_effective_date):
    # Iterate over our portfolios
    for portfolio_name, portfolio in client_holdings.items():

        # Create our adjust holdings request for the holding in each portfolio
        holding_adjustments = adjust_holdings_request(portfolio, instrument_universe) # but tax_lots are useful ??

        # Iterate over our two scopes
        for scope in scopes:
            
            # Set holdings in our scope
            set_holdings(scope, portfolio_name, holdings_effective_date, holding_adjustments)
            
    print ('All portfolios have been set')
    
def add_transaction_requests(batch_transaction_requests, transaction_id, transaction):
    batch_transaction_requests.append(
        models.TransactionRequest(
            transaction_id=transaction_id,
            type=transaction['type'],
            instrument_identifiers={
                'Instrument/default/LusidInstrumentId': transaction['instrument_uid']},
            transaction_date=transaction['transaction_date'],
            settlement_date=transaction['settlement_date'],
            units=transaction['units'],
            transaction_price=models.TransactionPrice(
                price=transaction['transaction_price'],
                type='Price'),
            total_consideration=models.CurrencyAndAmount(
                amount=transaction['units'] * transaction['transaction_price'],
                currency=transaction['transaction_currency']),
            source='Client',
            transaction_currency=transaction['transaction_currency'])
    )
        
def add_transaction_response(internal_scope_code, portfolio_name, batch_transaction_requests):
    transaction_response = client.transaction_portfolios.upsert_transactions(
        scope=internal_scope_code,
        code=portfolio_name,
        transactions=batch_transaction_requests)

    prettyprint.transactions_response(
        transaction_response, 
        internal_scope_code, 
        portfolio_name)
        
def upsert_transactions(client_transactions, portfolio, internal_scope_code):
    # Iterate over our portfolios
    for portfolio_name, portfolio in client_transactions.items():

        # Initialise a list to hold our transactions for each portfolio
        batch_transaction_requests = []

        # Iterate over the transactions for each portfolio
        for transaction_id, transaction in portfolio.items():

            # Add transaction requests
            add_transaction_requests(batch_transaction_requests, transaction_id, transaction)

        # Upsert transactions to LUSID
        add_transaction_response(internal_scope_code, portfolio_name, batch_transaction_requests)
        
def adjust_holdings_response(scope, portfolio_name, effective_at, holding_adjustments):
    response = client.transaction_portfolios.adjust_holdings(
        scope=scope,
        code=portfolio_name,
        effective_at=effective_at,
        holding_adjustments=holding_adjustments)
        
    prettyprint.adjust_holdings_response(
        response, 
        scope, 
        portfolio_name)
    
def adjust_all_portfolio_holdings(holdings, instrument_universe, scope, effective_at):
    # Iterate over our portfolios
    for portfolio_name, portfolio in holdings.items():

        # Create our adjust holdings request for the holding in each portfolio
        holding_adjustments = adjust_holdings_request(portfolio, instrument_universe)

        adjust_holdings_response(scope, portfolio_name, effective_at, holding_adjustments)

    print ('All holdings adjusted')
    
def define_portfolio(scope, portfolio_name, effective_at):
    portfolio = models.PortfolioReconciliationRequest(
        portfolio_id=models.ResourceId(
            scope=scope,
            code=portfolio_name),
        effective_at=effective_at,
        as_at=datetime.now(pytz.UTC).isoformat())
    
    return portfolio

def reconciliation(portfolio1, portfolio2, portfolio_name, dictionary):
    # Create our reconciliation request
    reconcile_holdings_request = models.PortfoliosReconciliationRequest(
        left=portfolio1,
        right=portfolio2,
        instrument_property_keys=[])

    # Reconcile the two portfolios
    reconciliation = client.reconciliations.reconcile_holdings(
        request=reconcile_holdings_request)

    # If there are any breaks, add them all to our dictionary
    if len(reconciliation.values) > 0:
        dictionary[portfolio_name] = reconciliation
        
def get_late_trades(report, scope, from_transaction_date, to_transaction_date):
    late_trades = {}

    for portfolio_name in report:

        late_trade = client.transaction_portfolios.get_transactions(
            scope=scope,
            code=portfolio_name,
            from_transaction_date=from_transaction_date,
            to_transaction_date=to_transaction_date)

        if len(late_trade.values) > 0:
            late_trades[portfolio_name] = late_trade

    return late_trades

def add_property(trade, property, label_value):
    transaction_id = trade[0].transaction_id
    portfolio_name = trade[2]
    scope = trade[0].properties["Transaction/default/SourcePortfolioScope"].value.label_value
    property_key = '{}/{}/{}'.format(property.domain, property.scope, property.code)
    r = client.transaction_portfolios.upsert_transaction_properties(
        scope=scope,
        code=portfolio_name,
        transaction_id=transaction_id,
        transaction_properties={
            property_key: 
                models.PerpetualProperty(
                    key=property_key,
                    value=models.PropertyValue(label_value=label_value)
                )
        })

    prettyprint.add_property_response(
        r, 
        scope, 
        portfolio_name, 
        transaction_id)