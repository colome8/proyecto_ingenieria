
from sqlalchemy.orm import sessionmaker
from data.database.schema import FXTickData
from data.database.settings import SQLALCHEMY_DATABASE_URL, pair
from sqlalchemy import create_engine

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

if __name__ == '__main__':
    # Example usage
    ticks_data = [
        {'currency_pair': 'EURUSD', 'bid': 1.2000, 'ask': 1.2010},
        {'currency_pair': 'GBPUSD', 'bid': 1.3800, 'ask': 1.3810},
        # Add more tick data as needed
    ]

    tick_data_controller = TickDataController()
    tick_data_controller.add_ticks(ticks_data)
    tick_data_controller.close_session()
