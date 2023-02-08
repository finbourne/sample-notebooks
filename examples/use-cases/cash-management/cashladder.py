import lusid
import lusid.models as models
from datetime import datetime
from lusidjam import RefreshingToken
from lusidtools.pandas_utils.lusid_pandas import lusid_response_to_data_frame
import pandas as pd
import numpy as np
import os
import pytz
from datetime import timedelta

# Authenticate our user and create our API client
# secrets_path = os.getenv("FBN_SECRETS_PATH")
secrets_path = os.getenv("HOME") + "/secrets/fbn-local.json"

# Initiate an API Factory which is the client side object for interacting with LUSID APIs
api_factory = lusid.utilities.ApiClientFactory(
    token=RefreshingToken(),
    api_secrets_filename=secrets_path,
    app_name="LusidJupyterNotebook",
)


def get_cash_ladder(start_date, portfolio_code, currency, scope):
    
    transaction_portfolio_api = api_factory.build(lusid.api.TransactionPortfoliosApi)
    
    def get_holdings_df():
    
        rename_cols = {
        "properties.Holding/default/SourcePortfolioId.value.label_value": "Portfolio",
        "holding_type": "HoldingType",
        "units": "CashImpact",
        "settled_units": "SettledUnits",
        "cost.currency": "Currency",
        "transaction.transaction_id": "TransactionId",
        "transaction.type": "TransactionType",
        "instrument_uid": "HoldingsInstrumeny",
        "transaction.instrument_uid": "CommitmentInstrument",
        "transaction.settlement_date": "SettlementDate"}

        cols = list(rename_cols.values())
        
        holdings_df = lusid_response_to_data_frame(
        api_factory.build(lusid.api.TransactionPortfoliosApi).get_holdings(
            scope=scope, code=portfolio_code, 
            effective_at=start_date
        )
        ).rename(columns=rename_cols)
        
        holdings_df = holdings_df[cols][holdings_df["HoldingType"] != "P"]
        holdings_df["SettlementDate"]  = pd.to_datetime(holdings_df["SettlementDate"], utc=True)
        
        holdings_df = holdings_df[holdings_df["Currency"] == currency]
        
        
        return holdings_df
    
    
    def add_daily_balances():
        
        holdings_df = get_holdings_df()
        period_opening_balance_value = int(holdings_df[holdings_df["HoldingType"]=="B"]["CashImpact"].to_list()[0])
        
        intraday_df = holdings_df[["SettlementDate", "CashImpact"]].groupby(["SettlementDate"], as_index=False).sum()
        day_1 = pd.Series([ intraday_df["SettlementDate"][0] - timedelta(days=1), int(period_opening_balance_value)], index = intraday_df.columns)
        intraday_df = intraday_df.append(day_1, ignore_index=True).sort_values("SettlementDate")
        
        intraday_df["ClosingBalance"] = intraday_df["CashImpact"].cumsum()
        intraday_df  = intraday_df.rename(columns={"CashImpact": "IntradayActivity"})
        intraday_df["OpeningBalance"] = intraday_df["ClosingBalance"].shift(1)
        intraday_df = intraday_df[["SettlementDate", "OpeningBalance", "IntradayActivity", "ClosingBalance"]]
        
        opening_balance_df = intraday_df[["SettlementDate", "OpeningBalance"]].reset_index(drop=True).rename(columns={"OpeningBalance": "CashImpact"})
        opening_balance_df["CashLadderStatus"] = "SOD Balance"
        opening_balance_df["ReportOrder"] = 0
        opening_balance_df.iat[0,1] = period_opening_balance_value
        
        closing_balance_df = intraday_df[["SettlementDate", "ClosingBalance"]].rename(columns={"ClosingBalance": "CashImpact"})
        closing_balance_df["CashLadderStatus"] = "EOD Balance"
        closing_balance_df["ReportOrder"] = 2
        closing_balance_df
        
        cash_ladder_no_trades = holdings_df.append(opening_balance_df).append(closing_balance_df)
        portfolio = cash_ladder_no_trades["Portfolio"].to_list()[0]
        cash_ladder_no_trades["Portfolio"] = portfolio[portfolio.rfind("/") + 1:]
        return cash_ladder_no_trades
    
    
    def add_trades_to_balance():
        
        trades_unedited = add_daily_balances()["TransactionId"].to_list()
        trades = [trade for trade in trades_unedited if str(trade)!="nan"]
        trades_for_filter = f"{trades}"[1:-1]
        
        trades_response = transaction_portfolio_api.get_transactions(scope=scope,
                                           code=portfolio_code,
                                          filter = f"transactionId in ({trades_for_filter})",
                                          property_keys = ["Instrument/default/Name",
                                                          f"Transaction/{scope}/TradeStatus"]
                                          
                                          )
        
        rename_cols = {
             f"properties.Transaction/{scope}/TradeStatus.value.label_value": "TradeStatus",
                "transaction_id": "TransactionId",
                "properties.Instrument/default/Name.value.label_value": "InstrumentName"}
    


        cols = list(rename_cols.values())
        
        trades_df = lusid_response_to_data_frame(trades_response).rename(columns=rename_cols)
        trades_df = trades_df[cols]
        cash_ladder = add_daily_balances().merge(trades_df, how="outer")
        
        cash_ladder["CashLadderStatus"] = np.where(cash_ladder["HoldingType"] == "B" ,
                                           "SOD Balance",
                                           np.where(
                                               pd.isnull(cash_ladder["CashLadderStatus"]),
                                            "Cash impact from a " + cash_ladder['TransactionType'] + " transaction",
                                           cash_ladder["CashLadderStatus"]
                                           ))
        
        
        cash_ladder["ReportOrder"] = np.where(cash_ladder["HoldingType"] == "B" ,
                                           0,
                                           np.where(
                                               pd.notnull(cash_ladder["TransactionId"]) & pd.isnull(cash_ladder["ReportOrder"]) ,
                                            1,
                                           cash_ladder["ReportOrder"]))
        
        cash_ladder["SettlementDate"] = np.where(cash_ladder["HoldingType"] == "B",
                                         pd.to_datetime(start_date, utc=True),
                                         cash_ladder["SettlementDate"])

        cash_ladder["TransactionId"] = np.where(pd.isnull(cash_ladder["TransactionId"]),
                                                 "",
                                                 cash_ladder["TransactionId"])
        
        cash_ladder["InstrumentName"] = np.where(pd.isnull(cash_ladder["InstrumentName"]),
                                                 "",
                                                 cash_ladder["InstrumentName"])

        cash_ladder["TradeStatus"] = np.where(pd.isnull(cash_ladder["TradeStatus"]),
                                                 "",
                                                 cash_ladder["TradeStatus"])

        cash_ladder = cash_ladder.sort_values(["SettlementDate", "ReportOrder"])
        cash_ladder["ReportRunTime"] = datetime.now().strftime(format="%X")
        cash_ladder["SettlementDate"] = cash_ladder["SettlementDate"].apply(lambda x: x.strftime(format="%Y-%m-%d"))
        
        cols_for_report = [
            "ReportRunTime",
            "SettlementDate",
            "Currency",
            "Portfolio",
            "CashLadderStatus",
            "InstrumentName",
            "CashImpact",
            "TransactionId",
            "TradeStatus"
        
        ]

        cash_ladder_report = cash_ladder[cols_for_report]
        cash_ladder_report.loc[:,"Currency"] = currency
        cash_ladder_report = cash_ladder_report.reset_index(drop=True).drop_duplicates()
        
        
        return cash_ladder_report   
    
    return add_trades_to_balance()
    