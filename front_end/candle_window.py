import sys
from datetime import datetime, timedelta
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtCore import QTimer
import mplfinance as mpf

class MainWindow(QMainWindow):
    def __init__(self, initial_data):
        super().__init__()

        # Create and set up the main widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Create a layout for the main widget
        layout = QVBoxLayout(self.central_widget)

        # Create a figure and canvas
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        # Initialize the timer for updating the plot
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(1000)  # Update plot every 1000 milliseconds

        self.data = initial_data

        # Set up the initial candlestick chart
        self.ax.grid(True)
        mpf.plot(self.data, ax=self.ax, type='candle', style='charles', title='Candlestick Plot')

    @staticmethod
    def update_candle(candle, new_value):
        candle = candle.copy()  # Create a copy of the DataFrame
        candle['close'] = new_value
        if candle['high'] < new_value:
            candle['high'] = new_value
        if candle['low'] > new_value:
            candle['low'] = new_value
        return candle

    def update_plot(self):
        # Update the close price of the last OHLC data point with a random value
        self.data.iloc[-1] = self.update_candle(self.data.iloc[-1], (np.random.rand() - 0.5) * 10)

        # Clear the previous candlestick chart and redraw it with the updated data
        self.ax.clear()
        self.ax.grid(True)
        mpf.plot(self.data, ax=self.ax, type='candle', style='charles', title='Candlestick Plot')

        # Draw the updated plot on the canvas
        self.canvas.draw()

if __name__ == '__main__':
    from data.feeder.feeder import Feeder

    app = QApplication(sys.argv)
    f = Feeder("EURUSD")
    data = f.get_ticks()
    window=MainWindow(data)

    window.setGeometry(100, 100, 800, 600)
    window.show()
    sys.exit(app.exec_())

