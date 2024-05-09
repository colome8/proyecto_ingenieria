import sys
from datetime import datetime

from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtCore import QTimer
import asyncio
import websockets
import json
import mplfinance as mpf
import pandas as pd
from io import StringIO
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib import pyplot as plt


class CandleWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.timeframe = 5
        self.pair = "EURUSD"


        # Create and set up the main widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Create a layout for the main widget
        layout = QVBoxLayout(self.central_widget)

        # Create a figure and canvas
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)


        # Start the asyncio event loop
        self.loop = asyncio.get_event_loop()
        self.data = None
        self.websocket_task = None

        # Set up the initial candlestick chart
        self.ax.grid(True)
        self.update_plot()

    def start_websocket_connection(self):
        async def ws_connect():
            async with websockets.connect(f'ws://127.0.0.1:4444/ws/{self.pair}/{self.timeframe}', timeout=60) as connection:
                data = await connection.recv()
                self.data = pd.read_json(StringIO(json.loads(data)))
                self.data = self.data.set_index(
                    pd.to_datetime(self.data.index, unit='s'))  # Convertir el índice a DatetimeIndex

                self.update_plot()
                while True:
                    await asyncio.sleep(1)
                    tick = await connection.recv()
                    print(self.data)
                    self.update_data(json.loads(tick))
                    self.update_plot()


        asyncio.run(ws_connect())

    def update_data(self, tick):
        timestamp = tick.get('timestamp')
        ask = tick.get('ask')
        bid = tick.get('bid')
        mid = (ask+bid)/2
        print(self.data)
        last_candle = self.data.iloc[-1].copy()
        print(last_candle.name, datetime.fromtimestamp(last_candle.name.timestamp() + self.timeframe * 60), datetime.fromtimestamp(timestamp))
        if (last_candle.name.timestamp()+self.timeframe*60)<timestamp:
            self.data = self.data[1:]._append(pd.Series({'Open':mid, 'High':ask,'Low':bid,'Close':mid},name=datetime.fromtimestamp(last_candle.name.timestamp()+self.timeframe*60)))
        else:
            last_candle.Close = mid
            if last_candle.High<ask:
                last_candle.High=ask
            if last_candle.Low>bid:
                last_candle.Low=bid
            self.data.iloc[-1] = last_candle


    def update_plot(self):
        self.ax.clear()
        self.ax.grid(True)
        if self.data is not None:
            mpf.plot(self.data, ax=self.ax, type='candle')
        self.canvas.draw()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CandleWindow()
    window.show()
    window.start_websocket_connection()  # Start WebSocket connection
    sys.exit(app.exec_())
