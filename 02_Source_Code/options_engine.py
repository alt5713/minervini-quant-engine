import yfinance as yf
import pandas as pd
import numpy as np

class OptionsInsightEngine:
    def __init__(self):
        pass

    def analyze_options_sentiment(self, ticker):
        try:
            stock = yf.Ticker(ticker)
            expirations = stock.options
            if not expirations: return None

            expiry = expirations[0]
            opt_chain = stock.option_chain(expiry)
            calls, puts = opt_chain.calls, opt_chain.puts

            # 1. Max Pain
            max_pain = self._calculate_max_pain(calls, puts)
            
            # 2. Call Walls (Open Interest 기반 정렬 및 필드명 통일)
            calls['open_interest'] = calls['openInterest']
            call_walls = calls.nlargest(5, 'open_interest')[['strike', 'open_interest', 'impliedVolatility']]
            
            # 3. 전체 OI 합산 (비중 계산용)
            total_call_oi = calls['open_interest'].sum()
            
            # 4. 내재 변동성 (IV) 분석
            avg_iv = (calls['impliedVolatility'].mean() + puts['impliedVolatility'].mean()) / 2
            current_price = stock.history(period='1d')['Close'].iloc[-1]

            return {
                "status": "Success",
                "current_price": current_price,
                "max_pain": max_pain,
                "call_walls": call_walls.to_dict('records'),
                "total_call_oi": total_call_oi,
                "avg_iv": avg_iv,
                "premium_status": "LIGHT" if avg_iv < 0.4 else "HEAVY"
            }
        except:
            return None

    def _calculate_max_pain(self, calls, puts):
        strikes = sorted(list(set(calls['strike']) | set(puts['strike'])))
        losses = []
        for s in strikes:
            c_loss = calls[calls['strike'] < s].apply(lambda x: (s - x['strike']) * x['openInterest'], axis=1).sum()
            p_loss = puts[puts['strike'] > s].apply(lambda x: (x['strike'] - s) * x['openInterest'], axis=1).sum()
            losses.append(c_loss + p_loss)
        return strikes[np.argmin(losses)]
