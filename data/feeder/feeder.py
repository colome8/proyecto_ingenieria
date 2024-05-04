from sqlalchemy import desc
from tqdm import tqdm
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError
import MetaTrader5 as mt5
from sqlalchemy.orm import sessionmaker

#TODO: Object with the loop that gets realtime data and uses controller to insert the data, and get cached data


class Feeder:
    def __init__(self):
        self.mt5 = mt5
        if not self.mt5.initialize():
            print("Failed to connect to MetaTrader 5!")
            quit()

    def get_most(self, pair):
        response = self.mt5.copy_ticks_from(pair, datetime.today()-timedelta(days=5),2**31-1, mt5.COPY_TICKS_ALL)
        return [{'timestamp':datetime.fromtimestamp(tick[0]),'bid':tick[1], 'ask':tick[2]} for tick in response]
"""
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

"""

def main():
    f = Feeder()
    t=f.get_most("EURUSD")
    print(len(t))
    print(t[0],t[-1])

if __name__ == '__main__':
    main()