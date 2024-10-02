import requests
from requests.exceptions import HTTPError
from urllib.parse import urlparse
from pydantic import BaseModel, root_validator
import json

from lusid.utilities import ApiClientFactory


class RebalanceTargetWeight(BaseModel):
    reference_portfolio_scope: str
    reference_portfolio_code: str
    weight: int
    link: str
    link_value: str

    def generate_target_weight_payload_dict(self):
        rebalance_mappings_payload_dict = {
            "referencePortfolioId": {
                "scope": self.reference_portfolio_scope,
                "code": self.reference_portfolio_code
            },
            "weight": self.weight,
            "link": self.link,
            "linkValue": self.link_value
        }
        return rebalance_mappings_payload_dict


class RebalanceMappingsConfiguration(BaseModel):
    name: str
    recipe_scope: str
    recipe_code: str
    rebalance_configuration_scope: str
    rebalance_configuration_code: str
    # rebalance_configuration_user_id: str
    benchmark_scope: str
    benchmark_code: str
    link_type: str


class _RebalanceMappingsPayload(BaseModel):
    configuration: RebalanceMappingsConfiguration
    target_weights: list[RebalanceTargetWeight]

    @root_validator
    def check_weights_sum_to_100(cls, values):
        target_weights = values.get('target_weights')

        total_weight = sum(weight.weight for weight in target_weights)
        if total_weight != 100:
            raise ValueError(
                f"The total weight must sum to 100, got {total_weight}")
        return values

    def generate_rebalance_mappings_configuration_dict(self):
        rebalance_mappings_payload_dict = {
            "name": self.configuration.name,
            "recipeId": {
                "scope": self.configuration.recipe_scope,
                "code": self.configuration.recipe_code
            },
            "rebalanceConfigurationId": {
                "scope": self.configuration.rebalance_configuration_scope,
                "code": self.configuration.rebalance_configuration_code
            },
            # "rebalanceConfigurationUserId": self.configuration.rebalance_configuration_user_id,
            "benchmarkId": {
                "scope": self.configuration.benchmark_scope,
                "code": self.configuration.benchmark_code
            },
            "linkType": self.configuration.link_type,
            "targetWeights": [target_weight.generate_target_weight_payload_dict()
                              for target_weight in self.target_weights]
        }
        return rebalance_mappings_payload_dict


class RebalanceMappingsApi():
    # initialise the auth by accepting and intialised ApiClientFactory
    def __init__(self, authorized_api_factory: ApiClientFactory):
        host_url = authorized_api_factory.api_client.configuration.host
        parsed_host_url = urlparse(host_url)
        self.client_domain = parsed_host_url.netloc
        self.access_token = authorized_api_factory.api_client.configuration.access_token.__getattribute__(
            'data')
        self.endpoint = f"https://{self.client_domain}/app"

    def get_all_rebalance_mappings(self):
        def get_all_rebalance_mappings_http():
            try:
                url = f"{self.endpoint}/api/rebalance/mappings/"
                headers = {"Authorization": f"Bearer {self.access_token}"}
                res = requests.get(url, headers=headers)
                res.raise_for_status()
            except HTTPError as http_err:
                raise Exception(f'HTTP error occurred: {http_err}')
            except Exception as err:
                raise Exception(f'Other error occurred: {err}')
            else:
                if res.json() == []:
                    print('No rebalance mappings exist')
                return res.json()

        res = get_all_rebalance_mappings_http()
        return res

    # Get a dictionary of rebalance mappings that currently exist within a scope/code
    def get_rebalance_mappings_from_scope(self, scope, code, is_portfolio_group=False):
        '''
        :param scope: The scope of the transaction portfolio or group of the rebalance mapping
        :type scope: str
        :param code: The code of the transaction portfolio or group of the rebalance mapping
        :type code: str
        '''
        def get_rebalance_mappings_from_scope_http(scope, code, is_portfolio_group):
            try:
                url = f"{self.endpoint}/api/rebalance/mappings/{scope}/{code}?isPortfolioGroup={is_portfolio_group}"
                headers = {"Authorization": f"Bearer {self.access_token}"}
                res = requests.get(url, headers=headers)
                res.raise_for_status()
            except HTTPError as http_err:
                raise Exception(f'HTTP error occurred: {http_err}')
            except Exception as err:
                raise Exception(f'Other error occurred: {err}')
            else:
                return res.json()

        res = get_rebalance_mappings_from_scope_http(
            scope,
            code,
            is_portfolio_group=is_portfolio_group
        )
        return res

    # delete a rebalance mapping by scope and code
    def delete_rebalance_mappings_from_scope(self, scope, code, is_portfolio_group=False):
        '''

        :param scope: The scope of the transaction portfolio or group of the rebalance mapping
        :type scope: str
        :param code: The code of the transaction portfolio or group of the rebalance mapping
        :type code: str

        '''
        def delete_rebalance_mappings_from_scope_http(scope, code, is_portfolio_group):
            try:
                url = f"{self.endpoint}/api/rebalance/mappings/{scope}/{code}?isPortfolioGroup={is_portfolio_group}"
                headers = {"Authorization": f"Bearer {self.access_token}"}
                res = requests.delete(url, headers=headers)
                res.raise_for_status()
            except HTTPError as http_err:
                if http_err.response.status_code == 404:
                    print(f'Check that the item exists at {url}')
                raise Exception(f'HTTP error occurred: {http_err}')
            except Exception as err:
                raise Exception(f'Other error occurred: {err}')
            else:
                print(f'rebalance mappings from {url} deleted')

        raw_res = delete_rebalance_mappings_from_scope_http(
            scope,
            code,
            is_portfolio_group=is_portfolio_group
        )

    # upsert rebalance mappings as per the RebalanceMappingsPayload structure above
    def upsert_rebalance_mappings(self, scope, code,
                                  rebalance_mappings_configuration: RebalanceMappingsConfiguration,
                                  rebalance_target_weights: list[RebalanceTargetWeight],
                                  is_portfolio_group=False
                                  ):

        payload_object = _RebalanceMappingsPayload(
            configuration=rebalance_mappings_configuration,
            target_weights=rebalance_target_weights
        )

        rebalance_mappings_payload_dict = payload_object.generate_rebalance_mappings_configuration_dict()

        def upsert_rebalance_mappings_http(scope, code, rebalance_mappings_payload_dict, is_portfolio_group):
            try:
                url = f"{self.endpoint}/api/rebalance/mappings/{scope}/{code}?isPortfolioGroup={is_portfolio_group}"
                headers = {"Authorization": f"Bearer {self.access_token}"}
                res = requests.post(url, headers=headers,
                                    json=rebalance_mappings_payload_dict)
                res.raise_for_status()
            except HTTPError as http_err:
                raise Exception(f'HTTP error occurred: {http_err}')
            except Exception as err:
                raise Exception(f'Other error occurred: {err}')
            else:
                return res.json()

        res = upsert_rebalance_mappings_http(
            scope,
            code,
            rebalance_mappings_payload_dict,
            is_portfolio_group=is_portfolio_group
        )
        return res
