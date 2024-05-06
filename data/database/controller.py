import datetime

import pandas as pd
from sqlalchemy.orm import sessionmaker
from data.database.schema import FXTickData
from data.database.settings import SQLALCHEMY_DATABASE_URL, pair
from sqlalchemy import create_engine, text, funcfilter, func, select, Integer, extract, cast, DateTime, String, and_


class TickDataController:
    def __init__(self):
        self.engine = create_engine(SQLALCHEMY_DATABASE_URL)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def add_ticks(self, ticks:list):
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

    def get_from_sql(self, time_frame:int,start_datetime:datetime.datetime):
        tf = time_frame

        subquery = select(
            func.datetime(func.floor(func.extract('epoch', FXTickData.timestamp) / (60 * tf)) * 60 * tf,
                          'unixepoch').label("time"),
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
        t0=time()
        data = self.session.execute(query_b).fetchall()
        t1=time()
        print("sql fetch: ",t1-t0)
        df_out = pd.DataFrame(data, columns=['datetime', 'Open', 'High','Low','Close'])
        df_out.set_index('datetime', inplace=True)
        df_out.index = pd.to_datetime(df_out.index)
        return df_out

    def get_from_pd(self, time_frame:int,start_datetime:datetime.datetime):
        tf = time_frame
        query = select(
            func.datetime(func.floor(func.extract('epoch', FXTickData.timestamp) / (60 * tf)) * 60 * tf,
                          'unixepoch').label("time"),
            FXTickData.ask,
            FXTickData.bid
        ).where(
            and_(
                FXTickData.currency_pair == pair,
                FXTickData.timestamp >= start_datetime
            )
        ).order_by(FXTickData.timestamp)

        t0=time()
        data = self.session.execute(query).fetchall()
        t1 = time()
        print("pd fetch: ",t1 - t0)

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
        df_out.index = pd.to_datetime(grouped_data.index)

        return df_out

    def get_from(self, time_frame:int,start_datetime:datetime.datetime):
        return self.get_from_pd(time_frame, start_datetime)


if __name__ == '__main__':
    from time import time
    tick_data_controller = TickDataController()
    d=datetime.datetime(2024,4,28,23)
    tf=60

    t0=time()
    c1 = tick_data_controller.get_from_pd(tf,d)
    t1=time()
    c2 = tick_data_controller.get_from_sql(tf,d)
    t2=time()

    print(c1)
    print(c2)
    print(all(c1==c2))
    print("pd fun: ",t1-t0)
    print("sql fun: ",t2-t1)