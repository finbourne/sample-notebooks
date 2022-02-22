import pandas as pd
import pytz
import lusid
import json
import datetime

def add_utc_to_df(df: pd.DataFrame) -> None:
    """"
    This Function modifies an existing Data Frame to contain UTC
    timezone awareness for all columns of types 'datetime' or
    'datetime64[ns]'
    :param pandas.DataFrame: LUSID response object
    :return: None
    """

    datetime_transformations = {
        "datetime": lambda d: d.replace(tzinfo=pytz.utc),
        "datetime64[ns]": lambda d: d.tz_localize('UTC')
    }

    for column in df.columns:
        # Get datatype from column and apply transformation
        dtype = str(df[column].dtype)
        if dtype in datetime_transformations:
            df[column] = df[column].apply(datetime_transformations.get(dtype))


def valuation_response_to_df(results: lusid.ListAggregationResponse) -> pd.DataFrame:
    """"
    This Function returns a pandas Data Frame from a LUSID valuation
    response object
    :param lusid.ListAggregationResponse: LUSID response object
    :return: pandas.DataFrame
    """
    headers = set(results.data[0].keys())

    data = {
        header: [result[header] for result in results.data] for header in headers
    }
    return pd.DataFrame(data)


def upsert_instrument(
        api_factory: lusid.utilities.ApiClientFactory,
        name: str,
        identifier: str,
        identifier_type: str = "ClientInternal",
        definition: lusid.Instrument = None,
):
    """"
    Upserts a LUSID instrument along with it's name and a unique identifier

    Parameters
    ----------
    api_factory : lusid.utilities.ApiClientFactory api_factory
    The api factory to use
    name : str
    The name of the instrument (e.g. 'Finbourne Inc.')
    identifier: str
    The unique identifier like a Figi
    identifier_type: str
    The type of the identifier (e.g. 'Figi')

    Returns
    ----------
    None
    """

    # Creates the instrument definition
    instrument_definition = lusid.models.InstrumentDefinition(
        name=name,
        identifiers={f"{identifier_type}": lusid.models.InstrumentIdValue(f"{identifier}")},
        definition=definition
    )
    upsert_request = {f"{identifier}": instrument_definition}

    # Upserts the instrument to LUSID
    response = api_factory.build(lusid.api.InstrumentsApi).upsert_instruments(
        request_body=upsert_request)

    if response.failed == {}:
        print(f"Instrument {instrument_definition.name} was successfully upserted into LUSID")
        print(f"Instrument created with LUID:{response.values[identifier].lusid_instrument_id}")
    else:
        print("An error occurred with the above upsert_instruments call, see error message:", response.failed)


def create_property(
        api_factory: lusid.utilities.ApiClientFactory,
        domain: str,
        scope: str,
        code: str,
        name: str,
        data_type: str,
):
    """"
    Creates a LUSID property definition and upserts it

    Parameters
    ----------
    api_factory : lusid.utilities.ApiClientFactory api_factory
    The api factory to use
    domain: str
    The domain of the property (e.g. 'Instrument')
    scope: str
    The scope of the property's resource ID
    code: str
    The code of the property's resource ID
    name: str
    The display name of the property
    data_type: str
    The property's date type (e.g. 'String')

    Returns
    ----------
    None
    """

    # Defines the property definition
    request = lusid.models.PropertyDefinition(
        domain=domain,
        scope=scope,
        code=code,
        display_name=name,
        data_type_id=lusid.models.ResourceId(scope="system", code=data_type),
    )

    # Creates and upserts the property definition
    try:
        api_factory.build(lusid.PropertyDefinitionsApi).create_property_definition(request)
        print("Property request sent.")
    except lusid.ApiException as e:
        if json.loads(e.body)["name"] == "PropertyAlreadyExists":
            print(f"Property {domain}/{scope}/{code} already exists")
        else:
            print(e.body)


def equity_swap_transaction(
        api_factory: lusid.utilities.ApiClientFactory,
        portfolio_scope: str,
        portfolio_code: str,
        notional: float,
        number_of_shares: float,
        equity_identifier: str,
        funding_leg_identifier: str,
        transaction_currency: str,
        direction: str,
        trade_date: datetime.datetime,
        transaction_id: str,
        linking_id: str,
        linking_id_property: str,
        funding_leg_identifier_type: str = "ClientInternal",
        equity_identifier_type: str = "ClientInternal",
        settlement_date: datetime.datetime = None,
        equity_txn_suffix: str = "EQ",
):
    """
    Creates a transaction that books either a long/short position
    against an underlying stock/instrument and an associated financing leg.

    Parameters
    ----------
    api_factory : lusid.utilities.ApiClientFactory api_factory
    The api factory to use
    portfolio_scope: str
    The scope of the portfolio, part of the resource ID
    portfolio_code: str
    The code of the portfolio, part of the resource ID
    notional: float
    The notional of the equity swap
    equity_identifier: str
    The identifier of the underlying equity or cash instrument
    funding_leg_identifier: str
    The identifier of the associated funding leg in the swap
    transaction_currency: str
    The currency of the transaction
    direction: str
    The direction of the swap, must be either 'L' or 'S' indicating long or short
    trade_date: datetime.datetime
    The transaction date
    transaction_id: str
    The transaction identifier
    linking_id: str
    The ID linking the equity/cash instrument to the funding leg
    linking_id_property: str
    The linking ID's property key, follows the LUSID property key format, i.e. domain/scope/code
    funding_leg_identifier_type: str
    The identifier type of the funding leg, will default to 'ClientInternal'
    equity_identifier_type: str
    The identifier type of the equity or cash instrument, will default to 'ClientInternal'
    settlement_date: datetime.datetime
    The transaction settlement date, if not provided will be set to the transaction date
    equity_txn_suffix: str
    The suffix to be added to the equity side transaction, will default to 'EQ'

    Returns
    ----------
    tuple(lusid.TransactionRequest)
    """


    # Check direction either L or S
    if direction not in ("L", "S"):
        raise ValueError(
            "Invalid direction passed, please ensure to use either 'L' or 'S' to indicate Long or Short direction.")

    transaction_type = "LongFundingLeg" if direction == "L" else "ShortFundingLeg"

    # Create funding leg transaction against pay/receive leg
    funding_leg_transaction = lusid.models.TransactionRequest(
        transaction_id=transaction_id,
        type=transaction_type,
        instrument_identifiers={f"Instrument/default/{funding_leg_identifier_type}": f"{funding_leg_identifier}"},
        transaction_date=trade_date,
        settlement_date=settlement_date if settlement_date else trade_date,
        units=notional,
        transaction_price=lusid.models.TransactionPrice(price=0, type="Price"),
        total_consideration=lusid.models.CurrencyAndAmount(amount=0, currency=transaction_currency),
        properties={
            "Transaction/default/RequiresFundingLegHistory": lusid.models.PerpetualProperty(
                key="Transaction/default/RequiresFundingLegHistory",
                value=lusid.models.PropertyValue(
                    label_value="required"
                ),
            ),
            linking_id_property: lusid.models.PerpetualProperty(
                key=linking_id_property,
                value=lusid.models.PropertyValue(
                    label_value=linking_id
                )
            )
        },
        transaction_currency=transaction_currency
    )

    # Set equity leg transaction id and define the transaction type
    equity_transaction_id = f"{equity_txn_suffix}-{transaction_id}"
    transaction_type = "LongSyntheticUnderlying" if direction == "L" else "ShortSyntheticUnderlying"

    equity_transaction = lusid.models.TransactionRequest(
        transaction_id=equity_transaction_id,
        type=transaction_type,
        instrument_identifiers={f"Instrument/default/{equity_identifier_type}": f"{equity_identifier}"},
        transaction_date=trade_date,
        settlement_date=settlement_date if settlement_date else trade_date,
        units=number_of_shares,
        transaction_price=lusid.models.TransactionPrice(price=0, type="Price"),
        total_consideration=lusid.models.CurrencyAndAmount(amount=notional, currency=transaction_currency),
        properties={
            linking_id_property: lusid.models.PerpetualProperty(
                key=linking_id_property,
                value=lusid.models.PropertyValue(
                    label_value=linking_id
                )
            )
        },
        transaction_currency=transaction_currency
    )

    return funding_leg_transaction, equity_transaction


def create_funding_leg(
        start_date: datetime.datetime,
        maturity_date: datetime.datetime,
        currency: str,
        rate_or_spread: float,
        pay_receive: str,
        payment_frequency: str,
        day_count_convention: str,
        index_reference: str,
        index_tenor: str,
        notional: float,
        roll_convention: str = "MF",
        settle_days: int = 2,
        reset_days: int = 0
):
    """
        Creates a funding leg instrument that can be used to represent the financing
        leg of a Total Return Swap instrument, or used as an independend instrument.

        Parameters
        ----------
        start_date: datetime.datetime
        The start or inception date of the leg, also the accrual start
        maturity_date: datetime.datetime
        The maturity date of the leg, also the last principal payment date
        currency: str
        The currency of the leg
        rate_or_spread: float
        The rate or spread of the funding leg
        pay_receive: str
        The direction of payments, either 'Pay' or 'Receive'
        payment_frequency: str
        The frequency of payments, e.g. '1M'
        day_count_convention: str
        The day count convention used for accrual periods
        index_reference: str
        The reference index on top of which the spread is applied, e.g. 'LIBOR.USD1M'
        index_tenor: str
        The tenor of the reference index, e.g. '1M'
        notional: float
        The notional of the financing leg, commonly initiated with zero and increased via transactions
        settle_days: int = 2
        The settlement days for payments/cash flows, defaults to 2
        reset_days: int = 0
        The reset days applied to reset/accrual periods, defaults to 0

        Returns
        ----------
        lusid.FundingLeg

    """

    flow_convention_float = lusid.models.FlowConventions(
        currency=currency,
        payment_frequency=payment_frequency,
        settle_days=settle_days,
        reset_days=reset_days,
        day_count_convention=day_count_convention,
        roll_convention=roll_convention,
        reset_calendars=[],
        payment_calendars=[]
    )

    index_convention = lusid.models.IndexConvention(
        currency=currency,
        payment_tenor=index_tenor,
        fixing_reference=index_reference,
        publication_day_lag=0,
        day_count_convention=day_count_convention
    )

    # Create the leg definitions
    leg_definition = lusid.models.LegDefinition(
        rate_or_spread=rate_or_spread,
        index_convention=index_convention,
        pay_receive=pay_receive,
        conventions=flow_convention_float,
        stub_type="LongBack",
        notional_exchange_type="None"
    )

    return lusid.models.FundingLeg(
        start_date=start_date,
        maturity_date=maturity_date,
        notional=notional,
        leg_definition=leg_definition,
        instrument_type="FundingLeg",
    )
