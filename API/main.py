import MetaTrader5 as mt5
from datetime import datetime, timedelta
import time
if not mt5.initialize():
    print("webos")

d = datetime.now() - timedelta(minutes=1)
ticks = mt5.copy_ticks_from('EURUSD', d, 10, mt5.COPY_TICKS_ALL)[-1]
while True:
    d = datetime.fromtimestamp((ticks[5]) / 1000)
    ticks = mt5.copy_ticks_from('EURUSD', d, 10, mt5.COPY_TICKS_ALL)[-1]
    time.sleep(1)
    print(d,ticks)
