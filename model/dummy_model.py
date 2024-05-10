import numpy as np
import pandas as pd


class DummyModel:
    @staticmethod
    def predict(X:pd.DataFrame):
        return X.iloc[-1].Close + np.random.normal()/1000
