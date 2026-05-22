import pandas as pd
import numpy as np
import yfinance as yf

class MinerviniV6Engine:
    def __init__(self):
        pass

    # ========================================
    # Step 1. [V5.0] 기초 체력 및 트렌드 검증
    # ========================================
    
    def v5_0_fundamental_check(self, df):
        """V5.0.1 - 재무적 질 (프록시 계산)"""
        scores = {'EPS_growth_acceleration': 0}
        try:
            if len(df) >= 252 * 4:
                # 주가 수익률을 통한 성장 가속화 시뮬레이션
                q1 = df['Close'].iloc[-(252*4+1):-(252*3+1)].pct_change().mean()
                q2 = df['Close'].iloc[-(252*3+1):-(252*2+1)].pct_change().mean()
                q3 = df['Close'].iloc[-(252*2+1):-252].pct_change().mean()
                
                # 버그 수정: 리스트 컴프리헨션 문법 수정 [q for q in ...]
                qs = [q1, q2, q3]
                if all([not pd.isna(q) for q in qs]):
                    if q3 > q2 and q2 > q1:
                        scores['EPS_growth_acceleration'] += 10
                
                # ROE/EPS 성장 대체 체크 (1년 전 대비 20% 상승 시 가점)
                if df['Close'].iloc[-1] > df['Close'].iloc[-252] * 1.2:
                    scores['EPS_growth_acceleration'] += 5
        except:
            scores['EPS_growth_acceleration'] = -5
            
        return {"score": scores['EPS_growth_acceleration'], "details": scores}

    def v5_0_trend_template(self, df):
        """V5.0.2 - 트렌드 템플릿 (MA 정배열 + EMA 기울기)"""
        if len(df) < 400:
            return {"score": -10, "reason": "데이터 부족"}
        
        try:
            # 지표 계산
            df['MA50'] = df['Close'].rolling(window=50).mean()
            df['MA150'] = df['Close'].rolling(window=150).mean()
            df['MA200'] = df['Close'].rolling(window=200).mean()
            df['EMA50'] = df['Close'].ewm(span=50, adjust=False).mean()
            
            last = df.iloc[-1]
            prev_30 = df.iloc[-30]
            
            # MA 정배열 확인
            ma_order_ok = (last['MA50'] > last['MA150'] > last['MA200'])
                
            # EMA(50) 상승 기울기 체크
            ema_slope = ((last['EMA50'] - prev_30['EMA50']) / prev_30['EMA50']) * 100
            
            score = 20 if ma_order_ok and ema_slope > 0.5 else (10 if ma_order_ok else 0)
            return {"score": score, "reason": f"MA 정배열: {'OK' if ma_order_ok else 'No'}, EMA 기울기: {ema_slope:.2f}%"}
        except Exception as e:
            return {"score": -10, "reason": str(e)}

    def v5_0_vcp_like(self, df):
        """V5.0.4 - VCP 대체 패턴 (ATR 수축 + 거래량 고갈)"""
        if len(df) < 365:
            return {"score": -10, "reason": "데이터 부족"}
        
        try:
            # 변동성 수축 체크
            recent_range_20 = (df['High'].iloc[-20:].max() - df['Low'].iloc[-20:].min()) / df['Close'].iloc[-1]
            annual_range = (df['High'].iloc[-252:].max() - df['Low'].iloc[-252:].min()) / df['Close'].iloc[-252]
            
            vcp_score = 0
            if annual_range > 0:
                contraction_ratio = recent_range_20 / annual_range
                if contraction_ratio <= 0.3: vcp_score += 40
                elif contraction_ratio <= 0.5: vcp_score += 25
                else: vcp_score -= 10
                
                # 거래량 Dry-up 체크
                max_vol = df['Volume'].iloc[-252:].max()
                recent_vol = df['Volume'].iloc[-20:].mean()
                vol_contraction = recent_vol / max_vol if max_vol > 0 else 1.0
                
                if vol_contraction <= 0.4: vcp_score += 30
                return {"score": vcp_score, "reason": f"ATR 수축: {contraction_ratio:.1%}, 거래량 고갈: {vol_contraction:.1%}"}
        except:
            return {"score": -5, "reason": "계산 오류"}
        return {"score": 0, "reason": "조건 미달"}

    # ========================================
    # Step 2. [V6.0] 파동 위치 및 안전마진
    # ========================================

    def v6_0_elliott_wave(self, df):
        """V6.0.1 - Elliott Wave Cycle Filter"""
        if len(df) < 504:
            return {"score": -5, "reason": "데이터 부족", "wave_type": "UNKNOWN"}
        
        try:
            current_high = df['High'].iloc[-1]
            prev_high = df['High'].iloc[-504] # 2년 전 고점 대비
            high_ratio = (current_high - prev_high) / prev_high if prev_high > 0 else 0
            
            # 저점 방어 확인 (1년 전 저점 대비 5% 이상 위)
            low_1yr = df['Low'].iloc[-252].min()
            is_low_holding = df['Low'].iloc[-1] >= low_1yr * 1.05
            
            if high_ratio < 0.1 and is_low_holding:
                return {"score": 25, "wave_type": "WAVE_3 (가속기)", "reason": f"고점 대비 {high_ratio:.1%}"}
            elif high_ratio < 0.2:
                return {"score": 20, "wave_type": "WAVE_1/2 (축적기)", "reason": "안정적 위치"}
            
            return {"score": 0, "wave_type": "UNKNOWN", "reason": "과열 또는 불확실"}
        except:
            return {"score": 0, "wave_type": "UNKNOWN", "reason": "분석 불가"}

    def v6_0_triangle(self, df):
        """V6.0.2 - Triangle Classification"""
        if len(df) < 50:
            return {"score": -5, "reason": "데이터 부족"}
        
        try:
            recent = df.iloc[-50:]
            highs = recent['High'].values
            
            # 하향 수렴 체크
            is_downward = all(highs[i] <= highs[i-1] for i in range(1, len(highs)))
            
            # 양봉 비율 체크
            up_days = (recent['Close'] > recent['Open']).sum()
            up_ratio = up_days / len(recent)
            
            score = 30 if is_downward else 20
            if up_ratio > 0.7: score += 15
            
            type_name = "Triangle Type 2 (하향수렴)" if is_downward else "Triangle Type 3 (대칭형)"
            return {"score": score, "type": type_name, "reason": f"양봉 비율: {up_ratio:.1%}"}
        except:
            return {"score": 0, "reason": "분석 불가"}

    def v6_0_rrg_sector(self, ticker):
        """V6.0.3 - RRG Sector Momentum"""
        try:
            # 버그 수정: yf.ticker -> yf.Ticker
            stock_info = yf.Ticker(ticker).info
            sector = stock_info.get('sector', 'Unknown')
            
            if 'Technology' in sector or 'Healthcare' in sector:
                return {"score": 25, "status": "LEADING", "reason": f"섹터: {sector}"}
            elif 'Finance' in sector or 'Energy' in sector:
                return {"score": 15, "status": "NEUTRAL", "reason": f"섹터: {sector}"}
            
            return {"score": 10, "status": "SLOWER", "reason": f"섹터: {sector}"}
        except:
            return {"score": 0, "status": "UNKNOWN", "reason": "정보 없음"}
