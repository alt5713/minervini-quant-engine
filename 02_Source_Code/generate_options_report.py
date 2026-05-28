import os
import sys
import argparse
import shutil
from datetime import datetime

# Add current folder to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from options_engine import OptionsInsightEngine
from options_visualizer import OptionsVisualizer

def generate_report(ticker):
    print("=" * 80)
    print(f"🚀 Antigravity Options Trading Planner & Report Generator for: {ticker}")
    print("=" * 80)
    
    # 1. Fetch data
    engine = OptionsInsightEngine()
    print(" > Fetching options chain data and calculating stats...")
    data = engine.analyze_options_data(ticker)
    if not data or data['status'] != "Success":
        print(f"❌ Failed to fetch or analyze options data for {ticker}. Option chain may not exist.")
        return False

    # 2. Paths
    date_str = datetime.now().strftime('%Y-%m-%d')
    workspace_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    workspace_charts_dir = os.path.join(workspace_root, "options_charts")
    os.makedirs(workspace_charts_dir, exist_ok=True)
    
    workspace_chart_path = os.path.join(workspace_charts_dir, f"options_{ticker}_{date_str}.png")
    workspace_report_path = os.path.join(workspace_root, f"options_trading_plan_{ticker}_{date_str}.md")

    # Conversation brain paths (Artifact Destination)
    brain_dir = "/Users/hwani/.gemini/antigravity-ide/brain/c25dc4e5-ae72-42a9-861f-8baeecbd6473"
    os.makedirs(brain_dir, exist_ok=True)
    brain_chart_path = os.path.join(brain_dir, f"options_{ticker}_{date_str}.png")
    brain_report_path = os.path.join(brain_dir, f"options_trading_plan_{ticker}_{date_str}.md")

    # 3. Generate visualizer dashboard
    print(" > Generating professional 3-panel dashboard chart...")
    viz = OptionsVisualizer()
    viz.generate_dashboard(data, workspace_chart_path)
    
    # Copy chart to brain folder for artifact integration
    shutil.copy(workspace_chart_path, brain_chart_path)
    print(f" > Chart successfully saved to both workspace and brain artifact folders.")

    # 4. Formulate markdown trading plan
    current_price = data['current_price']
    max_pain = data['max_pain']
    call_wall = data['call_wall']
    put_wall = data['put_wall']
    pcr_oi = data['pcr_oi']
    pcr_vol = data['pcr_vol']
    avg_iv = data['avg_iv']
    dte = data['days_to_expiry']
    expiry = data['selected_expiry']

    # Buy target ranges
    one_sigma_l = data['one_sigma_lower']
    one_sigma_u = data['one_sigma_upper']
    one_sigma_l_30d = data['one_sigma_lower_30d']
    one_sigma_u_30d = data['one_sigma_upper_30d']

    # Smart buy zone calculation (statistical support confluence)
    buy_bottom = one_sigma_l_30d
    buy_top = min(put_wall if put_wall else current_price, current_price)
    if buy_bottom > buy_top:
        buy_bottom, buy_top = buy_top, buy_bottom

    # Smart sell target calculation (statistical resistance confluence)
    sell_bottom = max(call_wall if call_wall else current_price, current_price)
    sell_top = one_sigma_u_30d
    if sell_bottom > sell_top:
        sell_bottom, sell_top = sell_top, sell_bottom

    # Sentiment analysis
    pcr_sentiment = "BULLISH" if pcr_oi < 0.65 else "BEARISH" if pcr_oi > 1.1 else "NEUTRAL"
    vol_smile_bias = "CALL SKEW (Bullish demand)" if (call_wall and call_wall > current_price and data['total_call_oi'] > data['total_put_oi']) else "PUT SKEW (Downside protection bid)"

    now_str = datetime.now().strftime('%Y-%m-%d %H:%M')

    md_content = f"""# 📊 Antigravity Options Trading Plan: {ticker}

> [!NOTE]
> **Plan Generation Time:** {now_str} (KST)  
> **Target Stock:** **{ticker}** | **Current Spot Price:** **${current_price:.2f}**
> **Selected Expiration Date:** **{expiry}** (DTE: **{dte}** days | Standard Monthly Expiry)

---

## 🎯 1. Statistical Execution Zones

By synthesizing the **1-Sigma Expected Move (Standard Deviation)** and institutional option wall structures (Call Wall/Put Wall), we establish high-probability price zones for swing planning.

```mermaid
graph TD
    classDef resistance fill:#fee2e2,stroke:#ef4444,stroke-width:2px;
    classDef support fill:#ecfdf5,stroke:#10b981,stroke-width:2px;
    classDef neutral fill:#f1f5f9,stroke:#64748b,stroke-width:1px;

    TopRange["Upper 1-Sigma (30d): ${one_sigma_u_30d:.2f}"] --> SellZone
    CallWall["Call Wall: ${(call_wall if call_wall else 0.0):.2f}"] --> SellZone
    SellZone["💰 Short-Term Profit Target Zone<br>(${sell_bottom:.2f} - ${sell_top:.2f})"]:::resistance

    Spot["Current Spot Price: ${current_price:.2f}"]:::neutral

    BuyZone["📈 Optimal Buy Accumulation Zone<br>(${buy_bottom:.2f} - ${buy_top:.2f})"]:::support
    PutWall["Put Wall: ${(put_wall if put_wall else 0.0):.2f}"] --> BuyZone
    LowRange["Lower 1-Sigma (30d): ${one_sigma_l_30d:.2f}"] --> BuyZone
```

### 📈 매수 집행 및 축적 구간 (Optimal Buy Accumulation Zone)
*   **통계적 가격대:** **${buy_bottom:.2f} ~ ${buy_top:.2f}**
*   **전략적 근거:**
    - 이 구간은 시장 참여자들이 주가 하락 시 강력한 방어선을 구축한 **풋월 (Put Wall: {f"${put_wall:.2f}" if put_wall else "N/A"})**과 **30일 기준 1시그마 하한선 (${one_sigma_l_30d:.2f})**이 겹치는 **통계적 강력한 매수 지지선**입니다.
    - 해당 범위 내로 주가가 조정받을 시, 마켓메이커들의 매수 델타 헤징 물량이 유입되며 강한 기술적 반등이 연출될 가능성이 매우 높습니다.
    - **실전 팁:** 분할 매수 진입선으로 설정하여 최적의 Risk-Reward Ratio를 확보하십시오.

### 💰 단기 목표가 및 청산 구간 (Short-Term Profit Target Zone)
*   **통계적 가격대:** **${sell_bottom:.2f} ~ ${sell_top:.2f}**
*   **전략적 근거:**
    - 이 구간은 거대 기관 투자자들의 콜옵션 매도 포지션이 집중되어 있어 돌파하기 매우 어려운 **콜월 (Call Wall: {f"${call_wall:.2f}" if call_wall else "N/A"})**과 **30일 기준 1시그마 상한선 (${one_sigma_u_30d:.2f})**이 결합된 **통계적 단기 저항선**입니다.
    - 주가가 이 범위에 진입할 경우 마켓메이커들이 매수했던 헤징용 현물 주식을 대량 매도하여 상승 탄력이 둔화되기 쉽습니다.
    - **실전 팁:** 단기 스윙 거래 시 이 구간을 최적의 분할 익절 목표선으로 설정하십시오.

---

## ⚡ 2. Options Market Sentiment & Skew Metrics

| 지표명 (Metric) | 수치 및 상태 (Value) | 해석 및 전략적 의미 (Interpretation) |
| :--- | :---: | :--- |
| **Max Pain Price** | **${max_pain:.2f}** | 만기 시점에 옵션 매수자들이 가장 큰 손실을 입는 가격대로, 만기가 임박할수록 강력한 **가격 자석 효과(Gravitational Pull)** 역할을 수행합니다. 현재가(${current_price:.2f}) 대비 만기 시 수렴 방향성을 예측할 수 있습니다. |
| **Average Implied Volatility** | **{avg_iv*100:.1f}%** | ATM(등가격) 인근의 평균 내재 변동성입니다. 변동성이 낮을수록 프리미엄이 저렴하므로 옵션 매수 전략이 유리하고, 높을수록 매도 전략이 유리합니다. |
| **Premium Level** | **{data['premium_status']}** | 현재 내재 변동성에 따른 프리미엄 상태입니다. HEAVY 상태인 경우 옵션 고평가 구간으로 스프레드 또는 커버드콜 등의 매도형 전략이 권장되며, LIGHT 상태인 경우 돌파 매수 전략에 적합합니다. |
| **Put/Call Ratio (OI)** | **{pcr_oi:.2f}** | 미결제약정 기준 풋/콜 비율입니다. 통상적으로 0.7 이하는 불마켓(강세 심리), 1.0 이상은 베어마켓(약세 심리)을 시각화합니다. (현재: **{pcr_sentiment}** 심리 우세) |
| **Put/Call Ratio (Volume)** | **{pcr_vol:.2f}** | 당일 거래량 기준 풋/콜 비율로, 실시간 단기 자금 유입의 방향을 알려줍니다. |

---

## 📊 3. Options Visualization Dashboard

아래 대시보드는 실시간 옵션 체인을 완벽히 가시화한 3개 핵심 그래프의 결과물입니다:
1. **왼쪽 (OI Profile):** 세로축 가격(Strike) 대비 미결제약정 분포 및 1-Sigma 밴드, 옵션 벽의 다이내믹 융합.
2. **우상단 (IV Smile):** 콜/풋의 프리미엄 Skew 구조(다운사이드 풋 프리미엄 비중 확인).
3. **우하단 (Option Month):** 다가오는 만기별 거래량 분포(만기 선택의 정당성 확보).

![Options Dashboard for {ticker}](options_{ticker}_{date_str}.png)

---

> [!WARNING]
> **리스크 경고 및 실전 대응 원칙:**
> - 옵션 데이터는 실시간으로 변화하는 시장 참여자들의 헤징 포지션을 반영하므로, 본 계획서는 다음 주요 이벤트(실적 발표, CPI 등)나 만기일 전환 시 업데이트가 필요합니다.
> - 통계적 1시그마 가격 범위(${one_sigma_l:.2f} ~ ${one_sigma_u:.2f})는 현재 변동성 기준 **{expiry} 만기**까지 주가가 이 범위 내에서 마감할 확률이 **68%**임을 의미합니다. 하단 1시그마선(${one_sigma_l:.2f})이 완전히 하향 붕괴될 경우, 즉각적인 스톱로스(Stop-Loss)를 가동하십시오.

---
*Disclaimer: 본 보고서는 Antigravity Options Insight Engine에 의해 정량 연산된 자료이며 투자 조언이 아닙니다.*
"""

    with open(workspace_report_path, 'w', encoding='utf-8') as f:
        f.write(md_content)
    with open(brain_report_path, 'w', encoding='utf-8') as f:
        f.write(md_content)

    print(f"🎉 Beautiful Options Markdown Trading Plan generated successfully:")
    print(f" - Workspace: {workspace_report_path}")
    print(f" - Brain Artifact: {brain_report_path}")
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Antigravity Options Trading Planner")
    parser.add_argument("ticker", type=str, nargs="?", default="TSLA", help="Stock ticker symbol (e.g. TSLA, NVDA)")
    args = parser.parse_args()
    
    generate_report(args.ticker.upper())
