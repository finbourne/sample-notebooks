import unittest
import os
from pathlib import Path
import pandas as pd

from lusidtools.general_utils import create_scope_id
from lusidtools.general_utils import import_file
from lusidtools.general_utils import fetch_portfolio_names
from lusidtools.general_utils import fetch_instrument_universe
from lusidtools.general_utils import fetch_instrument_market_cap
from lusidtools.general_utils.quick_func import fetch_instrument_analytics
from lusidtools.general_utils.quick_func import fetch_client_take_on_balances

from lusidtools.general_utils.quick_func import fetch_fund_accountant_daily_holdings_report
from lusidtools.general_utils.quick_func import client_transactions
from lusidtools.general_utils.quick_func import fetch_client_transactions


class TestResponseToPandasObject(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        pass

    def test_import_file(self):
        test_file = Path(__file__).parent.joinpath("data", "test_portfolio_groups.csv")
        test_df = import_file(test_file)
        self.assertTrue(len(test_df) > 1)
        self.assertIsInstance(test_df, pd.DataFrame)

    def test_fetch_portfolio_names(self):
        test_file = Path(__file__).parent.joinpath("data", "test_portfolio_groups.csv")
        portfolios_dict = fetch_portfolio_names(test_file)
        self.assertTrue(portfolios_dict["TEST_GROUP"][0], "UK_EQUITY")
        self.assertIsInstance(portfolios_dict, dict)

    def test_fetch_instrument_universe(self):
        test_file = Path(__file__).parent.joinpath("data", "test_instruments.csv")
        instrument_uni_paper = fetch_instrument_universe(test_file, paper=True)
        instrument_uni_no_paper = fetch_instrument_universe(test_file, paper=False)
        self.assertIsInstance(instrument_uni_paper, dict)
        self.assertTrue(
            instrument_uni_paper["Amazon_Nasdaq_AMZN"]["identifiers"]["Figi"],
            "BBG000BVPXP1",
        )
        self.assertIsInstance(instrument_uni_paper, dict)
        self.assertTrue(
            instrument_uni_no_paper["WPP_LondonStockEx_WPP"]["identifiers"][
                "ClientInternal"
            ],
            "imd_34536734",
        )

    def test_fetch_instrument_market_cap(self):
        test_file = Path(__file__).parent.joinpath("data", "test_market_cap.csv")
        instrument_market_cap = fetch_instrument_market_cap(test_file)
        self.assertIsInstance(instrument_market_cap, dict)
        self.assertTrue(instrument_market_cap["TEST1"], 100000)

    def test_fetch_instrument_analytics(self):
        test_file = Path(__file__).parent.joinpath("data", "test_analytics.csv")
        instrument_analytics = fetch_instrument_analytics(test_file)
        self.assertIsInstance(instrument_analytics, dict)
        self.assertTrue(instrument_analytics["AVEVA_GRP"][0], 27.84)

    def test_fetch_client_take_on_balances(self):
        test_file = Path(__file__).parent.joinpath("data", "test_analytics.csv")
        client_take_on_balances = fetch_client_take_on_balances(test_file)
        self.assertIsInstance(client_take_on_balances, dict)
        self.assertTrue(client_take_on_balances["AVEVA_GRP"][0], 27.84)

    def test_fetch_client_take_on_balances(self):
        test_file = Path(__file__).parent.joinpath("data", "test_holdings.csv")
        client_take_on_balances = fetch_client_take_on_balances(test_file)
        self.assertIsInstance(client_take_on_balances, dict)
        self.assertTrue(client_take_on_balances["client-A-strategy-balanced"]["WPP_LondonStockEx_WPP"]["quantity"], 2956000)

    def test_fetch_fund_accountant_daily_holdings_report(self):
        test_file = Path(__file__).parent.joinpath("data", "test_holdings.csv")
        fund_accountant_daily_holdings_report = fetch_fund_accountant_daily_holdings_report(test_file)
        self.assertIsInstance(fund_accountant_daily_holdings_report, dict)
        self.assertTrue(fund_accountant_daily_holdings_report["client-A-strategy-balanced"]["WPP_LondonStockEx_WPP"]["quantity"], 2956000)

    def test_client_transactions(self):
        test_file = Path(__file__).parent.joinpath("data", "test_transactions.csv")
        instrument_universe = {'WPP_LondonStockEx_WPP': {'identifiers': {"LUID": 'LUID_TEST12345'}}}
        client_transactions_dict = client_transactions(test_file, instrument_universe)[0]
        self.assertIsInstance(client_transactions_dict, dict)
        self.assertTrue(client_transactions_dict["client-A-strategy-balanced"]["tid_35b77104-7c72-4515-af2b-d22bb45e6edd"]["instrument_uid"], "LUID_TEST12345")

    def test_fetch_client_transactions(self):
        test_file = Path(__file__).parent.joinpath("data", "test_strategy_transactions.csv")
        client_transactions = fetch_client_transactions(test_file, 1)
        self.assertIsInstance(client_transactions, pd.DataFrame)
        self.assertTrue(client_transactions["transaction_id"][0], "tid_329432525234324")
