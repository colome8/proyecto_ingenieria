from datetime import datetime, timedelta
import MetaTrader5 as mt5
import time


class Feeder:
    def __init__(self, pair:str, cache_size:int = 100):
        self.mt5 = mt5
        if not self.mt5.initialize():
            print("Failed to connect to MetaTrader 5!")
            quit()
        self.pair = pair
        self.last_tick = {'timestamp': datetime.today() - timedelta(days=5)}

    def connect(self):
        if not self.mt5.initialize():
            print("Failed to connect to MetaTrader 5!")

    @staticmethod
    def parse(response):
        return [{'timestamp':datetime.fromtimestamp(tick[0]),'bid':tick[1], 'ask':tick[2]} for tick in response]
        

    def get_ticks(self):
        last_date = self.last_tick.get('timestamp')
        response = self.mt5.copy_ticks_from(self.pair,last_date,2**31-1, mt5.COPY_TICKS_ALL)
        if response is None:
            self.connect()
            return None
        data = self.parse(response)
        if self.last_tick == data[-1]:
            return None
        self.last_tick = data[-1]
        return data[1:]







if __name__ == '__main__':
    f = Feeder("EURUSD")
    t = f.get_ticks()
    print(t[-1])
    while True:
        if t := f.get_ticks():
            print(t)
        # time.sleep(0.01)