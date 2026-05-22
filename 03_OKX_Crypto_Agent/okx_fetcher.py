import ccxt
import pandas as pd
import numpy as np

class OKXFetcher:
    def __init__(self, api_key=None, secret=None, password=None):
        self.exchange = ccxt.okx({
            'apiKey': api_key,
            'secret': secret,
            'password': password,
            'enableRateLimit': True,
        })

    def fetch_ohlcv(self, symbol='BTC/USDT:USDT', timeframe='15m', limit=100):
        """OHLCV 데이터를 가져와 Pandas DataFrame으로 반환"""
        ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        return df

    def fetch_order_book(self, symbol='BTC/USDT:USDT', limit=20):
        """호가창 데이터를 가져옴"""
        return self.exchange.fetch_order_book(symbol, limit=limit)

    def fetch_funding_rate(self, symbol='BTC/USDT:USDT'):
        """현재 펀딩비 조회"""
        funding = self.exchange.fetch_funding_rate(symbol)
        return funding['fundingRate']

    def fetch_ticker(self, symbol='BTC/USDT:USDT'):
        """현재가 정보 조회"""
        return self.exchange.fetch_ticker(symbol)
