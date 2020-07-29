# Import LUSID
import lusid
import lusid.models as models
import lusid_sample_data as import_data
# Import Libraries
import pprint
from datetime import datetime, timedelta, time, date
import pytz
import uuid
import printer as prettyprint
from datetime import datetime
import pandas as pd
import numpy as np
import os
import json
import time
globals = {}

def valuation(api_factory, marketdata_scope, portfolio_group, time):
    
    time_parts = [time[:10], time[11:]]
    
    if time_parts[1] == 'LSE_market_close':
        time_parts[1] = "16:30:00.000000+00:00"
    elif time_parts[1] == 'NYSE_market_close':
        time_parts[1] = "21:00:00.000000+00:00"
        
    time = "T".join(time_parts)

    inline_recipe = models.ConfigurationRecipe(
        scope="User",
        code='quotes_recipe',
        market=models.MarketContext(
            market_rules=[
                models.MarketDataKeyRule(
                   key='Equity.Figi.*',
                   supplier='DataScope',
                   data_scope=marketdata_scope,
                   quote_type='Price',
                   field='Mid'),
               models.MarketDataKeyRule(
                   key='Equity.Isin.*',
                   supplier='DataScope',
                   data_scope=marketdata_scope,
                   quote_type='Price',
                   field='Mid'),
                models.MarketDataKeyRule(
                   key='Equity.LusidInstrumentId.*',
                   supplier='DataScope',
                   data_scope=marketdata_scope,
                   quote_type='Price',
                   field='Mid'),
                models.MarketDataKeyRule(
                   key='Fx.CurrencyPair.*',
                   supplier='DataScope',
                   data_scope=marketdata_scope,
                   quote_type='Rate',
                   field='Mid')
            ],
            suppliers=models.MarketContextSuppliers(
                commodity='DataScope',
                credit='DataScope',
                equity='DataScope',
                fx='DataScope',
                rates='DataScope'),
            options=models.MarketOptions(
                default_supplier='DataScope',
                default_instrument_code_type='Figi',
                default_scope=marketdata_scope)
        )
    )

    aggregation_request = models.AggregationRequest(
        inline_recipe=inline_recipe,
        effective_at=time,
        metrics=[
            models.AggregateSpec(key='Instrument/default/LusidInstrumentId',
            op='Value'),
            models.AggregateSpec(key='Instrument/default/Name',
            op='Value'),
            models.AggregateSpec(key='Holding/default/Units',
            op='Sum'),
            models.AggregateSpec(key='Holding/default/Cost',
            op='Sum'),
            models.AggregateSpec(key='Holding/default/PV',
            op='Sum'),
            models.AggregateSpec(key='Holding/default/PV',
            op='Proportion')
        ],
        group_by=[
            'Instrument/default/LusidInstrumentId'
        ],
        portfolio_identifier_code="GroupPortfolio")

    response = api_factory.build(lusid.api.AggregationApi).get_aggregation(
        scope=portfolio_group.scope,
        code=portfolio_group.code,
        aggregation_request=aggregation_request)
    
    dataframe = prettyprint.aggregation_responses_generic_df([response])
    dataframe = dataframe.append(dataframe.sum(numeric_only=True), ignore_index=True)
    return dataframe

                
                
def create_portfolio_group(api_factory, scope, code, portfolios):
    
    """
    This creates a portfolio group which contains a group of provided portfolios. This function is idempotent. It attempts
    to delete the portfolio group before creating it to ensure that it will always be created.
    
    param (lusid.utilities.ClientApiFactory) api_factory: The LUSID api factory to use
    param (str) scope: The LUSID scope to create the portfolio group in
    param (str) code: The code to create the portfolio group with
    param (list[models.ResourceId]) portfolios: A list of resource ids for the portfolios to add to the group
    param (datetime) creation_date: The creation date of the portfolio group
    
    returns (lusid.models.createportfoliogroupresonse): The response from creating the group
    """

    portfolio_creation_date = datetime.now(pytz.UTC) - timedelta(days=5000)

    try:
        api_factory.build(lusid.api.PortfolioGroupsApi).delete_portfolio_group(
            scope=scope,
            code=code)
    except:
        pass
    
    group_request = models.CreatePortfolioGroupRequest(
        code=code,
        display_name=code,
        values=portfolios,
        sub_groups=None,
        description=None,
        created=portfolio_creation_date)

    portfolio_group = api_factory.build(lusid.api.PortfolioGroupsApi).create_portfolio_group(
        scope=scope,
        create_portfolio_group_request=group_request)
    
    return portfolio_group
                
                
def upsert_quotes(api_factory, scope, data_frame, instrument_identifier_mapping, instrument_identifier_heirarchy, required_mapping):
    """
    This function takes quotes from a data_frame and upserts them into LUSID
    
    param (lusid.utilities.ClientApiFactory) api_factory: The LUSID api factory to use
    param (str) scope: The LUSID scope to upsert the quotes into
    param (Pandas DataFrame) data_frame: The DataFrame that the quotes are in
    param (dict) instrument_identifier_mapping : The dictionary with the instrument identifier mapping between LUSID and the dataframe
    param (list[str]) instrument_identifier_heirarchy : The heirarchy to use for the LUSID instrument identifiers when upserting quotes
    param (dict) required_mapping: The mapping of the LUSID required quote fields to the dataframe fields
    
    
    returns (Pandas DataFrame): The succesfully upserted quotes
    """
    
    # Initialise an empty instrument quotes list to hold the quotes
    instrument_quotes = {}
    
    quote_type_values = {
        'mid_price': {
            'quote_type': 'Price',
            'price_side': 'Mid',
            'value': 'price',
        },
        'mid_rate': {
            'quote_type': 'Rate',
            'price_side': 'Mid',
            'value': 'rate',
        }
    }
    
    # Iterate over the quotes
    for index, quote in data_frame.iterrows():
        
        quote_type = quote_type_values[quote[required_mapping['quote_type']]]["quote_type"]
        field = quote_type_values[quote[required_mapping['quote_type']]]["price_side"]
            
        for identifier in instrument_identifier_heirarchy:
            
            identifier_value = quote[instrument_identifier_mapping['identifier_mapping'][identifier]]
            
            if (identifier == "CurrencyPair") and (len(identifier_value) == 6):
                identifier_value = identifier_value[:3] + "/" + identifier_value[3:]
                
            
            if not pd.isna(identifier_value):
                break
        
        # Add the quote to the list of upsert quote requests
        effective_date = quote[required_mapping['effective_at']]
        
        instrument_quotes[identifier + "_" + identifier_value + "_" + effective_date] = models.UpsertQuoteRequest(
            quote_id=models.QuoteId(
                quote_series_id=models.QuoteSeriesId(
                    provider='DataScope',
                    instrument_id=identifier_value,
                    instrument_id_type=identifier,
                    quote_type=quote_type,
                    field=field
                ),
                effective_at=effective_date),
            metric_value=models.MetricValue(
                value=quote[required_mapping['value']],
                unit=quote[required_mapping['currency']]),
            lineage='InternalSystem'
        )

        
    # Upsert the quotes into LUSID
    response = api_factory.build(lusid.api.QuotesApi).upsert_quotes(
        scope=scope,
        request_body=instrument_quotes)

    # Pretty print the response
    #prettyprint.upsert_quotes_response(response)
    return prettyprint.upsert_quotes_response(response)               
                
    
def create_transaction_type_configuration(api_factory, aliases, movements):
    
    """
    This function creates a transaction type configuration if it doesn't already exist.
    
    param (lusid.utilities.ClientApiFactory) api_factory: The LUSID api factory to use
    param (list[tuple(str, str)]) aliases: A list of aliases with their type and group to use for the transaction type
    param (list[lusid.models.TransactionConfigurationMovementDataRequest]) movements: The movements to use for the transaction type
    
    return (lusid.models.createtransactiontyperesponse) response: The response from creating the transaction type
    """
    
    # Call LUSID to get your transaction type configuration
    response = api_factory.build(lusid.api.SystemConfigurationApi).list_configuration_transaction_types()

    aliases_current = []

    for transaction_grouping in response.transaction_configs:
        for alias in transaction_grouping.aliases:
            aliases_current.append((alias.type, alias.transaction_group))
    
    aliases_new = []
    
    for alias in aliases:

        if alias in aliases_current:
            return response
        
        aliases_new.append(models.TransactionConfigurationTypeAlias(
            type=alias[0],
            description=alias[0],
            transaction_class=alias[0],
            transaction_group=alias[1],
            transaction_roles='None'
        ))
            
        
    response = api_factory.build(lusid.api.SystemConfigurationApi).create_configuration_transaction_type(
        transaction_configuration_data_request=models.TransactionConfigurationDataRequest(
            aliases=aliases_new,
            movements=movements,
            properties=None
        )
    )

    return response


def create_portfolios(api_factory, scopes, code, currency):
    
    """
    This function creates a portfolio in multiple scopes. 
    
    param (lusid.utilities.ClientApiFactory) api_factory: The LUSID api factory to use
    param (list[str]) scopes: The scopes to create the portfolio in
    param (str) code: The code for the portfolio
    param (str) currency: The base/reporting currency of the portfolio
    
    return (list[lusid.models.createportfolioresponse]) responses: The responses from creating the portfolio in each scope
    """
    # The date your portfolio was first created
    portfolio_creation_date = (datetime.now(pytz.UTC) - timedelta(days=5000))
    
    responses = []
    
    for scope in scopes:
    
        try:
            api_factory.build(lusid.api.PortfoliosApi).delete_portfolio(
                scope=scope,
                code=code
            )
        except lusid.ApiException as e:
            pass
        
        # Create the request to add your portfolio to LUSID
        transaction_portfolio_request = models.CreateTransactionPortfolioRequest(
            display_name="Global Fund",
            code=code,
            base_currency=currency,
            created=portfolio_creation_date,
            sub_holding_keys=None)

        # Call LUSID to create your portfolio
        response = api_factory.build(lusid.api.TransactionPortfoliosApi).create_portfolio(
            scope=scope,
            create_transaction_portfolio_request=transaction_portfolio_request)
        
        responses.append(response)
        
    return responses

                
def create_cut_labels(api_factory, exchange_names, cut_label_type):
    
    """
    This function creates cut labels for the open or close of a short list
    of known stock exchanges. It is idempotent in that it will check if the cut
    label already exists before creating it. If it does already exist it will delete it
    first before attempting creation. 
    
    param (lusid.utilities.ClientApiFactory) api_factory: The LUSID api factory to use
    param (list[str]) exchange_names: The list of exchanges to create cut labels for
    param (str) cut_label_type: The type of cut label to create, options are currently
    'market open' or 'market close'.
    
    return (list[lusid.models.cutlabelresponse]) responses: The responses from creating the cut labels
    """
    
    # The available cut labels and exchanges
    available_cut_labels = ["market_open", "market_close"]
    
    exchange_info = {
        "LSE": {
            "time_zone": "GB",
            "hour": 16,
            "minutes": 30
        },
        "NYSE": {
            "time_zone": "America/New_York",
            "hour": 16,
            "minutes": 0
        }
    }
        
    
    # Validation of the types and the values
    if type(exchange_names) is not list: 
        raise TypeError(f"The exchange_names variable is of type {type(exchange_names)}. It must be a list of strings")
        
    if len(exchange_names) < 1:
        raise ValueError(f"No exchanges were provided, please provide a non-empty list for the variable exchange_names")
        
    if cut_label_type not in available_cut_labels:
        raise ValueError("The provided cut_label_type is not currently supported, please provide one" +
                         f"of the following {', '.join(available_cut_labels)}")
                         
    if not set(exchange_names).issubset(set(exchange_info.keys())):
        raise ValueError("One or more of the provided exchange_names is not currently supported, please provide a subset" +
                         f"of the following {', '.join(available_exchanges)}")
    
    # Delete each cut label if it already exists
    for exchange in exchange_names:
        exchange_code = exchange+'_'+cut_label_type
        try:
            response = api_factory.build(lusid.api.CutLabelDefinitionsApi).get_cut_label_definition(code=exchange_code)
            response = api_factory.build(lusid.api.CutLabelDefinitionsApi).delete_cut_label_definition(code=exchange_code)
        except lusid.ApiException as e:
            pass
    
    responses = []                     
                         
    for exchange in exchange_names:
        exchange_code = exchange+'_'+cut_label_type
        exchange_time = models.CutLocalTime(exchange_info[exchange]['hour'], exchange_info[exchange]['minutes'])          
        request = models.CutLabelDefinition(
            code=exchange_code, 
            description=f"{exchange_code} which is at {exchange_info[exchange]['hour']}:{exchange_info[exchange]['minutes']} local time", 
            display_name=exchange_code,
            cut_local_time=exchange_time,
            time_zone=exchange_info[exchange]['time_zone'])           
        try:
            response = api_factory.build(lusid.api.CutLabelDefinitionsApi).create_cut_label_definition(
                create_cut_label_definition_request=request)
            responses.append(response)             
        except lusid.ApiException as e:
            pass
                         
    return responses

                
                                          
 