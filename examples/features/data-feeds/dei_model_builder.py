# Use first block to import generic non-LUSID packages
import os
import pandas as pd
import datetime
import json
import pytz
from IPython.core.display import HTML

# Then import the key modules from the LUSID package (i.e. The LUSID SDK)
import lusid as lu
import lusid.api as la
import lusid.models as lm
import lumipy as lumi

# And use absolute imports to import key functions from Lusid-Python-Tools and other helper package

from lusid.utilities import ApiClientFactory
from lusidjam import RefreshingToken
from lusidtools.cocoon.cocoon import load_from_data_frame
from lusidtools.pandas_utils.lusid_pandas import lusid_response_to_data_frame
from lusidtools.jupyter_tools import StopExecution

# Authenticate our user and create our API client
secrets_path = os.getenv("FBN_SECRETS_PATH")
token = RefreshingToken()

api_factory = ApiClientFactory(
    token=RefreshingToken(),
    api_secrets_filename=secrets_path,
    app_name="LusidJupyterNotebook",
)

portfolio_api = api_factory.build(lu.api.PortfoliosApi)
properties_api = api_factory.build(lu.api.PropertyDefinitionsApi)
instruments_api = api_factory.build(lu.api.InstrumentsApi)
reference_portfolios_api = api_factory.build(lu.api.ReferencePortfolioApi)
search_api = api_factory.build(lu.api.SearchApi)


def get_instruments_with_dei_data():

    dei_instruments = instruments_api.list_instruments(
        filter="properties.Instrument/DEI/DeiMetrics eq 'Y'",
        limit=500,
        instrument_property_keys=[
            "Instrument/DEI/TotalDeiScore",
            "Instrument/DEI/BoardDeiScore",
            "Instrument/DEI/ExecutiveDeiScore",
            "Instrument/DEI/GenderDeiScore",
            "Instrument/DEI/PctDistributionOfCaucasianExecutives",
        ],
    )

    def format_df(df):

        rename_cols = {}

        column_and_values = df.head(1).copy().to_dict()

        for item in column_and_values:

            if item.endswith("key"):

                new_column = item[:13] + "value.metric_value.value"

                value = column_and_values[item][0]

                rename_cols[new_column] = value[value.rfind("/") + 1 :]

        rename_cols

        df = df.rename(columns=rename_cols)

        cols = [
            "lusid_instrument_id",
            "name",
            "TotalDeiScore",
            "BoardDeiScore",
            "ExecutiveDeiScore",
            "GenderDeiScore",
            "PctDistributionOfCaucasianExecutives",
        ]

        return df[cols].copy()

    df = lusid_response_to_data_frame(dei_instruments)

    formatted_df = format_df(df)

    formatted_df["PctDistributionOfCaucasianExecutives"] = (
        1 - formatted_df["PctDistributionOfCaucasianExecutives"]
    )

    return formatted_df


def dei_filter_by_quantiles(
    df,
    total_dei_quantile_value=0,
    executive_dei_quantile_value=0,
    board_dei_quantile_value=0,
    gender_dei_quantile_value=0,
    pct_dist_cauc_ex_quantile_value=0):

    total_dei_quantile_result = df["TotalDeiScore"].quantile(total_dei_quantile_value)
    executive_dei_quantile_result = df["ExecutiveDeiScore"].quantile(
        executive_dei_quantile_value
    )
    board_dei_quantile_result = df["BoardDeiScore"].quantile(board_dei_quantile_value)
    gender_dei_quantile_result = df["GenderDeiScore"].quantile(
        gender_dei_quantile_value
    )
    pct_dist_cauc_ex_quantile_result = df[
        "PctDistributionOfCaucasianExecutives"
    ].quantile(pct_dist_cauc_ex_quantile_value)

    df = (
        df[
            (df.TotalDeiScore >= total_dei_quantile_result)
            & (df.BoardDeiScore >= board_dei_quantile_result)
            & (df.ExecutiveDeiScore >= executive_dei_quantile_result)
            & (df.GenderDeiScore >= gender_dei_quantile_result)
            & (
                df.PctDistributionOfCaucasianExecutives
                > pct_dist_cauc_ex_quantile_result
            )
        ]
        .copy()
        .sort_values("TotalDeiScore", ascending=False)
    )

    return df


def create_reference_portfolio(portfolio_code, portfolio_scope):

    try:

        response = reference_portfolios_api.create_reference_portfolio(
            scope=portfolio_scope,
            create_reference_portfolio_request=lm.CreateReferencePortfolioRequest(
                display_name=portfolio_code,
                description=portfolio_code,
                code=portfolio_code,
                created="2000-01-01",
                base_currency="GBP",
            ),
        )

    except lu.ApiException as e:

        print(json.loads(e.body)["title"])


def build_equally_weighted_model_portfolio(portfolio_code, portfolio_scope, df, max_stocks=20):

    create_reference_portfolio(portfolio_code, portfolio_scope)

    instruments = df.head(max_stocks)["lusid_instrument_id"].to_list()

    instrument_count = len(instruments)

    weights = 100 / instrument_count

    constituents = [
        lm.ReferencePortfolioConstituentRequest(
            instrument_identifiers={"Instrument/default/LusidInstrumentId": i},
            weight=weights,
            currency="USD",
        )
        for i in instruments
    ]

    # Create our request to add our constituents
    constituents_request = lm.UpsertReferencePortfolioConstituentsRequest(
        effective_from="2020-01-01",
        weight_type="Periodical",
        period_type="Quarterly",
        period_count=1,
        constituents=constituents,
    )

    # Call LUSID to upsert our constituents into our reference portfolio
    response = reference_portfolios_api.upsert_reference_portfolio_constituents(
        scope=portfolio_scope,
        code=portfolio_code,
        upsert_reference_portfolio_constituents_request=constituents_request,
    )

    return response


def get_model_portfolio(scope, code):

    constituent_response = reference_portfolios_api.get_reference_portfolio_constituents(
        scope,
        code,
        property_keys=[
            "Instrument/default/Name",
            "Instrument/DEI/TotalDeiScore",
            "Instrument/DEI/ExecutiveDeiScore",
            "Instrument/DEI/BoardDeiScore",
            "Instrument/DEI/GenderDeiScore",
            "Instrument/DEI/PctDistributionOfCaucasianExecutives",
        ],
    )

    constituent_values = []

    for item in constituent_response.constituents:

        currency = item.currency
        weight = item.weight
        name = item.properties["Instrument/default/Name"].value.label_value
        board_dei_score = item.properties[
            "Instrument/DEI/BoardDeiScore"
        ].value.metric_value.value
        executive_dei_score = item.properties[
            "Instrument/DEI/ExecutiveDeiScore"
        ].value.metric_value.value
        gender_dei_score = item.properties[
            "Instrument/DEI/GenderDeiScore"
        ].value.metric_value.value
        total_dei_score = item.properties[
            "Instrument/DEI/TotalDeiScore"
        ].value.metric_value.value

        constituent_values.append(
            [
                name,
                weight,
                currency,
                board_dei_score,
                executive_dei_score,
                gender_dei_score,
                total_dei_score,
            ]
        )

        columns = [
            "name",
            "weight",
            "currency",
            "board_dei_score",
            "executive_dei_score",
            "gender_dei_score",
            "total_dei_score",
        ]

    return pd.DataFrame(constituent_values, columns=columns)
