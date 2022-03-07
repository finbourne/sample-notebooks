import pandas as pd

# Create data frame skeleton
def new_data_frame():
    return pd.DataFrame(columns = [
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



# Read response to data frame
def cashladder_to_df(response):
    
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

def clean_df_cols(df: pd.DataFrame, exclusions: list=[], inclusions: list=[]):
    """"
    Takes a dataframe, and cleans it based on the given lists of strings, where if a column name contains an exclusion
    string in the column name it will be dropped, and the reverse is true for an inclusion.

    Parameters
    ----------
    df: pd.DataFrame
    Input pandas DataFrame to clean
    exclusions: list
    List of strings that if contained in any column names are dropped from the dataframe
    inclusions: list
    List of strings that if not contained in any column names are dropped from the dataframe

    Returns
    ----------
    pd.DataFrame
    """

    cols_to_drop = [col for col in df.columns for exclusion in exclusions if exclusion in col]
    new_df = df.drop(columns=cols_to_drop)

    if inclusions:
        cols_to_include = [col for col in new_df.columns for inclusion in inclusions if inclusion in col]
        new_df = new_df[cols_to_include]

    return new_df

def reorder_df_cols(df, order_tags=["start", "gains", "carry", "flows", "end"]):

    # Order columns based on order tags, store untagged cols
    ordered_cols = [col for tag in order_tags for col in df.columns if tag in col]
    other_cols = [col for col in df.columns if col not in ordered_cols]

    # Create new cols with other cols set at the head and reorder the dataframe
    new_order_cols = other_cols + ordered_cols
    new_df = df[new_order_cols]

    return new_df
