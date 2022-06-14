import pandas as pd
import lusid


# Create data frame skeleton
def new_data_frame():
    return pd.DataFrame(columns=[
        "Currency",
        "Date",
        "Activity",
        "Value"
    ])


# Add open values
def add_open_row(element, record):
    df = new_data_frame()
    df = df.append({
        "Currency": element.currency,
        "Date": record.effective_date,
        "Activity": "Open",
        "Value": record.open
    }, ignore_index=True)

    return df


# Add close values
def add_close_row(element, record, df):
    df = df.append({
        "Currency": element.currency,
        "Date": record.effective_date,
        "Activity": "Close",
        "Value": record.close
    }, ignore_index=True)

    return df


# Add activites
def add_activity_row(element, record, df, activity, value):
    df = df.append({
        "Currency": element.currency,
        "Date": record.effective_date,
        "Activity": activity,
        "Value": value
    }, ignore_index=True)

    return df


def cashladder_to_df(response) -> pd.DataFrame:
    """
    Formats a LUSID cash ladder response to a pandas DataFrame.
    Parameters
    ----------
    response

    Returns
    -------
    pd.DataFrame
    """

    base_df = new_data_frame()

    for element in response.values:
        shks = {shk: value.value.label_value for shk, value in element.sub_holding_keys.items()}

        for record in element.records:
            working_df = add_open_row(element, record)

            for activity, value in record.activities.items():
                working_df = add_activity_row(element, record, working_df, activity, value)
            working_df = add_close_row(element, record, working_df)

            for k, v in shks.items():
                working_df[k] = v
            base_df = base_df.append(working_df, ignore_index=True)

    return base_df


def cash_flow_response_to_df(
        portfolio_cash_flows_response: lusid.ResourceListOfPortfolioCashFlow,
        sum_by_date: bool = True
) -> pd.DataFrame:
    """
   Takes a LUSID response from 'GetPortfolioCashFlows' and formats pays and receives into a dataframe, adding the net
   column.
    """

    def select_cols(
            df: pd.DataFrame,
            filter_col: str,
            filter_value: str,
            cols_to_keep: list,
    ) -> pd.DataFrame:
        return df[df[filter_col] == filter_value][cols_to_keep]

    # Extract cash payment data from cash flow response
    cash_flows_dict = portfolio_cash_flows_response.to_dict()
    cash_flow_data = pd.json_normalize(cash_flows_dict["values"])

    # Split pays and receives and handle -ve signage for pay outflows
    pay_data = select_cols(
        cash_flow_data,
        "diagnostics.PayReceive",
        "Pay",["payment_date", "amount", "source_transaction_id"]
    )
    pay_data["amount"] = pay_data["amount"].apply(lambda x: -1 * x)
    pay_data.rename(columns={"amount": "payAmount"}, inplace=True)
    rec_data = select_cols(
        cash_flow_data,
        "diagnostics.PayReceive",
        "Receive",
        ["payment_date", "amount", "source_transaction_id"]
    )
    rec_data.rename(columns={"amount": "receiveAmount"}, inplace=True)

    # Merge on payment date and ignore join dupes
    merged_df = pay_data.merge(rec_data, on=["payment_date", "source_transaction_id"])
    merged_df.drop_duplicates(subset=["payment_date", "source_transaction_id"], keep="first", inplace=True,
                              ignore_index=True)

    # Add net flows and reduce index to dates
    merged_df['netAmount'] = merged_df['payAmount'] + merged_df['receiveAmount']
    merged_df["payment_date"] = merged_df["payment_date"].apply(lambda x: x.date())
    merged_df.set_index(keys="payment_date", inplace=True)

    # Aggregate sub-holdings
    if sum_by_date:
        merged_df = merged_df.groupby(merged_df.index).sum()

    return merged_df

