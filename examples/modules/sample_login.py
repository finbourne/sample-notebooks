import lusid
import lusid.models as models
import os
import json
from urllib.request import pathname2url
import requests
from collections import UserString
from datetime import datetime, timedelta, time


class RefreshingToken(UserString):

    def __init__(self):

        token_data = {
            "expires": datetime.now(),
            "current_access_token": ''
        }

        current_access_token = ''

        def get_token():
            if token_data['expires'] <= datetime.now():
                with open("./../access_token.txt", "r") as access_token_file:
                    token_data['current_access_token'] = access_token_file.read()

                token_data['expires'] = datetime.now() + timedelta(seconds=120)

            return token_data['current_access_token']

        self.access_token = get_token

    def __getattribute__(self, name):
        token = object.__getattribute__(self, 'access_token')()
        if name == 'data':
            return token
        return token.__getattribute__(name)


def authenticate_secrets():
    class LusidApi():

        def __init__(self, client):
            self.aggregation = lusid.AggregationApi(client)
            self.metadata = lusid.ApplicationMetadataApi(client)
            self.corporate_action_sources = lusid.CorporateActionSourcesApi(client)
            self.data_types = lusid.DataTypesApi(client)
            self.derived_transaction_portfolios = lusid.DerivedTransactionPortfoliosApi(client)
            self.instruments = lusid.InstrumentsApi(client)
            self.login = lusid.InstrumentsApi(client)
            self.portfolio_groups = lusid.PortfolioGroupsApi(client)
            self.portfolios = lusid.PortfoliosApi(client)
            self.property_definitions = lusid.PropertyDefinitionsApi(client)
            self.quotes = lusid.QuotesApi(client)
            self.reconciliations = lusid.ReconciliationsApi(client)
            self.reference_portfolios = lusid.ReferencePortfolioApi(client)
            self.results = lusid.ResultsApi(client)
            self.schemas = lusid.SchemasApi(client)
            self.scopes = lusid.ScopesApi(client)
            self.search = lusid.SearchApi(client)
            self.system_configuration = lusid.SystemConfigurationApi(client)
            self.transaction_portfolios = lusid.TransactionPortfoliosApi(client)
            self.cut_labels = lusid.CutLabelDefinitionsApi(client)

    environment = os.getenv("FBN_DEPLOYMENT_ENVIRONMENT", None)

    if environment == "JupyterNotebook":
        api_url = os.getenv("FBN_LUSID_API_URL", None)
        if api_url is None:
            raise KeyError("Missing FBN_LUSID_API_URL environment variable, please set it to the LUSID base API url")
        api_factory = lusid.utilities.ApiClientFactory(
            token=RefreshingToken(),
            api_url=api_url,
            app_name="LusidJupyterNotebook")
        return api_factory

    dir_path = os.path.dirname(os.path.realpath(__file__))
    secrets_path = os.path.join(dir_path, "../secrets.json")

    api_factory = lusid.utilities.ApiClientFactory(api_secrets_filename=secrets_path)

    return api_factory