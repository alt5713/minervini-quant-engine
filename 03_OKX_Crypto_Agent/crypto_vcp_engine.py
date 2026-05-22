import pandas as pd
import numpy as np

class CryptoVCPEngine:
    def __init__(self, stats_window=50):
        self.stats_window = stats_window

    def analyze(self, df):
        """캔들 데이터를 기반으로 VCP 점수 및 상태 계산"""
        if len(df) < self.stats_window:
            return {"score": 0, "status": "Insufficient Data"}

        # 1. 이동평균선 (EMA) 계산
        df['ema10'] = df['close'].ewm(span=10, adjust=False).mean()
        df['ema20'] = df['close'].ewm(span=20, adjust=False).mean()
        df['ema50'] = df['close'].ewm(span=50, adjust=False).mean()

        # 2. 변동성 수축 (ATR 기반)
        df['tr'] = np.maximum(df['high'] - df['low'], 
                             np.maximum(abs(df['high'] - df['close'].shift(1)), 
                                        abs(df['low'] - df['close'].shift(1))))
        df['atr'] = df['tr'].rolling(window=14).mean()
        
        # 최근 5개 ATR이 그 이전 20개 ATR 평균보다 낮은지 확인 (수축 여부)
        recent_atr = df['atr'].iloc[-5:].mean()
        historical_atr = df['atr'].iloc[-25:-5].mean()
        atr_contraction = (recent_atr < historical_atr)

        # 3. 가격 타이트니스 (Tightness)
        # 최근 10개 캔들의 최고가-최저가 폭이 1% 이내인지 확인
        recent_range = (df['high'].iloc[-10:].max() - df['low'].iloc[-10:].min()) / df['close'].iloc[-1]
        is_tight = (recent_range < 0.015) # 1.5% 이내면 타이트함

        # 4. 거래량 Z-Score (Quiet Period 확인)
        vol_mean = df['volume'].iloc[-self.stats_window:].mean()
        vol_std = df['volume'].iloc[-self.stats_window:].std()
        current_vol_z = (df['volume'].iloc[-1] - vol_mean) / vol_std

        # 5. 종합 점수 산출
        score = 0
        if df['ema10'].iloc[-1] > df['ema20'].iloc[-1] > df['ema50'].iloc[-1]: score += 40 # 정배열
        if atr_contraction: score += 20 # 변동성 수축
        if is_tight: score += 20 # 가격 타이트니스
        if current_vol_z < 0: score += 20 # 조용한 거래량 (Quiet Period)

        status = "BUY" if score >= 80 else "WAIT"
        
        return {
            "score": score,
            "status": status,
            "ema_alignment": score >= 40,
            "atr_contraction": atr_contraction,
            "is_tight": is_tight,
            "vol_z": current_vol_z,
            "recent_range_pct": recent_range * 100
        }
