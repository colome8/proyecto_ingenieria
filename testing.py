import asyncio
from datetime import datetime
from io import StringIO
from model.dummy_model import DummyModel
import pandas as pd
import websockets
import json
import pytz

class Client:
    def __init__(self, pair:str, timeframe:int):
        self.pair=pair
        self.timeframe=timeframe
        self.df = pd.DataFrame([])

    def get_prediction(self):
        return DummyModel.predict(self.df)
    def update_data(self,tick):
        timestamp = tick.get('timestamp')
        ask = tick.get('ask')
        bid = tick.get('bid')
        mid = (ask + bid) / 2
        if (self.df.iloc[-1].name.timestamp() + self.timeframe * 60) < timestamp:
            self.df=self.df._append(pd.Series({'Open':mid, 'High':ask,'Low':bid,'Close':mid},name=datetime.fromtimestamp(self.df.iloc[-1].name.timestamp()+self.timeframe*60,pytz.UTC)))
        else:
            self.df.iloc[-1].Close = mid
            if self.df.iloc[-1].High<ask:
                self.df.iloc[-1].High=ask
            if self.df.iloc[-1].Low>bid:
                self.df.iloc[-1].Low=bid
        print("Last value ",mid,"  Prediction: ",self.get_prediction())


    async def ws_connect(self):
        async with websockets.connect(f'ws://127.0.0.1:4444/ws/{self.pair}/{self.timeframe}', timeout=60) as connection:
            data = await connection.recv()
            df = pd.read_json(StringIO(json.loads(data)))
            self.df = df.set_index(
                pd.to_datetime(df.index, unit='s'))
            while True:
                res = await connection.recv()
                tick = json.loads(res)
                self.update_data(tick)
                await asyncio.sleep(0.005)


    def run(self):
        asyncio.run(self.ws_connect())

if __name__ == '__main__':
    c = Client("EURUSD",5)
    c.run()

