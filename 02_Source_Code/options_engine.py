import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, date

class OptionsInsightEngine:
    def __init__(self):
        pass

    def analyze_options_sentiment(self, ticker):
        """
        Backward compatible method used by the existing market scanners.
        """
        try:
            res = self.analyze_options_data(ticker)
            if res is None:
                return None
            
            # Reconstruct the exact dictionary expected by main_agent and scanner
            # calls_walls should have 'strike', 'open_interest', 'impliedVolatility'
            calls_df = pd.DataFrame(res['calls'])
            calls_df['open_interest'] = calls_df['openInterest']
            call_walls = calls_df.nlargest(5, 'open_interest')[['strike', 'open_interest', 'impliedVolatility']]
            
            return {
                "status": "Success",
                "current_price": res['current_price'],
                "max_pain": res['max_pain'],
                "call_walls": call_walls.to_dict('records'),
                "total_call_oi": res['total_call_oi'],
                "avg_iv": res['avg_iv'],
                "premium_status": res['premium_status']
            }
        except Exception as e:
            print(f"⚠️ analyze_options_sentiment fallback trigger: {e}")
            return None

    def analyze_options_data(self, ticker, expiry=None):
        """
        Advanced options extraction method providing comprehensive metrics,
        Put/Call ratios, 1-Sigma expected ranges, and full options chain for plotting.
        """
        try:
            stock = yf.Ticker(ticker)
            expirations = stock.options
            if not expirations:
                return None

            # Get current stock price
            hist = stock.history(period='5d')
            if hist.empty:
                return None
            current_price = hist['Close'].iloc[-1]

            # 1. Smart Expiration Selection / Option Month Profile
            expirations_data = []
            selected_expiry = expiry
            
            # Scan the first 5 expirations to build the Option Month Profile and find the most active one
            for exp in expirations[:5]:
                try:
                    chain = stock.option_chain(exp)
                    c_oi = chain.calls['openInterest'].fillna(0).sum()
                    p_oi = chain.puts['openInterest'].fillna(0).sum()
                    expirations_data.append({
                        'expiry': exp,
                        'calls_oi': int(c_oi),
                        'puts_oi': int(p_oi),
                        'total_oi': int(c_oi + p_oi)
                    })
                except:
                    continue

            # If no expiry specified, automatically select the expiration with highest Open Interest
            if not selected_expiry:
                if expirations_data:
                    # Pick the one with the maximum total open interest
                    selected_expiry = max(expirations_data, key=lambda x: x['total_oi'])['expiry']
                else:
                    selected_expiry = expirations[0]

            # Fetch target option chain
            opt_chain = stock.option_chain(selected_expiry)
            calls, puts = opt_chain.calls.copy(), opt_chain.puts.copy()

            # Clean and fill NaN values
            calls['openInterest'] = calls['openInterest'].fillna(0)
            puts['openInterest'] = puts['openInterest'].fillna(0)
            calls['volume'] = calls['volume'].fillna(0)
            puts['volume'] = puts['volume'].fillna(0)
            calls['impliedVolatility'] = calls['impliedVolatility'].fillna(0)
            puts['impliedVolatility'] = puts['impliedVolatility'].fillna(0)

            # 2. Max Pain Calculation
            max_pain = self._calculate_max_pain(calls, puts)

            # 3. Call and Put Walls
            call_wall = calls.loc[calls['openInterest'].idxmax()]['strike'] if not calls.empty else None
            put_wall = puts.loc[puts['openInterest'].idxmax()]['strike'] if not puts.empty else None

            # 4. Total volumes and open interests
            total_call_oi = calls['openInterest'].sum()
            total_put_oi = puts['openInterest'].sum()
            total_call_vol = calls['volume'].sum()
            total_put_vol = puts['volume'].sum()

            # Put/Call Ratio (PCR)
            pcr_oi = total_put_oi / total_call_oi if total_call_oi > 0 else 0
            pcr_vol = total_put_vol / total_call_vol if total_call_vol > 0 else 0

            # 5. Implied Volatility (IV) Analysis
            # For ATM IV, get average of options within 10% of the current spot price
            near_calls = calls[(calls['strike'] >= current_price * 0.9) & (calls['strike'] <= current_price * 1.1)]
            near_puts = puts[(puts['strike'] >= current_price * 0.9) & (puts['strike'] <= current_price * 1.1)]
            
            iv_calls = near_calls['impliedVolatility'].mean() if not near_calls.empty else calls['impliedVolatility'].mean()
            iv_puts = near_puts['impliedVolatility'].mean() if not near_puts.empty else puts['impliedVolatility'].mean()
            
            avg_iv = (iv_calls + iv_puts) / 2.0 if (not np.isnan(iv_calls) and not np.isnan(iv_puts)) else 0.3
            if avg_iv <= 0:
                avg_iv = 0.3 # Fallback default

            # DTE (Days to Expiration)
            expiry_dt = datetime.strptime(selected_expiry, "%Y-%m-%d").date()
            today = date.today()
            dte = max(1, (expiry_dt - today).days)

            # 6. 1-Sigma Expected Move Calculation
            # Expiry-specific expected move
            sigma_move = current_price * avg_iv * np.sqrt(dte / 365.0)
            one_sigma_lower = current_price - sigma_move
            one_sigma_upper = current_price + sigma_move

            # Normalized 30-day expected move (excellent for mid-term swing planning)
            sigma_move_30d = current_price * avg_iv * np.sqrt(30.0 / 365.0)
            one_sigma_lower_30d = current_price - sigma_move_30d
            one_sigma_upper_30d = current_price + sigma_move_30d

            return {
                "status": "Success",
                "ticker": ticker,
                "current_price": current_price,
                "selected_expiry": selected_expiry,
                "days_to_expiry": dte,
                "max_pain": max_pain,
                "call_wall": call_wall,
                "put_wall": put_wall,
                "total_call_oi": total_call_oi,
                "total_put_oi": total_put_oi,
                "total_call_vol": total_call_vol,
                "total_put_vol": total_put_vol,
                "pcr_oi": pcr_oi,
                "pcr_vol": pcr_vol,
                "avg_iv": avg_iv,
                "premium_status": "LIGHT" if avg_iv < 0.4 else "HEAVY",
                "one_sigma_lower": one_sigma_lower,
                "one_sigma_upper": one_sigma_upper,
                "one_sigma_lower_30d": one_sigma_lower_30d,
                "one_sigma_upper_30d": one_sigma_upper_30d,
                "calls": calls.to_dict('records'),
                "puts": puts.to_dict('records'),
                "expirations_profile": expirations_data
            }
        except Exception as e:
            print(f"❌ analyze_options_data error for {ticker}: {e}")
            return None

    def _calculate_max_pain(self, calls, puts):
        calls = calls.copy()
        puts = puts.copy()
        calls['openInterest'] = calls['openInterest'].fillna(0)
        puts['openInterest'] = puts['openInterest'].fillna(0)
        
        strikes = sorted(list(set(calls['strike'].dropna()) | set(puts['strike'].dropna())))
        if not strikes:
            return 0
        losses = []
        for s in strikes:
            c_loss = calls[calls['strike'] < s].apply(lambda x: (s - x['strike']) * x['openInterest'], axis=1).sum()
            p_loss = puts[puts['strike'] > s].apply(lambda x: (x['strike'] - s) * x['openInterest'], axis=1).sum()
            losses.append(c_loss + p_loss)
        return strikes[np.argmin(losses)]

