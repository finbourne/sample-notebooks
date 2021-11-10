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
def response_to_df(response):
    
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
