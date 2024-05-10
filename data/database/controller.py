from datetime import datetime

import pandas as pd
from sqlalchemy.orm import sessionmaker
from data.database.schema import FXTickData
from data.database import SQLALCHEMY_DATABASE_URL
from sqlalchemy import create_engine, text, funcfilter, func, select, Integer, extract, cast, DateTime, String, and_


class TickDataController:
    def __init__(self):
        self.engine = create_engine(SQLALCHEMY_DATABASE_URL)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def add_ticks(self, ticks:list, pair:str):
        """
        Add a batch of tick data to the database.

        Args:
            ticks (list): A list of dictionaries where each dictionary represents a tick data record.
                          Each dictionary should contain keys 'currency_pair', 'bid', and 'ask'.
        """
        for tick in ticks:
            tick_record = FXTickData(currency_pair=pair, **tick)
            self.session.add(tick_record)

        self.session.commit()

    def close_session(self):
        self.session.close()

    def get_from_sql(self, time_frame:int,start_datetime:float, pair:str):
        tf = time_frame

        subquery = select(
            (func.floor(FXTickData.timestamp / (60 * tf)) * 60 * tf).label("time"),
            FXTickData.ask,
            FXTickData.bid
        ).where(
            and_(
                FXTickData.currency_pair == pair,
                FXTickData.timestamp >= start_datetime
            )
        ).order_by(FXTickData.timestamp).alias("subquery")

        query_a = select(
            subquery.c.time,
            subquery.c.ask,
            subquery.c.bid,
            func.first_value(subquery.c.ask).over(partition_by=subquery.c.time).label("fist_ask"),
            func.first_value(subquery.c.bid).over(partition_by=subquery.c.time).label("fist_bid"),
            func.last_value(subquery.c.ask).over(partition_by=subquery.c.time).label("last_ask"),
            func.last_value(subquery.c.bid).over(partition_by=subquery.c.time).label("last_bid"),
        ).subquery()

        query_b=select(query_a.c.time,
                 (func.max(query_a.c.fist_ask)+func.max(query_a.c.fist_bid))/2,
                 func.max(query_a.c.ask),
                 func.min(query_a.c.bid),
                 (func.max(query_a.c.last_ask)+func.max(query_a.c.last_bid))/2).group_by(query_a.c.time)
        data = self.session.execute(query_b).fetchall()

        df_out = pd.DataFrame(data, columns=['datetime', 'Open', 'High','Low','Close'])
        df_out.set_index('datetime', inplace=True)
        return df_out

    def get_from_pd(self, time_frame:int,start_datetime:float, pair:str):
        tf = time_frame
        query = select(
            (func.floor(FXTickData.timestamp / (60 * tf)) * 60 * tf).label("time"),
            FXTickData.ask,
            FXTickData.bid
        ).where(
            and_(
                FXTickData.currency_pair == pair,
                FXTickData.timestamp >= start_datetime
            )
        ).order_by(FXTickData.timestamp)

        data = self.session.execute(query).fetchall()
        # Convert the result to a DataFrame
        df = pd.DataFrame(data, columns=['datetime', 'ask', 'bid'])

        # Group by datetime and aggregate the data
        agg_functions = {
            'ask': ['max', 'first', 'last'],
            'bid': ['min', 'first', 'last']
        }
        grouped_data = df.groupby('datetime').agg(agg_functions)

        # Calculate OHLC values efficiently
        df_out = pd.DataFrame({
            'Open': (grouped_data[('ask', 'first')] + grouped_data[('bid', 'first')]) / 2,
            'High': grouped_data[('ask', 'max')],
            'Low': grouped_data[('bid', 'min')],
            'Close': (grouped_data[('ask', 'last')] + grouped_data[('bid', 'last')]) / 2
        })

        return df_out

    def get_from(self, time_frame:int,start_datetime:float, pair:str):
        return self.get_from_sql(time_frame, start_datetime, pair)

    def get_last_date(self, pair):
        last_date = (
            self.session.query(func.max(FXTickData.timestamp))
            .filter(FXTickData.currency_pair == pair)
            .scalar()
        )
        return last_date



if __name__ == '__main__':
    from time import time
    tick_data_controller = TickDataController()
    d=datetime(2024,4,28,23).timestamp()
    tf=5
    pair = "EURUSD"

    t0=time()
    c1 = tick_data_controller.get_from_pd(tf,d,pair)
    t1=time()
    c2 = tick_data_controller.get_from_sql(tf,d, pair)
    t2=time()

    print(c1)
    print(c2)
    print(all(c1==c2))
    print("pd fun: ",t1-t0)
    print("sql fun: ",t2-t1)
    print((tick_data_controller.get_last_date(pair)))