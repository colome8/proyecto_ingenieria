import MetaTrader5 as mt5
from datetime import datetime
import pandas as pd
import numpy as np

if not mt5.initialize():
    print('Failed')
data = mt5.copy_rates_range('EURUSD', mt5.TIMEFRAME_D1, datetime(2023, 1, 1), datetime.today())
print(data)

# timestamp / open / high / low / close / volume / npi / npi

columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'variable1', 'variable2']

# Convertir la lista de tuplas en un DataFrame
df = pd.DataFrame(data)

df['time'] = pd.to_datetime(df['time'],unit='s')

# Mostrar el DataFrame resultante
print(df.head())