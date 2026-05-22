import yfinance as yf
import pandas as pd
from datetime import datetime
import warnings

warnings.filterwarnings('ignore')

class DataFetcher:
    def __init__(self):
        self.market_ticker = "SPY"

    def fetch_data(self, ticker, start_date="2015-01-01"):
        """주가 데이터 수집 및 전처리"""
        try:
            end_date = datetime.now().strftime('%Y-%m-%d')
            stock = yf.download(ticker, start=start_date, end=end_date, progress=False, interval='1d')
            
            if stock.empty:
                print(f"⚠️ {ticker} 데이터를 찾을 수 없습니다.")
                return None
            
            # 전처리: 컬럼이 MultiIndex인 경우 처리
            if isinstance(stock.columns, pd.MultiIndex):
                stock.columns = stock.columns.get_level_values(0)
                
            stock = stock.dropna()
            stock['Volume'] = stock['Volume'].astype(float)
            stock['Return'] = stock['Close'].pct_change()
            
            return stock
        except Exception as e:
            print(f"❌ {ticker} 데이터 로드 오류: {e}")
            return None

    def fetch_market_data(self, start_date="2015-01-01"):
        """시장 지수(SPY) 데이터를 가져옵니다."""
        return self.fetch_data(self.market_ticker, start_date=start_date)

    def calculate_rs_intensity(self, stock_df, spy_df):
        """V5.0.3 - RS Intensity 2.0 (시장 대비 탄력)"""
        if stock_df is None or spy_df is None or len(stock_df) < 90 or len(spy_df) < 90:
            return {"score": -5, "rs_intensity": "0.00x", "reason": "데이터 부족"}

        try:
            # 최근 3개월 (약 63일) 수익률 비교
            # 사용자님 로직 기반 (최근 분기별 데이터 확보가 어려운 경우를 대비한 프록시 계산)
            stock_recent = stock_df['Close'].iloc[-63:].pct_change().sum()
            spy_recent = spy_df['Close'].iloc[-63:].pct_change().sum()
            
            if pd.isna(stock_recent) or pd.isna(spy_recent) or spy_recent == 0:
                return {"score": 0, "rs_intensity": "0.00x", "reason": "계산 불가"}
                
            rs_intensity = stock_recent / spy_recent
            score = 30 if rs_intensity >= 1.5 else (20 if rs_intensity >= 1.0 else 0)
            
            return {
                "score": score,
                "rs_intensity": f"{rs_intensity:.2f}x",
                "reason": "RS Intensity OK" if rs_intensity >= 1.0 else "시장 대비 약세"
            }
        except Exception as e:
            return {"score": -5, "rs_intensity": "0.00x", "reason": str(e)}
