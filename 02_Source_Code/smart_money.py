import yfinance as yf
import pandas as pd
import numpy as np

class SmartMoneyEngine:
    def __init__(self):
        # 섹터 매핑 (미국 주요 섹터 ETF)
        self.sector_map = {
            'Technology': 'XLK',
            'Healthcare': 'XLV',
            'Financial Services': 'XLF',
            'Consumer Cyclical': 'XLY',
            'Communication Services': 'XLC',
            'Industrials': 'XLI',
            'Energy': 'XLE',
            'Basic Materials': 'XLB',
            'Real Estate': 'XLRE',
            'Utilities': 'XLU',
            'Consumer Defensive': 'XLP'
        }

    def calculate_v7_5_score(self, ticker, stock_data):
        """V7.5 부가 점수 (0~100 범위) 및 시장 국면 가중치 계산"""
        results = {
            'rrg_score': 0.0,
            'money_flow_score': 0.0,
            'vpa_score': 0.0,
            'regime_weight': 1.0,
            'total_bonus': 0.0
        }

        try:
            # 1. RRG 섹터 분석
            results['rrg_score'] = self._analyze_rrg_flow(ticker)
            
            # 2. 스마트 머니 (Money Flow)
            results['money_flow_score'] = self._analyze_money_flow(stock_data)
            
            # 3. VPA 매집봉 (Effort vs Result)
            results['vpa_score'] = self._analyze_vpa_pattern(stock_data)
            
            # 4. 시장 국면 가중치 (Regime Adjustment)
            results['regime_weight'] = self._adjust_market_regime()
            
            # 보너스 총점 계산 (시장 국면 가중치 적용)
            raw_bonus = results['rrg_score'] + results['money_flow_score'] + results['vpa_score']
            results['total_bonus'] = round(raw_bonus * results['regime_weight'], 1)
            
            return results
        except Exception as e:
            print(f"⚠️ V7.5 분석 오류: {e}")
            return results

    def _analyze_rrg_flow(self, ticker):
        """모듈 1: RRG 섹터 순환 필터"""
        try:
            stock = yf.Ticker(ticker)
            sector = stock.info.get('sector', 'Technology')
            sector_etf = self.sector_map.get(sector, 'XLK')
            
            # 섹터와 시장(SPY) 데이터 비교
            data = yf.download([sector_etf, 'SPY'], period='3mo', progress=False)['Close']
            
            if len(data) < 20: return 0
            
            # 상대 강도(RS) 계산
            rs_ratio = (data[sector_etf] / data['SPY']).pct_change(20).iloc[-1]
            
            score = 0
            if rs_ratio > 0.02: score = 30  # Leading
            elif rs_ratio > 0: score = 15    # Improving
            elif rs_ratio < -0.02: score = -10 # Lagging
            
            return float(score)
        except:
            return 0

    def _analyze_money_flow(self, df):
        """모듈 2: Force Index 기반 자금 유입 체크"""
        try:
            if len(df) < 10: return 0
            
            # Force Index: (Close - Prev Close) * Volume
            force_index = (df['Close'] - df['Close'].shift(1)) * df['Volume']
            recent_force = force_index.iloc[-5:].sum()
            
            score = 0
            if recent_force > 0:
                score = 30 if df['Close'].iloc[-1] > df['Close'].rolling(20).mean().iloc[-1] else 15
            
            return float(score)
        except:
            return 0

    def _analyze_vpa_pattern(self, df):
        """모듈 3: VPA (Effort vs Result) 매집봉 감지"""
        try:
            if len(df) < 5: return 0
            
            last_vol = df['Volume'].iloc[-1]
            avg_vol = df['Volume'].rolling(20).mean().iloc[-1]
            price_change = abs(df['Close'].pct_change().iloc[-1])
            
            score = 0
            # 노력(거래량)은 큰데 결과(가격변동)가 작음 = 매집(Accumulation)
            if last_vol > avg_vol * 1.5 and price_change < 0.01:
                score = 40
            # 돌파 시 거래량 동반
            elif last_vol > avg_vol * 1.2 and df['Close'].iloc[-1] > df['Close'].iloc[-2]:
                score = 20
                
            return float(score)
        except:
            return 0

    def _adjust_market_regime(self):
        """모듈 4: 시장 국면 가중치 (나스닥 50일선 기준)"""
        try:
            nasdaq = yf.download('^IXIC', period='3mo', progress=False)['Close']
            ma50 = nasdaq.rolling(50).mean().iloc[-1]
            current = nasdaq.iloc[-1]
            
            # 강세장(1.2배 가중치) vs 약세장(0.8배 가중치)
            return 1.2 if current > ma50 else 0.8
        except:
            return 1.0
