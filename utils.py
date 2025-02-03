import pandas as pd

def convert_dt_index(df:pd.DataFrame) -> pd.DataFrame:
    '''Convert the index of a DataFrame from datetime to date'''
    df.index = pd.to_datetime(df.index).date
    return df

def color_returns(val):
    color = "green" if val > 0 else "red"
    return f"color: {color}"