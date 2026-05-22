from data_fetcher import DataFetcher
from core_logic import MinerviniV6Engine
from risk_management import AdaptiveExecution
from smart_money import SmartMoneyEngine
from options_engine import OptionsInsightEngine
from conflict_resolver import AdvancedConflictResolver # V9.5 업데이트
from rrg_visualizer import RRGVisualizer
import pandas as pd
import numpy as np

class AntigravityMasterV95: # V9.5 Upgrade
    def __init__(self):
        self.fetcher = DataFetcher()
        self.v6_engine = MinerviniV6Engine()
        self.risk_mgr = AdaptiveExecution()
        self.smart_money = SmartMoneyEngine()
        self.options_insight = OptionsInsightEngine()
        # VCP 통계 기반 초기화 (V9.5 신규)
        self.conflict_resolver = AdvancedConflictResolver(historical_vcp_stats={'mean': 65, 'std': 12})
        self.rrg_viz = RRGVisualizer()

    def run_strategy_pipeline(self, sector_stock_map):
        print("="*80)
        print("⚡ Antigravity Minervini V9.5 - Statistical Optimization Pipeline Enabled")
        print("="*80)
        
        regime = self._check_market_regime()
        if not regime['allow_entry']:
            print(f"\n⛔ 진입 제한: {regime['reason']}")
            return

        all_reports = []
        for sector, tickers in sector_stock_map.items():
            for ticker in tickers:
                print(f" > {ticker} 분석 중 (V9.5 Volatility Normalization)...")
                try:
                    df = self.fetcher.fetch_data(ticker)
                    if df is None: continue
                    
                    vcp_score = self.v6_engine.v5_0_trend_template(df)['score'] + \
                                self.v6_engine.v5_0_vcp_like(df)['score']
                    
                    flow_score = self.smart_money.calculate_v7_5_score(ticker, df)['total_bonus']
                    
                    is_korea = ticker.endswith('.KQ') or ticker.endswith('.KS')
                    options_result = self.options_insight.analyze_options_sentiment(ticker) if not is_korea else None
                    fallback_signal = self._apply_fallback_logic(df) if not options_result else None
                    
                    # [V9.5 핵심] 변동성 팩터를 포함한 충돌 회피 연산
                    decision, adj_weight = self.conflict_resolver.resolve(
                        vcp_score, options_result, fallback_signal, market_regime=regime
                    )
                    
                    # 최종 가중치 합산 (V9.5 통계적 모델)
                    total_score = (vcp_score * 0.4 + flow_score * 0.3) * adj_weight
                    
                    all_reports.append({
                        'ticker': ticker, 'sector': sector, 'score': total_score,
                        'decision': decision, 'current_price': df['Close'].iloc[-1],
                        'stop_loss': self.risk_mgr.v7_2_atr_stop(df)['stop_price'],
                        'v8_0': options_result
                    })
                except Exception as e:
                    print(f"  ⚠️ {ticker} 분석 실패: {e}")

        self._generate_v9_report(all_reports)

    def _apply_fallback_logic(self, df):
        recent_vol = df['Volume'].tail(5).mean()
        avg_vol = df['Volume'].tail(60).mean()
        return 'STRONG_SIGNAL' if recent_vol > avg_vol * 1.5 else 'NEUTRAL'

    def _check_market_regime(self):
        try:
            spy = self.fetcher.fetch_market_data()
            current_spy = spy['Close'].iloc[-1]
            ma50_spy = spy['Close'].rolling(50).mean().iloc[-1]
            
            # 시장 변동성 팩터 계산 (V9.5 신규)
            # 최근 20일 수익률의 표준편차 기반
            vol_factor = spy['Close'].pct_change().tail(20).std() * 100
            # 정규화: 평균 변동성(1.0) 기준
            norm_vol_factor = max(1.0, vol_factor / 1.2) 

            if current_spy < ma50_spy:
                return {'allow_entry': False, 'reason': 'SPY below 50MA', 'state': 'Bearish'}
            return {'allow_entry': True, 'state': 'Bullish', 'volatility_factor': norm_vol_factor}
        except:
            return {'allow_entry': True, 'state': 'Unknown', 'volatility_factor': 1.0}

    def _generate_v9_report(self, reports):
        sorted_reports = sorted(reports, key=lambda x: x['score'], reverse=True)
        print("\n" + "X"*80)
        print("🏆 Antigravity V9.5 마스터 실전 가이드")
        print("X"*80)
        for i, r in enumerate(sorted_reports):
            color = "🟢" if r['decision'] == "BUY" else "🟡" if r['decision'] == "WAIT" else "⚪"
            print(f"\n{i+1}위. {color} [{r['ticker']}] (Score: {r['score']:.2f})")
            print(f"   - 최종 결정: {r['decision']} (가중치 적용 완료)")
            print(f"   - 실행 가이드: 매수 ${r['current_price']:.2f} / 손절 ${r['stop_loss']:.2f}")

if __name__ == "__main__":
    my_portfolio = {'XLK': ['CIFR'], 'XLC': ['GOOGL'], 'KRW': ['189330.KQ']}
    master = AntigravityMasterV95()
    master.run_strategy_pipeline(my_portfolio)
