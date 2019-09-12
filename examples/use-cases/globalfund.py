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
import boto3
globals = {}

def connect_athena_s3_clients(AWS_SERVER_PUBLIC_KEY, AWS_SERVER_SECRET_KEY, region):
    """
    param (str) AWS_SERVER_PUBLIC_KEY: The AWS public key for the Athena/S3 user
    param (str) AWS_SERVER_SECRET_KEY: The AWS secret key for the Athena/S3 user
    param (str) region: The default AWS region to use
    
    returns (boto3.s3.resource) s3_client: The AWS S3 client
    returns (boto3.athena.client) athena_client: The AWS Athena client
    """
    
    # Create a boto3 session using AWS access credentials
    session = boto3.Session(
        aws_access_key_id=AWS_SERVER_PUBLIC_KEY,
        aws_secret_access_key=AWS_SERVER_SECRET_KEY,
        region_name=region
    )
    
    # Create an S3 Resource and an Athena client
    s3_client = session.resource('s3')
    athena_client = session.client('athena')
        
    return s3_client, athena_client


def fetch_data(athena_client, s3_client, database_name, sql_query, results_bucket, output_file_path, retry_time):
    
    """
    param (boto3.client) client: The Athena client
    param (boto3.resource) s3: The s3 resource
    param (str) database_name: The name of the database to execute the query against
    param (str) sql_query: The query to execute
    param (str) results_bucket: The bucket to contain the Athena results
    returns (str) output_file_path: The path of the output file from the Athena query
    param (int) retry_time: The retry time in seconds to check that the query has succeeded
    
    returns (Pandas DataFrame) <unamed>: The Pandas DataFrame containing the generated view
    """
    
    # Generate the data view using AWS Athena
    output_bucket, output_path = generate_data_view(
        client=athena_client, 
        results_bucket=results_bucket, 
        database_name=database_name, 
        sql_query=sql_query, 
        retry_time=retry_time
        )

    # Fetch the data view from AWS S3
    fetch_data_view(
        s3=s3_client, 
        bucket=output_bucket, 
        file_path=output_path, 
        output_path=output_file_path, 
        retry_time=retry_time)
    
    # Load the data into a dataframe from the file
    return pd.read_csv(output_file_path)


def generate_data_view(client, results_bucket, database_name, sql_query, retry_time):
    
    """
    param (boto3.athena.client) client: The Athena client
    param (str) results_bucket: The bucket to contain the Athena results
    param (str) database_name: The name of the database to execute the query against
    param (str) sql_query: The query to execute
    param (int) retry_time: The retry time in seconds to check that the query has succeeded
    
    returns (str) output_bucket: The bucket containing the output of the Athena query
    returns (str) output_file_path: The path of the output file from the Athena query
    """

    # Start a new execution query
    response = client.start_query_execution(
        # The SQL query statements to be executed.
        QueryString=sql_query,
        # A unique case-sensitive string used to ensure the request to create the query is idempotent
        ClientRequestToken=str(uuid.uuid4()),
        # The database within which the query executes.
        QueryExecutionContext={
            'Database': database_name
        },
        # Specifies information about where and how to save the results of the query execution.
        ResultConfiguration={
            'OutputLocation': 's3://{}'.format(results_bucket),
            'EncryptionConfiguration': {
                'EncryptionOption': 'SSE_S3'
            }
        }
    )

    # Get the id of the query
    query_id = response['QueryExecutionId']

    while True:
        # Check the status of the query's execution
        response = client.get_query_execution(
            QueryExecutionId=query_id
        )
        # Get the state and output details
        query_state = response['QueryExecution']['Status']['State']
        output_file_details = response['QueryExecution']['ResultConfiguration']['OutputLocation'].split('/')
        output_file_path = output_file_details[3]
        output_bucket = output_file_details[2]

        # If the query has succeeded break the loop
        if query_state == "SUCCEEDED":
            break

        # If it has not succeeded try again after the retry time
        time.sleep(retry_time)

    # Return the output bucket and file path
    return output_bucket, output_file_path


def fetch_data_view(s3, bucket, file_path, output_path, retry_time):
    
    """
    param (boto3.resource) s3: The s3 resource
    param (str) bucket: The bucket to retrieve the file from
    param (str) file_path: The path to the file to retrieve
    param (str) output_path: The path to save the file to
    param (int) retry_time: The time to take before retrying to get the file
    """

    while True:

        try:
            # Try and retrieve the file
            s3.Bucket(bucket).download_file(
                file_path, output_path)
            break
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == "404":
                print("The object does not exist.")
            else:
                raise


def valuation(client, marketdata_scope, portfolio_group, time):
    
    """
    This function values a portfolio group in LUSID
    
    param (lusid.client) client: The LUSID client to use
    param (str) marketdata_scope: The scope of the marketdata to use in the valuation
    param (models.ResourceId) portfolio_group: The resourceId of the portfolio group with its scope and code
    param (date or str) time: The time at which to run the valuation
    
    
    returns (Pandas DataFrame): The response from the valuation
    """

    # Create an inline recipe to use for the valuation
    inline_recipe = models.ConfigurationRecipe(
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

    # Create the aggreation request with the fields required
    aggregation_request = models.AggregationRequest(
        inline_recipe=inline_recipe,
        effective_at=time,
        metrics=[
            models.AggregateSpec(key='Holding/default/SubHoldingKey',
            op='Value'),
            models.AggregateSpec(key='Instrument/default/Name',
            op='Value'),
            models.AggregateSpec(key='Holding/default/Units',
            op='Sum'),
            models.AggregateSpec(key='Holding/default/Cost',
            op='Sum'),
            models.AggregateSpec(key='Holding/default/PV',
            op='Sum'),
        ],
        group_by=[
            'Holding/default/SubHoldingKey'
        ])

    # Perform the valuation
    response = client.aggregation.get_aggregation_by_group(
        scope=portfolio_group.scope,
        code=portfolio_group.code,
        request=aggregation_request)

    # Return the response in a Pandas DataFrame
    return prettyprint.aggregation_responses_generic_df([response])

                
                
def create_portfolio_group(client, scope, code, portfolios):
    
    """
    This creates a portfolio group which contains a group of provided portfolios. This function is idempotent. It attempts
    to delete the portfolio group before creating it to ensure that it will always be created.
    
    param (lusid.client) client: The LUSID client to use
    param (str) scope: The LUSID scope to create the portfolio group in
    param (str) code: The code to create the portfolio group with
    param (list[models.ResourceId]) portfolios: A list of resource ids for the portfolios to add to the group
    
    returns (lusid.models.createportfoliogroupresonse): The response from creating the group
    """
    
    try:
        client.portfolio_groups.delete_portfolio_group(
            scope=scope,
            code=code)
    except:
        pass
    
    group_request = models.CreatePortfolioGroupRequest(
        code=code,
        display_name=code,
        values=portfolios,
        sub_groups=None,
        description=None)

    portfolio_group = client.portfolio_groups.create_portfolio_group(
        scope=scope,
        request=group_request)
    
    return portfolio_group
                
                
def upsert_quotes(client, scope, data_frame, instrument_identifier_mapping, instrument_identifier_heirarchy, required_mapping):
    """
    This function takes quotes from a data_frame and upserts them into LUSID
    
    param (lusid.client) client: The LUSID client to use
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
    response = client.quotes.upsert_quotes(
        scope=scope,
        quotes=instrument_quotes)

    # Pretty print the response
    #prettyprint.upsert_quotes_response(response)
    return prettyprint.upsert_quotes_response(response)               
                
    
def create_transaction_type_configuration(client, aliases, movements):
    
    """
    This function creates a transaction type configuration if it doesn't already exist.
    
    param (lusid.Client) client: The LUSID client to use
    param (list[tuple(str, str)]) aliases: A list of aliases with their type and group to use for the transaction type
    param (list[lusid.models.TransactionConfigurationMovementDataRequest]) movements: The movements to use for the transaction type
    
    return (lusid.models.createtransactiontyperesponse) response: The response from creating the transaction type
    """
    
    # Call LUSID to get your transaction type configuration
    response = client.system_configuration.list_configuration_transaction_types()

    aliases_current = []

    for transaction_grouping in response.values:
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
            
        
    response = client.system_configuration.create_configuration_transaction_type(
        type=models.TransactionConfigurationDataRequest(
            aliases=aliases_new,
            movements=movements,
            properties=None
        )
    )

    return response


def create_portfolios(client, scopes, code, currency):
    
    """
    This function creates a portfolio in multiple scopes. 
    
    param (lusid.Client) client: The LUSID client to use
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
            client.portfolios.delete_portfolio(
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
        response = client.transaction_portfolios.create_portfolio(
            scope=scope,
            create_request=transaction_portfolio_request)
        
        responses.append(response)
        
    return responses

                
def create_cut_labels(client, exchange_names, cut_label_type):
    
    """
    This function creates cut labels for the open or close of a short list
    of known stock exchanges. It is idempotent in that it will check if the cut
    label already exists before creating it. If it does already exist it will delete it
    first before attempting creation. 
    
    param (lusid.Client) client: The LUSID client to use
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
            response = client.cut_labels.get_cut_label_definition(code=exchange_code)
            response = client.cut_labels.delete_cut_label_definition(code=exchange_code)             
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
            response = client.cut_labels.create_cut_label_definition(
                create_request=request)      
            responses.append(response)             
        except lusid.ApiException as e:
            pass
                         
    return responses

                
                                          
 