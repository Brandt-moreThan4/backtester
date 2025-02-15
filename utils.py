import pandas as pd
import datetime as dt

def convert_dt_index(df:pd.DataFrame) -> pd.DataFrame:
    '''Convert the index of a DataFrame from datetime to date'''
    df.index = pd.to_datetime(df.index).date
    return df

def color_returns(val):
    color = "green" if val > 0 else "red"
    return f"color: {color}"


class DynamicDates:
    @classmethod
    def today(cls):
        return dt.datetime.today()

    @classmethod
    def yesterday(cls):
        return cls.today() - dt.timedelta(days=1)

    @classmethod
    def day_before_yesterday(cls):
        return cls.today() - dt.timedelta(days=2)

    @classmethod
    def prior_year_end(cls):
        return dt.datetime(cls.today().year - 1, 12, 31)

    @classmethod
    def one_year_ago(cls):
        return cls.yesterday().replace(year=cls.today().year - 1)

    @classmethod
    def three_years_ago(cls):
        return cls.yesterday().replace(year=cls.today().year - 3)

    @classmethod
    def five_years_ago(cls):
        return cls.yesterday().replace(year=cls.today().year - 5)

    @classmethod
    def ten_years_ago(cls):
        return cls.yesterday().replace(year=cls.today().year - 10)

    @classmethod
    def fifteen_years_ago(cls):
        return cls.yesterday().replace(year=cls.today().year - 15)


if __name__ == '__main__':
    print("Today:", DynamicDates.today())
    print("Yesterday:", DynamicDates.yesterday())
    print("One Year Ago:", DynamicDates.one_year_ago())
