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
            self.analytics_stores = lusid.AnalyticsStoresApi(client)
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
        config = lusid.Configuration()
        config.access_token = RefreshingToken()
        api_url = os.getenv("FBN_LUSID_API_URL", None)
        if api_url is None:
            raise KeyError("Missing FBN_LUSID_API_URL environment variable, please set it to the LUSID base API url")
        config.host = api_url
        client = lusid.ApiClient(config)
        return LusidApi(client)

    # Load our configuration details from the environment variables
    token_url = os.getenv("FBN_TOKEN_URL", None)
    api_url = os.getenv("FBN_LUSID_API_URL", None)
    username = os.getenv("FBN_USERNAME", None)
    password_raw = os.getenv("FBN_PASSWORD", None)
    client_id_raw = os.getenv("FBN_CLIENT_ID", None)
    client_secret_raw = os.getenv("FBN_CLIENT_SECRET", None)

    # If any of the environmental variables are missing use a local secrets file
    if token_url is None or username is None or password_raw is None or client_id_raw is None \
            or client_secret_raw is None or api_url is None:

        dir_path = os.path.dirname(os.path.realpath(__file__))
        with open(os.path.join(dir_path, "../secrets.json"), "r") as secrets:
            config = json.load(secrets)

        token_url = os.getenv("FBN_TOKEN_URL", config["api"]["tokenUrl"])
        username = os.getenv("FBN_USERNAME", config["api"]["username"])
        password = pathname2url(os.getenv("FBN_PASSWORD", config["api"]["password"]))
        client_id = pathname2url(os.getenv("FBN_CLIENT_ID", config["api"]["clientId"]))
        client_secret = pathname2url(os.getenv("FBN_CLIENT_SECRET", config["api"]["clientSecret"]))
        api_url = os.getenv("FBN_LUSID_API_URL", config["api"]["apiUrl"])

    else:
        password = pathname2url(password_raw)
        client_id = pathname2url(client_id_raw)
        client_secret = pathname2url(client_secret_raw)

    # Prepare our authentication request
    token_request_body = ("grant_type=password&username={0}".format(username) +
                          "&password={0}&scope=openid client groups".format(password) +
                          "&client_id={0}&client_secret={1}".format(client_id, client_secret))
    headers = {"Accept": "application/json", "Content-Type": "application/x-www-form-urlencoded"}

    # Make our authentication request
    okta_response = requests.post(token_url, data=token_request_body, headers=headers)

    # Ensure that we have a 200 response code
    assert okta_response.status_code == 200

    # Retrieve our api token from the authentication response
    api_token = okta_response.json()["access_token"]

    # Initialise our API client using our token so that we can include it in all future requests
    config = lusid.Configuration()
    config.access_token = api_token
    config.host = api_url
    client = lusid.ApiClient(config)

    return LusidApi(client)