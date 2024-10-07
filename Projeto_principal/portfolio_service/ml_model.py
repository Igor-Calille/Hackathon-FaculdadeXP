import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import TimeSeriesSplit, GridSearchCV
from indicadores import Indicadores

def train_ml_model(data):
    data['target'] = data['close'].shift(-1)
    features = ['open', 'high', 'low', 'close', 'volume']

    ind = Indicadores()
    data['rsi_14'] = ind.get_rsi(data['close'])
    data['stoch_rsi_14'] = ind.get_stochastic_rsi(data['close'])
    data['macd'] = ind.get_macd(data['close'])
    data['ema_14'] = ind.get_media_movel_exponecial(data['close'])

    data.dropna(inplace=True)

    X = data[['open', 'high', 'low', 'close', 'volume', 'rsi_14', 'stoch_rsi_14', 'macd', 'ema_14']]
    y = data['target']

    tscv = TimeSeriesSplit(n_splits=5)
    model = RandomForestRegressor(random_state=42)
    param_search = {
        'n_estimators': [50, 100],
        'max_features': ['sqrt', 'log2'],
        'max_depth': [None, 10],
        'min_samples_split': [2, 5],
        'min_samples_leaf': [1, 2],
        'bootstrap': [True, False]
    }
    
    gsearch = GridSearchCV(estimator=model, cv=tscv, param_grid=param_search, scoring='neg_mean_squared_error', n_jobs=-1, verbose=2)
    gsearch.fit(X, y)

    best_model = gsearch.best_estimator_
    data['predicted_price'] = best_model.predict(X)
    data['signal_ml'] = np.where(data['predicted_price'] > data['close'], 1, -1)

    return data['signal_ml']
