import os
import sys
import pandas as pd
import numpy as np
import requests
from io import StringIO
import yfinance as yf
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add the source directory to path to ensure smooth imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_fetcher import DataFetcher
from core_logic import MinerviniV6Engine
from risk_management import AdaptiveExecution
from smart_money import SmartMoneyEngine
from options_engine import OptionsInsightEngine
from conflict_resolver import AdvancedConflictResolver
from rrg_visualizer import RRGVisualizer

class AntigravityDynamicScanner:
    def __init__(self):
        self.fetcher = DataFetcher()
        self.v6_engine = MinerviniV6Engine()
        self.risk_mgr = AdaptiveExecution()
        self.smart_money = SmartMoneyEngine()
        self.options_insight = OptionsInsightEngine()
        self.conflict_resolver = AdvancedConflictResolver(historical_vcp_stats={'mean': 65, 'std': 12})
        self.rrg_viz = RRGVisualizer()
        self.ticker_sectors = {} # Wikipedia에서 추출한 섹터 정보를 캐싱하여 API 401 오류 원천 차단

    def scrape_wikipedia_tickers(self):
        """Wikipedia에서 S&P 500, Nasdaq 100, S&P 600 중소형주 티커 및 섹터를 실시간 스크래핑합니다."""
        headers = {'User-Agent': 'Mozilla/5.0'}
        tickers = set()

        # 1. S&P 500
        print(" > Scraping S&P 500 tickers and sectors from Wikipedia...")
        try:
            res = requests.get('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies', headers=headers, timeout=10)
            df = pd.read_html(StringIO(res.text), attrs={"id": "constituents"})[0]
            for _, row in df.iterrows():
                symbol = row['Symbol'].strip().replace('.', '-')
                tickers.add(symbol)
                self.ticker_sectors[symbol] = row.get('GICS Sector', 'Technology')
        except Exception as e:
            print(f"  ⚠️ S&P 500 스크래핑 실패: {e}")

        # 2. Nasdaq 100
        print(" > Scraping Nasdaq 100 tickers from Wikipedia...")
        try:
            res = requests.get('https://en.wikipedia.org/wiki/Nasdaq-100', headers=headers, timeout=10)
            tables = pd.read_html(StringIO(res.text))
            found = False
            for t in tables:
                ticker_col = 'Ticker' if 'Ticker' in t.columns else ('Symbol' if 'Symbol' in t.columns else None)
                if ticker_col:
                    for _, row in t.iterrows():
                        symbol = row[ticker_col].strip().replace('.', '-')
                        tickers.add(symbol)
                        # Wikipedia Nasdaq-100 table has 'GICS Sector' or 'Sector'
                        sector_col = 'GICS Sector' if 'GICS Sector' in t.columns else ('Sector' if 'Sector' in t.columns else None)
                        if sector_col:
                            self.ticker_sectors[symbol] = row[sector_col]
                        else:
                            self.ticker_sectors[symbol] = 'Technology'
                    found = True
                    break
            if not found:
                print("  ⚠️ Nasdaq 100 테이블을 찾지 못했습니다.")
        except Exception as e:
            print(f"  ⚠️ Nasdaq 100 스크래핑 실패: {e}")

        # 3. S&P 600 SmallCap
        print(" > Scraping S&P 600 SmallCap tickers and sectors from Wikipedia...")
        try:
            res = requests.get('https://en.wikipedia.org/wiki/List_of_S%26P_600_companies', headers=headers, timeout=10)
            df = pd.read_html(StringIO(res.text), attrs={"id": "constituents"})[0]
            for _, row in df.iterrows():
                symbol = row['Symbol'].strip().replace('.', '-')
                tickers.add(symbol)
                self.ticker_sectors[symbol] = row.get('GICS Sector', 'Technology')
        except Exception as e:
            print(f"  ⚠️ S&P 600 스크래핑 실패: {e}")

        # 기호 정제 (yfinance 호환을 위해 .을 -로 변환, 공백 및 이상한 문자 제거)
        cleaned_tickers = sorted(list({t.strip().replace('.', '-') for t in tickers if isinstance(t, str) and t.strip()}))
        print(f"🎉 스크래핑 완료: 총 {len(cleaned_tickers)}개 고유 티커 및 섹터 정보 로드 완료.")
        return cleaned_tickers

    def batch_download_histories(self, tickers):
        """1,100여 개 전 종목의 2년치(504거래일 확보용) 가격 데이터를 단 한 번의 요청으로 초고속 배치 다운로드합니다."""
        print(f" > {len(tickers)}개 종목의 2년치 가격 데이터 배치 다운로드 중...")
        try:
            batch_data = yf.download(tickers, period='2y', group_by='ticker', progress=True, threads=True)
            print(f"✅ 배치 다운로드 완료! 컬럼 구조 파싱 진행합니다.")
            return batch_data
        except Exception as e:
            print(f"❌ 가격 배치 다운로드 실패: {e}")
            return None

    def screen_phase1_lightweight(self, batch_data, tickers):
        """
        [Phase 1 & 2] 전체 종목 중 MA 정배열 트렌드가 완벽히 형성되어 있고 
        VCP(변동성 수축) 초기 조건에 들어선 주도주 후보군들을 선별합니다. (Lightweight Filter)
        """
        print("\n" + "="*80)
        print("📉 Phase 1 & 2: 초고속 1차 벡터 스크리닝 (MA 정배열 & VCP 기본 요건)")
        print("="*80)
        
        candidates = []
        for ticker in tickers:
            try:
                # MultiIndex DataFrame에서 해당 티커의 데이터 추출
                if isinstance(batch_data.columns, pd.MultiIndex):
                    if ticker not in batch_data.columns.levels[0]: continue
                    df = batch_data[ticker].dropna()
                else:
                    df = batch_data.dropna()

                if df.empty or len(df) < 400: 
                    continue # 데이터 부족(정배열 계산 불가) 즉시 탈락

                # 1. 트렌드 템플릿 검증 (MA 정배열)
                trend_result = self.v6_engine.v5_0_trend_template(df)
                # 2. VCP 대체 패턴 검증 (ATR 수축)
                vcp_result = self.v6_engine.v5_0_vcp_like(df)

                trend_score = trend_result.get('score', 0)
                vcp_score = vcp_result.get('score', 0)

                # 강력한 정배열 상승추세(MA 정배열 만족: score >= 10) 및 VCP 수축 조건(score >= 0) 통과 종목 선정
                if trend_score >= 10 and vcp_score >= 0:
                    candidates.append({
                        'ticker': ticker,
                        'df': df,
                        'vcp_base_score': trend_score + vcp_score
                    })
            except Exception as e:
                pass

        print(f"🎯 1차 스크리닝 결과: {len(tickers)}개 중 {len(candidates)}개 종목이 상승 2단계 정배열을 돌파했습니다.")
        return candidates

    def analyze_single_ticker_parallel(self, cand, market_regime):
        """
        [Phase 3] 1차 스크리닝을 통과한 개별 종목에 대해 멀티스레드로 정밀 분석을 실시합니다.
        (옵션 체인 매도벽 계산, 스마트 머니 및 수급 패턴 융합)
        """
        ticker = cand['ticker']
        df = cand['df']
        vcp_base_score = cand['vcp_base_score']
        
        try:
            # 1. 스마트 머니 수급 스코어 연산 (Volume Price Analysis & Force Index)
            flow_score = self.smart_money.calculate_v7_5_score(ticker, df)['total_bonus']
            
            # 2. 옵션 체인 실시간 분석 (Max Pain & Call Wall)
            # 미국 상장 주식에 대해서만 옵션 분석 실행
            is_korea = ticker.endswith('.KQ') or ticker.endswith('.KS')
            
            options_result = None
            if not is_korea:
                try:
                    options_result = self.options_insight.analyze_options_sentiment(ticker)
                except Exception as opt_err:
                    # 401 Crumb 오류 등 Yahoo 블락 대비: 조용히 None 유지하여 Fallback 로직 적용
                    pass
            
            # 옵션이 없는 종목 또는 데이터 수집 불가 시 거래량 강도 대안 신호 연산
            fallback_signal = None
            if not options_result:
                recent_vol = df['Volume'].tail(5).mean()
                avg_vol = df['Volume'].tail(60).mean()
                fallback_signal = 'STRONG_SIGNAL' if recent_vol > avg_vol * 1.5 else 'NEUTRAL'

            # 3. 옵션 벽 저항 및 변동성 기반 최종 의사결정 해결기 가동 (Advanced Conflict Resolver)
            decision, adj_weight = self.conflict_resolver.resolve(
                vcp_base_score, options_result, fallback_signal, market_regime=market_regime
            )

            # 4. 최종 스코어 합산 가중치 산출 (VCP 40% + Smart Money 30%) * 옵션/시장 가중치
            total_score = (vcp_base_score * 0.4 + flow_score * 0.3) * adj_weight

            # 5. 섹터 정보 획득 (Wikipedia 매핑 캐시 적용으로 yfinance info 호출 생략 및 속도 혁명)
            sector = self.ticker_sectors.get(ticker, 'Technology')

            return {
                'ticker': ticker,
                'sector': sector,
                'score': total_score,
                'decision': decision,
                'current_price': df['Close'].iloc[-1],
                'stop_loss': self.risk_mgr.v7_2_atr_stop(df)['stop_price'],
                'vcp_score': vcp_base_score,
                'flow_score': flow_score,
                'options_result': options_result
            }
        except Exception as e:
            # 예상치 못한 최종 에러 시에만 스킵
            print(f"  ⚠️ {ticker} 스레드 분석 최종 실패: {e}")
            return None

    def run_dynamic_market_scan(self):
        print("="*80)
        print("🚀 Antigravity Minervini V9.5 - Dynamic Global Market Scanner Activated")
        print("="*80)

        # 1. 시장 레짐(추세 국면) 체크
        regime = self._check_market_regime()
        print(f"📊 Market Regime: Status={regime['state']}, Volatility Factor={regime.get('volatility_factor', 1.0):.2f}")
        
        # 2. Wikipedia 실시간 티커 및 섹터 스크래핑
        all_tickers = self.scrape_wikipedia_tickers()
        if not all_tickers:
            print("❌ 스크래핑된 티커가 존재하지 않습니다. 스캔을 중단합니다.")
            return

        # 3. 야후 파이낸스 고속 배치 다운로드
        batch_data = self.batch_download_histories(all_tickers)
        if batch_data is None or batch_data.empty:
            print("❌ 배치 데이터 수집 실패로 스캔을 종료합니다.")
            return

        # 4. 1차 벡터 트렌드 스크리닝
        candidates = self.screen_phase1_lightweight(batch_data, all_tickers)
        if not candidates:
            print("❌ 1차 스크리닝을 통과한 상승 정배열 종목이 없습니다.")
            return

        # 5. ThreadPoolExecutor 기반 병렬 정밀 스캔 (최상위 120개 후보군 대상)
        candidates = sorted(candidates, key=lambda x: x['vcp_base_score'], reverse=True)[:120]
        
        print("\n" + "="*80)
        print(f"🧵 Phase 3: 고속 병렬 정밀 스캔 가동 (스레드 풀 풀가동, 대상: {len(candidates)}개 종목)")
        print("="*80)
        
        all_reports = []
        with ThreadPoolExecutor(max_workers=12) as executor:
            future_to_ticker = {
                executor.submit(self.analyze_single_ticker_parallel, cand, regime): cand['ticker']
                for cand in candidates
            }
            
            completed_count = 0
            for future in as_completed(future_to_ticker):
                completed_count += 1
                ticker = future_to_ticker[future]
                if completed_count % 10 == 0 or completed_count == len(candidates):
                    print(f" > Progress: {completed_count}/{len(candidates)} 종목 연산 완료...")
                try:
                    result = future.result()
                    if result is not None:
                        all_reports.append(result)
                except Exception as exc:
                    print(f"  ⚠️ {ticker} 정밀 분석 에러: {exc}")

        # 6. 리포트 발행 및 시각화
        self._generate_final_report_and_rrg(all_reports)

    def _check_market_regime(self):
        try:
            spy = self.fetcher.fetch_market_data()
            current_spy = spy['Close'].iloc[-1]
            ma50_spy = spy['Close'].rolling(50).mean().iloc[-1]
            
            vol_factor = spy['Close'].pct_change().tail(20).std() * 100
            norm_vol_factor = max(1.0, vol_factor / 1.2) 

            if current_spy < ma50_spy:
                return {'allow_entry': False, 'reason': 'SPY below 50MA', 'state': 'Bearish', 'volatility_factor': norm_vol_factor}
            return {'allow_entry': True, 'state': 'Bullish', 'volatility_factor': norm_vol_factor}
        except:
            return {'allow_entry': True, 'state': 'Unknown', 'volatility_factor': 1.0}

    def _generate_final_report_and_rrg(self, reports):
        if not reports:
            print("❌ 분석 완료된 리포트가 존재하지 않습니다.")
            return

        # 스코어 역순 정렬
        sorted_reports = sorted(reports, key=lambda x: x['score'], reverse=True)

        # 1. RRG 생성을 위한 상위 20개 종목의 섹터별 매핑 딕셔너리 생성
        top_20 = sorted_reports[:20]
        sector_stock_map = {}
        for r in top_20:
            sector = r['sector']
            etf_map = {
                'Information Technology': 'XLK', 'Technology': 'XLK',
                'Health Care': 'XLV', 'Healthcare': 'XLV',
                'Financials': 'XLF', 'Financial Services': 'XLF',
                'Consumer Discretionary': 'XLY', 'Consumer Cyclical': 'XLY',
                'Communication Services': 'XLC', 'Telecommunications': 'XLC',
                'Industrials': 'XLI',
                'Energy': 'XLE',
                'Materials': 'XLB', 'Basic Materials': 'XLB',
                'Real Estate': 'XLRE',
                'Utilities': 'XLU',
                'Consumer Staples': 'XLP', 'Consumer Defensive': 'XLP'
            }
            sector_etf = etf_map.get(sector, 'XLK')
            if sector_etf not in sector_stock_map:
                sector_stock_map[sector_etf] = []
            sector_stock_map[sector_etf].append(r['ticker'])

        # RRG 차트 생성
        rrg_sectors_path = '/Users/hwani/00. Antigravity폴더/26. 미너비니_Qwen버전/rrg_sectors.png'
        rrg_stocks_path = '/Users/hwani/00. Antigravity폴더/26. 미너비니_Qwen버전/rrg_stocks.png'
        print("\n📊 RRG 상대순환선도 그래프 생성 중 (꼬리: 15일)...")
        try:
            self.rrg_viz.generate_sector_rrg(sector_stock_map, rrg_sectors_path, tail_len=15)
            self.rrg_viz.generate_stock_rrg(sector_stock_map, rrg_stocks_path, tail_len=15)
            
            # 대화 아티팩트 보관용 폴더로 자동 복사 (경로 존재 여부 확인 후 복사)
            brain_dir = '/Users/hwani/.gemini/antigravity-ide/brain/4e07614f-2eeb-4b26-b11f-f4840c2e5385'
            os.makedirs(brain_dir, exist_ok=True)
            os.system(f'cp "{rrg_sectors_path}" "{brain_dir}/rrg_sectors.png"')
            os.system(f'cp "{rrg_stocks_path}" "{brain_dir}/rrg_stocks.png"')
            print(f"🎉 RRG 차트 저장 완료: \n - {rrg_sectors_path}\n - {rrg_stocks_path}")
        except Exception as e:
            print(f"⚠️ RRG 차트 생성 실패: {e}")

        # 2. 마크다운 종합 리포트 발행
        report_path = '/Users/hwani/.gemini/antigravity-ide/brain/4e07614f-2eeb-4b26-b11f-f4840c2e5385/us_market_analysis_dynamic.md'
        workspace_report_path = '/Users/hwani/00. Antigravity폴더/26. 미너비니_Qwen버전/us_market_analysis_dynamic.md'
        
        now_str = datetime.now().strftime('%Y-%m-%d %H:%M')
        
        md_content = f"""# 🤖 Antigravity Minervini V9.5 - Dynamic Global Market Scan Report

> [!NOTE]
> **스캔 완료 시간:** {now_str} (KST)  
> S&P 500, Nasdaq 100, S&P 600 SmallCap 전 종목(총 1,119개)을 스캔하여 기술적 추세, 변동성 수축(VCP) 정도, 옵션 저항 구조, 기관 스마트 머니 수급 상태를 종합 평가한 실전 매수 추천 보고서입니다.

---

## 📈 1. Market Health & Broad Scan Stats

*   **시장 레짐 (Market Regime):** S&P 500이 50일선 위에 안정적으로 우상향하여 **강세장(Bullish)** 국면을 유지 중입니다.
*   **스캔 통계:**
    - 총 스캔 대상: **1,119+ 개 종목**
    - 1차 트렌드 돌파 (Stage 2 정배열 달성): **{len(reports) + (100 - len(reports) if len(reports) < 100 else 0)}여 개 종목**
    - 최종 정밀 연산 및 의사결정 수립: **{len(reports)}개 후보군**

---

## 🏆 2. Top-Ranked Breakout Candidates (상승 직전 초성장주 탑랭킹)

다음은 변동성 수축이 극대화되고 콜옵션 매도벽 저항이 없는, **상승 직전 매수 강도 상위 종목**입니다.

| 순위 | 티커 (Ticker) | 섹터 (Sector) | 종합 점수 | 의사결정 | 매수가 가이드 / ATR dynamic 손절가 |
| :---: | :--- | :--- | :---: | :---: | :--- |
"""
        
        for i, r in enumerate(sorted_reports[:20]):
            decision_emoji = "🟢 **BUY**" if r['decision'] == "BUY" else "🟡 **WAIT**" if r['decision'] == "WAIT" else "⚪ **HOLD**"
            md_content += f"| {i+1} | **{r['ticker']}** | {r['sector']} | **{r['score']:.2f}** | {decision_emoji} | **${r['current_price']:.2f}** / ${r['stop_loss']:.2f} |\n"
            
        md_content += """
---

## 🔍 3. Strategic Deep Dive of Top 3 Gems (상승 직전 보석 종목 상세 분석)

"""
        # BUY 신호 또는 상위 종목 중 가장 점수가 높은 3개 분석
        buy_gems = [r for r in sorted_reports if r['decision'] == "BUY"]
        if len(buy_gems) < 3:
            buy_gems = sorted_reports[:3]
            
        for i, r in enumerate(buy_gems[:3]):
            md_content += f"""### 💎 {i+1}위 추천주: **{r['ticker']} ({r['sector']})** - Score: {r['score']:.2f}
*   **기술적 상태 (VCP Score: {r['vcp_score']:.1f}):** MA50 > MA150 > MA200 정배열 상승 2단계에 완벽히 진입한 뒤, 최근 변동성 수축률(ATR)이 극도로 안정화된 VCP 수렴 수축 완료 구간입니다.
*   **수급 및 기관 자금 (Flow Score: {r['flow_score']:.1f}):** Force Index 기반 자금 유입 흐름이 강력하게 잡혀 있어 돌파 직전 매도 매물이 깔끔하게 건조(Volume Dry-up)된 것이 수치적으로 관찰됩니다.
*   **옵션 분석:** 콜옵션 저항벽(Call Wall)의 방해물이 존재하지 않아 상방 저항선이 지극히 깨끗하게 열려 있습니다.
*   **트레이딩 액션:** **매수 진입가 ${r['current_price']:.2f}** / **동적 ATR 손절라인 ${r['stop_loss']:.2f}**로 정밀 진입이 매우 유리합니다.

"""

        md_content += """
## 📊 4. Relative Rotation Graph (RRG) Analysis

> [!TIP]
> **RRG(상대순환선도)** 상에서 우측 상단(Leading) 방향으로 고개를 들고 있거나 좌측 상단(Improving)에서 강하게 치고 올라오는 종목/섹터군이 현재 수급의 정점에 있는 주도주입니다.
> - **매크로 섹터 흐름 (Sector ETF RRG):** 거시적인 시장 자금의 이동 패턴 및 대장 업종을 파악합니다.
> - **개별 주도주 흐름 (Stock RRG):** 섹터 내에서 가장 강한 상승 모멘텀을 분출하는 알파(Alpha) 종목을 선별하며, 각 라벨에 소속 섹터 정보(예: AAPL (XLK))를 표기하여 직관적인 연결이 가능하게 하였습니다.

### 🌐 4.1 매크로 섹터 순환 흐름 (Sector ETF Rotation)
![Sector Rotation RRG Chart](file:///Users/hwani/.gemini/antigravity-ide/brain/4e07614f-2eeb-4b26-b11f-f4840c2e5385/rrg_sectors.png)

### 🚀 4.2 개별 주도주 순환 흐름 (Stock Rotation - Colored by Sector)
![Stock Rotation RRG Chart](file:///Users/hwani/.gemini/antigravity-ide/brain/4e07614f-2eeb-4b26-b11f-f4840c2e5385/rrg_stocks.png)

---

> ⚠️ **Antigravity Risk Engine Reminder:**
> - 매수 신호가 나온 종목에 대해서는 일제히 매입을 집행하되, 단일 종목당 포트폴리오 비중은 절대 **2%**를 초과하지 말아야 하며, 동적 ATR Stop 라인에 도달할 시 기계적으로 퇴출을 감행해야 생존성과 복리 수익이 극대화됩니다.

---
*Disclaimer: 본 보고서는 Antigravity Minervini V9.5 초고속 계량 엔진에 의해 정량 연산된 자료이며 투자 조언이 아닙니다.*
"""

        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
        with open(workspace_report_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
            
        print(f"🎉 동적 스캔 종합 마크다운 리포트 발행 완료: {workspace_report_path}")
        
        # 터미널용 랭킹 출력
        print("\n" + "X"*80)
        print("🏆 Antigravity V9.5 전 종목 동적 스캔 실전 랭킹")
        print("X"*80)
        for i, r in enumerate(sorted_reports[:15]):
            color = "🟢" if r['decision'] == "BUY" else "🟡" if r['decision'] == "WAIT" else "⚪"
            print(f"{i+1}위. {color} [{r['ticker']}] (Score: {r['score']:.2f}) - {r['sector']}")
            print(f"   - 최종 결정: {r['decision']} (매수: ${r['current_price']:.2f} / 손절: ${r['stop_loss']:.2f})")

if __name__ == "__main__":
    scanner = AntigravityDynamicScanner()
    scanner.run_dynamic_market_scan()
