import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta
import pytz
import lusid
import lusid.models as models
import json
from dateutil import parser
import lusid

globals = {}
# Map Numpy data types to LUSID data types
globals['data_type_mapping'] = {
    'object': 'string',
    'float64': 'number',
    'int64': 'number',
    'bool': 'string',
    'datetime64[ns, UTC]': 'string'
}

def file_type_checks(file_name_type_mapping):
    """
    This function checks that all the input files are of the expected type

    :param dict file_name_type_mapping:
    :return:
    """
    # Iterate over each file
    for file_name, file_type in file_name_type_mapping.items():
        # Check that the file name ends with the correct file type
        if not file_name.endswith('.{}'.format(file_type)):
            raise Exception('''The input file "{0}" does not end with ".{1}". Please check that this is a valid {1} file 
            and if so add the extension'''.format(file_name, file_type))


def load_instruments(client, data_frame, instrument_identifier_mapping, instrument_mapping_required, instrument_mapping_optional, property_columns, scope):
    """
    This function upserts instruments

    :param client:
    :param data_frame:
    :param instrument_identifier_mapping:
    :param instrument_mapping_required:
    :param instrument_mapping_optional:
    :return:
    """
    
    dtypes = data_frame.loc[:, property_columns].dtypes

    # Initialise our batch upsert request
    batch_upsert_request = {}

    # Iterate over our instrument universe
    for row, instrument in data_frame.iterrows():

        # Create our identifiers
        identifiers = {}
        
        properties = create_property_values(instrument, -1, scope, 'Instrument', dtypes, instrument_properties=True)

        for identifier_lusid, identifier_column in instrument_identifier_mapping['identifier_mapping'].items():

            if not pd.isna(instrument[identifier_column]):

                identifiers[identifier_lusid] = models.InstrumentIdValue(
                    value=instrument[identifier_column])

        # Add the instrument to our batch request using the FIGI as the main unique identifier
        single_instrument = models.InstrumentDefinition(
            name=instrument[instrument_mapping_required['name']],
            identifiers=identifiers,
            properties=properties)

        batch_upsert_request[instrument[instrument_mapping_required['name']]] = single_instrument

    # Call LUSID to upsert our batch
    instrument_response = client.instruments.upsert_instruments(
        requests=batch_upsert_request)

    # Pretty print the response from LUSID
    return instrument_response


def resolve_instruments(client, data_frame, identifier_mapping):
    """
    This function attempts to resolve each row of the file to an instrument in LUSID

    :param LusidApi client: The LusidApi client to use
    :param Pandas DataFrame data_frame: The DataFrame containing the csv file's data
    :param dict identifier_mapping: The column mapping between allowable identifiers in LUSID
    and identifier columns in the dataframe

    :return: Pandas DataFrame _data_frame: The input DataFrame with resolution columns added
    """
    # Check that the data_frame is a Pandas DataFrame
    if type(data_frame) is not pd.DataFrame:
        raise Exception('data_frame should be a Pandas DataFrame but is of type {}'.format(
            type(data_frame)))

    # Check that the identifier_mapping is a dictionary
    if type(identifier_mapping) is not dict:
        raise Exception('identifier_mapping should be a dictionary but is of type {}'.format(
            type(identifier_mapping)))

    if 'is_cash_with_currency' not in identifier_mapping.keys():
        raise Exception('There is no column specified in the identifier_mapping to identify whether or not an instrument is cash')

    # Check that the values of the mapping exist in the DataFrame
    if not (set([identifier_mapping['is_cash_with_currency']]) <= set(data_frame.columns)):
        raise Exception('there are values in identifier_mapping is cash with currency that are not columns in the dataframe')

    # Check that the values of the mapping exist in the DataFrame
    if not (set(identifier_mapping['identifier_mapping'].values()) <= set(data_frame.columns)):
        raise Exception('there are values in identifier_mapping that are not columns in the dataframe')

    # Get the allowable instrument identifiers from LUSID
    response = client.instruments.get_instrument_identifier_types()

    # Collect the names and property keys for the identifiers and concatenate them
    allowable_identifier_names = [identifier.identifier_type for identifier in response.values]
    allowable_identifier_keys = [identifier.property_key for identifier in response.values]
    allowable_identifiers = allowable_identifier_names + allowable_identifier_keys

    # Check that the identifiers in the mapping are all allowed to be used in LUSID
    if not (set(identifier_mapping['identifier_mapping'].keys()) <= set(allowable_identifiers)):
        raise Exception(
            'there are LUSID identifiers in the identifier_mapping which are not configured in LUSID')

    # Copy the data_frame to ensure the original isn't modified
    _data_frame = data_frame.copy(deep=True)

    # Set up the result Pandas Series to track resolution
    found_with = pd.Series(index=_data_frame.index, dtype=np.dtype(object))
    resolvable = pd.Series(index=_data_frame.index, dtype=np.dtype(bool))
    luid = pd.Series(index=_data_frame.index, dtype=np.dtype(object))
    comment = pd.Series(index=_data_frame.index, dtype=np.dtype(object))

    # Iterate over each row in the DataFrame
    for index, row in _data_frame.iterrows():

        if index % 10 == 0:
            print('Up to row {}'.format(index))
        # Initialise list to hold the identifiers used to resolve
        found_with_current = []
        # Initialise a value of False for the row's resolvability to an instrument in LUSID
        resolvable_current = False
        # Initilise the LUID value
        luid_current = None
        # Initialise the comment value
        comment_current = "No instruments found for the given identifiers"
        # Takes the currency resolution function and applies it
        currency = row[identifier_mapping['is_cash_with_currency']]

        if not pd.isna(currency):
            resolvable_current = True
            found_with_current.append(currency)
            luid_current = currency
            comment_current = 'Resolved as cash with a currency'

        search_requests = []

        # Iterate over identifiers
        for identifier_lusid, identifier_dataframe in identifier_mapping['identifier_mapping'].items():
            # If the identifier exists
            if not pd.isnull(row[identifier_dataframe]):
                # Create the key to reference this identifier in LUSID
                if 'Instrument/default/' not in identifier_lusid:
                    identifier_type = 'Instrument/default/{}'.format(identifier_lusid)
                else:
                    identifier_type = identifier_lusid
                # Pull the value from the transaction
                identifier_value = row[identifier_dataframe]
                # Create a search request for the identifier
                search_requests.append(
                    models.InstrumentSearchProperty(
                        key=identifier_type,
                        value=identifier_value))

        # Call LUSID to search for instruments
        attempts = 0
        
        if len(search_requests) > 0:
            while attempts < 3:
                try:
                    response = client.search.instruments_search(
                        symbols=search_requests,
                        mastered_only=True)
                    break
                except lusid.rest.ApiException as error_message:
                    attempts += 1

            if attempts == 3:
                comment_current = 'Failed to find instrument due to LUSID error during search'
                # Update the luid series
                luid.iloc[index] = luid_current
                # Update the found with series
                found_with.iloc[index] = found_with_current
                # Update the resolvable series
                resolvable.iloc[index] = resolvable_current
                # Update the comment series
                comment.iloc[index] = comment_current
                continue

            search_request_number = -1

            for result in response:

                search_request_number += 1
                # If there are matches
                if len(result.mastered_instruments) == 1:
                    # Add the identifier responsible for the successful search request to the list
                    found_with_current.append(
                        search_requests[
                            search_request_number].key.split('/')[2]
                    )
                    comment_current = 'Uniquely resolved to an instrument in the securities master'
                    resolvable_current = True
                    luid_current = result.mastered_instruments[0].identifiers['LusidInstrumentId'].value
                    break

                elif len(result.mastered_instruments) > 1:
                    comment_current = 'Multiple instruments found for the instrument using identifier {}'.format(
                        search_requests[
                            search_request_number].key.split('/')[2]
                    )
                    resolvable_current = False
                    luid_current = np.NaN
                    

        # Update the luid series
        luid.iloc[index] = luid_current
        # Update the found with series
        found_with.iloc[index] = found_with_current
        # Update the resolvable series
        resolvable.iloc[index] = resolvable_current
        # Update the comment series
        comment.iloc[index] = comment_current

    # Add the series to the dataframe
    _data_frame['resolvable'] = resolvable
    _data_frame['foundWith'] = found_with
    _data_frame['LusidInstrumentId'] = luid
    _data_frame['comment'] = comment

    return _data_frame


def make_code_lusid_friendly(raw_code):
    """
    This function takes a column name and converts it to a LUSID friendly code for us in creating LUSID objects

    :param str raw_code: A raw column header which needs special characters stripped out
    :return: str friendly_code: A LUSID friendly code with special characters removed
    """
    friendly_code = str(raw_code).replace(" ", "") \
        .replace("(", "") \
        .replace(")", "") \
        .replace("/", "") \
        .replace("%", "Percentage")\
        .replace("&", "and")\
        .strip()

    return friendly_code


def create_property_definitions_from_file(client, scope, domain, data_frame, missing_property_columns):
    """
    Creates the property definitions for all the columns in a file

    :param LusidApi client: The LusidApi client to use
    :param str scope: The scope to create the property definitions in
    :param str domain: The domain to create the property definitions in
    :param Pandas Series data_frame_dtypes: The dataframe dtypes to add definitions for
    :return: dict property_key_mapping: A mapping of data_frame columns to property keys
    """

    missing_property_data_frame = data_frame.loc[:, missing_property_columns]

    # Ensure that all data types in the file have been mapped
    if not (set([str(data_type) for data_type in missing_property_data_frame.dtypes.unique()]) <= set(globals['data_type_mapping'])):
        raise Exception('''There are data types in the data_frame which have not been mapped to LUSID data types,
            please ensure that all data types have been mapped before retrying''')

    # Initialise a dictionary to hold the keys
    property_key_mapping = {}

    # Iterate over the each column and its data type
    for column_name, data_type in missing_property_data_frame.dtypes.iteritems():

        # Make the column name LUSID friendly
        lusid_friendly_code = make_code_lusid_friendly(column_name)

        # If there is no data Pandas infers a type of float, would prefer to infer object
        if missing_property_data_frame[column_name].isnull().all():
            print ('{} is null'.format(column_name))
            data_type = 'object'
            data_frame[column_name] = data_frame[column_name].astype('object', copy=False)

        # Create a request to define the property, assumes value_required is false for all
        property_request = models.CreatePropertyDefinitionRequest(
            domain=domain,
            scope=scope,
            code=lusid_friendly_code,
            value_required=False,
            display_name=column_name,
            data_type_id=models.ResourceId(
                scope='default',
                code=globals['data_type_mapping'][str(data_type)])
        )

        # Call LUSID to create the new property
        property_response = client.property_definitions.create_property_definition(
            definition=property_request)

        print('Created - {} - with datatype {}'.format(property_response.key, property_response.data_type_id.code))

        # Grab the key off the response to use when referencing this property in other LUSID calls
        property_key_mapping[column_name] = property_response.key

    return property_key_mapping, data_frame


def find_missing_portfolios(client, scope, codes):
    """
    Finds which of the provided portfolios don't already exist in a scope

    :param LusidApi client: The LusidApi client to use
    :param str scope: The scope of the portfolios
    :param list[str] codes: The codes of the portfolios
    :return: set[str] missing_portfolios: The codes of the missing portfolios
    """

    response = client.portfolios.list_portfolios_for_scope(
        scope=scope
    )

    portfolios_in_lusid = [portfolio.id.code for portfolio in response.values]
    missing_portfolios = set(codes) - set(portfolios_in_lusid)

    return missing_portfolios


def create_portfolios_if_not_exist(client, scope, data_frame, required_mapping, optional_mapping):
    """
    This function creates portfolios

    :param LusidApi client: The LusidApi client to use
    :param str scope: The scope to create the portfolios in
    :param dict mapping: The mapping from the data_frame to LUSID
    :param pandas DataFrame data_frame: The DataFrame containing the portfolio details
    :param datetime created_date: The date from which the portfolios should be effective
    :param str accounting_method: The accounting method of the portfolios
    :return: dict[str: models.Portfolio]: A dict of the created portfolios keyed by the code
    """
    responses = {}

    portfolio_codes_to_check = data_frame[required_mapping['code']].unique()

    # Get all the portfolios currently in the scope
    existing_portfolios_in_scope = client.portfolios.list_portfolios_for_scope(scope=scope)
    existing_portfolio_codes = [portfolio.id.code for portfolio in existing_portfolios_in_scope.values]

    # Determine which need to be created by excluding those that already exist
    portfolio_codes_to_create = list(set(portfolio_codes_to_check) - set(existing_portfolio_codes))

    for code in portfolio_codes_to_create:

        portfolio = data_frame.loc[data_frame[required_mapping['code']] == code]

        # Build the request to create the portfolio
        request = models.CreateTransactionPortfolioRequest(
            display_name=portfolio[required_mapping['display_name']].values[0],
            code=make_code_lusid_friendly(code),
            created=portfolio[required_mapping['created']].values[0],
            base_currency=portfolio[required_mapping['base_currency']].values[0])

        for lusid_field, column_name in optional_mapping.items():

            if column_name is not None:
                setattr(request, lusid_field, portfolio[column_name].values[0])

        # Call LUSID to create the portfolio
        response = client.transaction_portfolios.create_portfolio(
            scope=scope,
            create_request=request
        )

        responses[code] = response

    return responses


def set_transaction_mapping(client, transaction_mapping):
    """
    Sets the transaction mapping in LUSID so that the system can resolve the transactions into movements

    :param LusidApi client: The LusidApi client to use
    :param dict transaction_mapping: The transaction mapping configuration
    :return: ResourceListOfTransactionConfigurationData response: The response from LUSID
    """

    # Initialise your list of configuration requests, one for each transaction type
    configuration_requests = []

    # Iterate over your configurations in the default mapping
    for configuration in transaction_mapping['values']:

        # Initialise your list of aliases for this configuration
        aliases = []

        # Iterate over the aliases in the imported config
        for alias in configuration['aliases']:
            # Append the alias to your list
            aliases.append(
                models.TransactionConfigurationTypeAlias(
                    type=alias['type'],
                    description=alias['description'],
                    transaction_class=alias['transactionClass'],
                    transaction_group=alias['transactionGroup'],
                    transaction_roles=alias['transactionRoles']))

        # Initialise your list of movements for this configuration
        movements = []

        # Iterate over the movements in the impoted config
        for movement in configuration['movements']:

            # Add properties if they exist in the config
            if len(movement['properties']) > 0:
                key = movement['properties'][0]['key']
                value = models.PropertyValue(
                    label_value=movement['properties'][0]['value'])
                properties = {key: models.PerpetualProperty(
                    key=key,
                    value=value
                )}
            else:
                properties = {}

            if len(movement['mappings']) > 0:
                mappings = [
                    models.TransactionPropertyMappingRequest(
                        property_key=movement['mappings'][0]['propertyKey'],
                        set_to=movement['mappings'][0]['setTo'])
                ]
            else:
                mappings = []

            # Append the movement to your list
            movements.append(
                models.TransactionConfigurationMovementDataRequest(
                    movement_types=movement['movementTypes'],
                    side=movement['side'],
                    direction=movement['direction'],
                    properties=properties,
                    mappings=mappings))

        # Build your configuration for this transaction type
        configuration_requests.append(
            models.TransactionConfigurationDataRequest(
                aliases=aliases,
                movements=movements,
                properties=None))

    # Call LUSID to set your configuration for our transaction types
    response = client.system_configuration.set_configuration_transaction_types(
        types=configuration_requests)

    return response


def load_file_multiple_portfolios(client, scope, data_frame, mapping_required, mapping_optional, source, file_type, identifier_mapping=None, property_columns=[]):
    """
    Handles loading transactions into multiple portfolios

    :param LusidApi client: The LusidApi client to use
    :param str scope: The scope of the portfolios to load the transactions into
    :param Pandas DataFrame data_frame: The dataframe containing the transactions
    :param dict{str, str} mapping_required: The dictionary mapping the dataframe fields to LUSID's required base transaction/holding schema
    :param dict{str, str} mapping_optional: The dictionary mapping the dataframe fields to LUSID's optional base transaction/holding schema
    :param str source: The source system of the transactions
    :param str file_type: The type of file i.e. transactions or holdings or instruments
    :param dict{str, str} identifier_mapping: The dictionary mapping of LUSID instrument identifiers to identifiers in the dataframe
    :param list[str] property_columns: The columns to create properties for
    :return: dict{str, UpsertPortfolioTransactionsResponse} responses: A mapping between the portfolio and the response
    """
    # Initialise the responses dictionary
    responses = {}

    if file_type.lower() not in ['transaction', 'holding', 'instrument']:
        raise Exception('The file_type must be one of "transaction" or "holding" or "instrument", you supplied {}'.format(file_type))

    domain_lookup = {
        'transaction': 'Transaction',
        'holding': 'Holding',
        'instrument': 'Instrument'
    }

    
    missing_property_columns, data_frame = check_property_definitions_exist_in_scope(
        client=client,
        scope=scope,
        domain=domain_lookup[file_type.lower()],
        data_frame=data_frame)

    print('Check for missing {} properties complete'.format(file_type.lower()))

    # If there are missing properties
    if len(missing_property_columns) > 0:
        if len(property_columns) > 0:
            missing_property_columns = [x for x in missing_property_columns if x in property_columns]
        if len(missing_property_columns) > 0:
            print('There are missing {} properties, these will be added'.format(file_type.lower()))
            print(missing_property_columns)

        # Create property definitions for all of the columns in the file that have missing definitions
        property_key_mapping, data_frame = create_property_definitions_from_file(
            client=client,
            scope=scope,
            domain=domain_lookup[file_type.lower()],
            data_frame=data_frame,
            missing_property_columns=missing_property_columns)
        
    if 'instrument' in file_type.lower():
        response = load_instruments(client, data_frame, identifier_mapping, mapping_required, mapping_optional, property_columns, scope)
        return {'instruments': response}
        
    # Get the unique portfolios
    portfolios = data_frame[mapping_required['portfolio_code']].unique()   
        
    # Iterate over each portfolio and upsert the transactions
    for portfolio in portfolios:
        _data_frame = data_frame.loc[data_frame[mapping_required['portfolio_code']] == portfolio]
        if 'transaction' in file_type.lower():
            response = load_transactions(client, scope, str(portfolio), _data_frame,  mapping_required, mapping_optional, source, property_columns)
        elif 'holding' in file_type.lower():
            response = load_holdings(client, scope, str(portfolio), _data_frame,  mapping_required, mapping_optional)
        
        responses['portfolio'] = response
    return responses


def check_property_definitions_exist_in_scope(client, scope, domain, data_frame):

    """
    This function identifiers which property definitions are missing from LUSID

    :param LusidApi client: The LusidApi client to use
    :param str scope: The scope to check for property definitions in
    :param str domain: The domain to check for property definitions in
    :param Pandas DataFrame data_frame: The dataframe to check properties for
    :return: list[str] missing_property_columns: The columns missing properties in LUSID
    """

    data_type_update_map = {
        'number': 'float64',
        'string': 'object'
    }

    # Initialise a set to hold the missing properties
    missing_keys = set([])
    # Iterate over the column names
    column_property_mapping = {}
    for column_name, data_type in data_frame.dtypes.iteritems():
        # Create the property key
        property_key = '{}/{}/{}'.format(
            domain, scope, make_code_lusid_friendly(column_name)
        )
        column_property_mapping[property_key] = column_name

        # Get a tuple with the first value being True/False key is missing, second is data type of the key
        result = check_property_definitions_exist_in_scope_single(client, property_key)
        # If the key is missing add it to the set
        if result[0]:
            missing_keys.add(property_key)
        # If it is not missing check that the data type of the property matches the dataframe
        else:
            data_type_lusid = result[1]
            # If the data type does not match
            if data_type_lusid != globals['data_type_mapping'][str(data_type)]:
                print("data types don't match for column {} it is {} in LUSID and {} in file".format(
                    column_name,
                    data_type_lusid,
                    data_type))
                # Update the data type in the dataframe if possible
                data_frame[column_name] = data_frame[column_name].astype(
                    data_type_update_map[data_type_lusid], copy=False)

                print('Updated {} to {}'.format(column_name, data_type_update_map[data_type_lusid]))

    missing_property_columns = [column_property_mapping[property_key] for property_key in missing_keys]

    return missing_property_columns, data_frame


def check_property_definitions_exist_in_scope_single(client, property_key):
    """
    This function takes a list of property keys and looks to see which property definitions already exist inside LUSID

    :param LusidApi client: The LusidApi client to use
    :param list[str] property_keys: The property keys to get from LUSID
    :return: tuple(missing, data_type): Whether or not they key is missing and if it is not it's data type
    """

    data_type = None

    try:
        response = client.property_definitions.get_property_definition(
            domain=property_key.split('/')[0],
            scope=property_key.split('/')[1],
            code=property_key.split('/')[2])

        missing = False
        data_type = response.data_type_id.code

    except lusid.rest.ApiException:
        missing = True

    return (missing, data_type)


def create_property_values(row, null_value, scope, domain, dtypes, instrument_properties=False):
    """
    This function generates the property values for a row in a file

    :param Pandas Series row:
    :param number null_value:
    :param str scope:
    :param str domain:
    :return: dict {str, models.PerpetualProperty} properties:
    """
    # Ensure that all data types in the file have been mapped
    if not (set([str(data_type) for data_type in dtypes.unique()]) <= set(globals['data_type_mapping'])):
        raise Exception('''There are data types in the data_frame which have not been mapped to LUSID data types,
            please ensure that all data types have been mapped before retrying''')


    # Initialise the empty properties dictionary
    properties = {}

    # Iterate over each column name and data type
    for column_name, data_type in dtypes.iteritems():

        # Set the data type to be a string so that it is easier to work with
        string_data_type = str(data_type)
        # Convert the numpy data type to a LUSID data type using the global mapping
        lusid_data_type = globals['data_type_mapping'][string_data_type]
        # Get the value of the column from the row
        row_value = row[column_name]

        # Use the correct LUSID property value based on the data type
        if lusid_data_type == 'string':
            if pd.isna(row_value):
                row_value = str(null_value)
            property_value = models.PropertyValue(
                label_value=row_value)

        if lusid_data_type == 'number':
            # Handle null values given the input null value override
            if pd.isnull(row_value):
                row_value = null_value

            property_value = models.PropertyValue(
                metric_value=models.MetricValue(
                    value=row_value))

        # Set the property
        properties[
            '{}/{}/{}'.format(
                domain, scope, make_code_lusid_friendly(column_name))
        ] = models.PerpetualProperty(
                key='{}/{}/{}'.format(domain, scope, make_code_lusid_friendly(column_name)),
                value=property_value
        )
        
    # If these properties are for instruments they need to be in a list rather than a dictionary
    if instrument_properties:
        properties = list(properties.values())
            
    return properties



def convert_datetime_utc(datetime):
    """
    This function ensures that a variable is a timezone aware UTC datetime

    :param datetime:
    :return:
    """

    if isinstance(datetime, str):
        datetime = parser.parse(datetime)

    return datetime


def load_transactions(client, scope, code, data_frame, transaction_mapping_required, transaction_mapping_optional, source, property_columns=[]):
    """
    This function loads transactions for a given portfolio into LUSID

    :param LusidApi client: The LusidApi client to use
    :param str scope: The scope of the portfolio to upsert the transactions into
    :param str code: The code of the portfolio to upsert the transactions into
    :param Pandas DataFrame data_frame: The dataframe containing the data
    :param dict {str, str} transaction_mapping: The mapping of the fields from the dataframe to LUSID
    :param str source: The source system of the transactions, used to fetch the correct transaction types
    :return: UpsertPortfolioTransactionsResponse response: Response from LUSID to the upsert request
    """
    # Initialise a list to hold the requests
    transaction_requests = []
    if len(property_columns) > 0:
        dtypes = data_frame.loc[:, property_columns].dtypes
    else:
        dtypes = data_frame.drop(['resolvable', 'foundWith', 'LusidInstrumentId', 'comment'], axis=1).dtypes

    # Iterate over each transaction
    for index, transaction in data_frame.iterrows():

        # Set the identifier for the transaction which was found earlier
        if transaction['comment'] == 'Resolved as cash with a currency':
            identifier_key = 'Currency'
        else:
            identifier_key = 'LusidInstrumentId'

        identifiers = {
            'Instrument/default/{}'.format(identifier_key): transaction['LusidInstrumentId']
        }

        # Set the properties for the transaction
        properties = create_property_values(transaction, -1, scope, 'Transaction', dtypes)

        exchange_rate = None

        if ('exchange_rate' in transaction_mapping_optional.keys()) and (transaction_mapping_optional['exchange_rate'] is not None):

            exchange_rate = transaction[transaction_mapping_optional['exchange_rate']]

            properties['Transaction/default/TradeToPortfolioRate'] = models.PerpetualProperty(
                key='Transaction/default/TradeToPortfolioRate',
                value=models.PropertyValue(
                    metric_value=models.MetricValue(
                        value=1/exchange_rate
                    )
                )
            )

        # Create the transaction request
        transaction_requests.append(
            models.TransactionRequest(
                transaction_id=make_code_lusid_friendly(transaction[transaction_mapping_required['transaction_id']]),
                type=transaction[transaction_mapping_required['transaction_type']],
                instrument_identifiers=identifiers,
                transaction_date=convert_datetime_utc(transaction[transaction_mapping_required['transaction_date']]),
                settlement_date=convert_datetime_utc(transaction[transaction_mapping_required['settlement_date']]),
                units=transaction[transaction_mapping_required['units']],
                transaction_price=models.TransactionPrice(
                    price=transaction[transaction_mapping_required['transaction_price.price']],
                    type='Price'),
                total_consideration=models.CurrencyAndAmount(
                    amount=transaction[transaction_mapping_required['total_consideration.amount']],
                    currency=make_code_lusid_friendly(transaction[transaction_mapping_required['total_consideration.currency']])),
                exchange_rate=exchange_rate,
                transaction_currency=make_code_lusid_friendly(transaction[transaction_mapping_required['transaction_currency']]),
                source=source,
                properties=properties
                )
        )

    # Call LUSID to upsert the transactions
    response = client.transaction_portfolios.upsert_transactions(
        scope=scope,
        code=code,
        transactions=transaction_requests)

    return response


def load_holdings(client, scope, code, data_frame, holdings_mapping_required, holdings_mapping_optional):
    """
    This function sets the holdings for a given portfolio from a set of holdings

    :param LusidApi client: The LusidApi client to use
    :param str scope: The scope of the portfolio to upsert the holdings into
    :param str code: The code of the portfolio to upsert the holdings into
    :param Pandas DataFrame data_frame: The dataframe containing the data
    :param dict{str, str} holdings_mapping: The mapping of the fields from the dataframe to LUSID
    :return: response models.AdjustHolding: The response from LUSID after setting the holdings
    """
    # Initialise a list to hold the requests
    holding_adjustments = []
    # Create a Pandas Series with the column names and data types less the resolved details for property generation
    dtypes = data_frame.drop(['resolvable', 'foundWith', 'LusidInstrumentId', 'comment'], axis=1).dtypes
    # Get all effective dates from the file
    effective_dates = list(data_frame[holdings_mapping_required['effective_date']].unique())
    # If there is more than one throw an error
    if len(effective_dates) > 1:
        raise Exception('There are {} effective dates in the holding file, need there to be just one'.format(
            len(effective_dates))
        )
    # Convert the effective date to be a timezone aware datetime
    effective_date = pytz.utc.localize(parser.parse(effective_dates[0]))

    # Iterate over each holding
    for index, holding in data_frame.iterrows():

        # Set the identifier for the holding which was found earlier
        if holding['comment'] == 'Resolved as cash with a currency':
            identifier_key = 'Currency'
        else:
            identifier_key = 'LusidInstrumentId'

        identifiers = {
            'Instrument/default/{}'.format(identifier_key): holding['LusidInstrumentId']
        }

        # Set the properties for the holding
        properties = create_property_values(holding, -1, scope, 'Holding', dtypes)

        single_cost = models.CurrencyAndAmount(
            amount=None,
            currency=None
        )

        for lusid_field, column_name in holdings_mapping_optional.items():
            if (lusid_field.split(".")[1] == 'cost') and (column_name is not None):
                setattr(single_cost, lusid_field.split(".")[2], holding[column_name])

        if (single_cost.amount is None) and (single_cost.currency is None):
            single_cost = None

        single_tax_lot =  models.TargetTaxLotRequest(
            units=holding[holdings_mapping_required['tax_lots.units']],
            cost=single_cost)

        for lusid_field, column_name in holdings_mapping_optional.items():
            if (lusid_field.split(".")[1] != 'cost') and (column_name is not None):
                setattr(single_tax_lot, lusid_field.split(".")[2], holding[column_name])

        single_holding_adjustment = models.AdjustHoldingRequest(
            instrument_identifiers=identifiers,
            tax_lots=[single_tax_lot],
            properties=properties
        )
      

        # Create the adjust holding request
        holding_adjustments.append(single_holding_adjustment)

    # Call LUSID to upsert the transactions
    response = client.transaction_portfolios.adjust_holdings(
        scope=scope,
        code=code,
        effective_at=effective_date,
        holding_adjustments=holding_adjustments)

    return response





