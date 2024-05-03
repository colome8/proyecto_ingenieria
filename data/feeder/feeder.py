from sqlalchemy import desc
from tqdm import tqdm
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError
import MetaTrader5 as mt5
from sqlalchemy.orm import sessionmaker
from data.database.schema import *

#TODO: Object with the loop that gets realtime data and uses controller to insert the data, and get cached data

class Feeder:
    def _init_(self):
        if not mt5.initialize():
            print("Failed to connect to MetaTrader 5!")
            quit()
        self.mt5 = mt5
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def fast_feed_ticks_range(self, symbol, date_from: datetime = datetime.now() - timedelta(days=5),
                              date_to: datetime = datetime.now()):
        ticks = mt5.copy_ticks_range(symbol, date_from, date_to, mt5.COPY_TICKS_ALL)
        print(ticks)
        if ticks is not None:
            tick_count = len(ticks)
            with self.SessionLocal() as session:
                with tqdm(total=tick_count, desc="Feeding ticks") as pbar:
                    for tick in ticks:
                        if tick:
                            tick_data = FXTickData(currency_pair=symbol, bid=tick[1], ask=tick[2],
                                                   timestamp=datetime.fromtimestamp(tick[0]))
                            session.add(tick_data)
                            pbar.update(1)
                    session.commit()
        elif date_from < date_to:
            self.fast_feed_ticks_range(symbol, date_from + timedelta(days=1), date_to)
    def feed_ticks_range(self, symbol, date_from: datetime = datetime.now() - timedelta(days=1),
                         date_to: datetime = datetime.now(), motive: str = "Feeding ticks", disable_tqdm: bool = False):
        ticks = mt5.copy_ticks_range(symbol, date_from, date_to, mt5.COPY_TICKS_ALL)
        if ticks is not None:
            tick_count = len(ticks)
            with self.SessionLocal() as session:
                with tqdm(total=tick_count, desc=motive, disable=disable_tqdm) as pbar:
                    for tick in ticks:
                        if tick:
                            tick_data = FXTickData(currency_pair=symbol, bid=tick[1], ask=tick[2],
                                                   timestamp=datetime.fromtimestamp(tick[0]))
                            try:
                                session.add(tick_data)
                                session.commit()
                                pbar.update(1)
                            except IntegrityError:
                                session.rollback()
                                pbar.update(1)
                                continue

        elif date_from < date_to:
            self.feed_ticks_range(symbol, date_from + timedelta(days=1), date_to)

    def update_ticks(self, symbol, disable_tqdm: bool = False):
        with self.SessionLocal() as session:
            latest_date = session.query(FXTickData).filter_by(currency_pair=symbol).order_by(
                desc('timestamp')).first().timestamp
        self.feed_ticks_range(symbol, latest_date, motive=f"Updating ticks from {latest_date}",
                              disable_tqdm=disable_tqdm)



def main():
    f = Feeder()

