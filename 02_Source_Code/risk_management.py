import pandas as pd
import numpy as np

class AdaptiveExecution:
    def __init__(self):
        pass

    def v7_0_tennis_ball_rs(self, df):
        """V7.2.1 - Tennis Ball RS Filter (저점 버티기)"""
        if len(df) < 20:
            return {"score": 0, "reason": "데이터 부족"}
        
        try:
            # 주가 수익률 기반 RSI 대안 계산
            returns = df['Close'].pct_change()
            recent_rsi_5 = returns.iloc[-5:].mean() * 100
            
            # 저점에서의 회복 탄력성 (사용자 로직 시뮬레이션)
            is_recovery = recent_rsi_5 > -1.0 # 급락 후 진정 구간
            
            score = 25 if is_recovery else 0
            return {"score": score, "rsi_level": round(recent_rsi_5, 2), "reason": "회복 신호 확인" if is_recovery else "과열 또는 하락 중"}
        except:
            return {"score": 0, "reason": "계산 오류"}

    def v7_1_apex_maturity(self, df):
        """V7.2.2 - Apex Maturity Index (수렴 완성도)"""
        if len(df) < 252:
            return {"score": 0, "reason": "데이터 부족"}
        
        try:
            current_close = df['Close'].iloc[-1]
            high_1yr = df['High'].iloc[-252:].max()
            low_1yr = df['Low'].iloc[-252:].min()
            
            price_range = high_1yr - low_1yr
            position = (current_close - low_1yr) / price_range if price_range > 0 else 0.5
            
            score = 30
            if position <= 0.3: score += 40 # 하단부 수렴 (완성도 높음)
            elif position >= 0.7: score -= 20 # 상단부 과열
            
            return {"score": score, "position": f"{position:.1%}", "reason": f"가격 위치: {position:.1%}"}
        except:
            return {"score": 15, "reason": "분석 불가"}

    def v7_2_atr_stop(self, df):
        """V7.2.3 - ATR-Buffer Stop (동적 손절)"""
        try:
            current_close = df['Close'].iloc[-1]
            # 14일 ATR 계산
            high_low = df['High'] - df['Low']
            atr_14 = high_low.rolling(window=14).mean().iloc[-1]
            
            # 손절 거리 (ATR의 1.5~2배)
            stop_buffer = atr_14 * 1.5
            stop_price = current_close - stop_buffer
            
            return {
                "score": 40,
                "atr": atr_14,
                "stop_price": stop_price,
                "reason": "동적 손절 라인 설정 완료"
            }
        except:
            return {"score": 0, "stop_price": 0, "reason": "계산 불가"}

    def v7_3_momentum_decay(self, df):
        """V7.2.4 - Momentum Decay (에너지 둔화)"""
        if len(df) < 20:
            return {"score": 0, "reason": "데이터 부족"}
            
        try:
            returns = df['Close'].pct_change()
            ma3 = returns.rolling(window=3).mean().iloc[-1]
            ma6 = returns.rolling(window=6).mean().iloc[-1]
            
            decay = 0
            if ma6 != 0:
                decay_ratio = (ma3 - ma6) / abs(ma6)
                if decay_ratio < -0.2: # 단기 모멘텀이 장기 대비 20% 이상 둔화
                    decay = 45
                elif decay_ratio < -0.1:
                    decay = 30
            
            return {"score": decay, "reason": "에너지 둔화 징후" if decay > 0 else "에너지 유지"}
        except:
            return {"score": 0, "reason": "분석 불가"}
