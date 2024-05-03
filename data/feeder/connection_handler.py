import MetaTrader5 as mt5


class Mt5Connection:
    def __init__(self):
        self.conn = mt5
        self.is_connected = self.conn.initialize()










if __name__ == '__main__':
    from datetime import datetime, timedelta
    b=mt5.initialize()
    print(b)
    t=mt5.copy_ticks_from("EURUSD",datetime.now()-timedelta(days=5),2**31-1,mt5.COPY_TICKS_ALL)
    print((t))