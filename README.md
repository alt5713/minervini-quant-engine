# 🤖 Antigravity Minervini V9.5 - 설치 및 사용 설명서
> **Statistical Optimization & Adaptive Risk Engine**

본 시스템은 월가의 전설적인 트레이더 **마크 미너버니(Mark Minervini)**의 **SEPA(특정 진입 시점 분석)** 및 **VCP(변동성 수축 패턴)** 전략을 현대적인 퀀트 기술과 결합하여 정량화한 최첨단 자동 주도주 발굴 및 리스크 분석 엔진입니다. 

미국 시장의 기술적 정배열, VCP 수렴도, 기관 스마트 머니 유입(VPA), 실시간 옵션 시장의 미결제약정(Call Walls/Max Pain)을 융합 연산하여 최종 **BUY / WAIT** 결정을 산출하고, Bloomberg Terminal 스타일의 **RRG(Relative Rotation Graph) 시각화**를 제공합니다.

---

## 📂 1. 전체 시스템 구성 및 디렉토리 구조

프로젝트는 모듈화된 파이프라인 구조로 설계되어 있어, 유지보수와 기능 확장이 매우 용이합니다.

```text
26. 미너비니_Qwen버전/
├── 01_Specification_Documentation/
│   ├── antigravity_minervini_v6.0_specification.md  # 알고리즘 사양서
│   └── antigravity_crypto_v1.0_specification.md      # 크립토 버전 사양서
├── 02_Source_Code/
│   ├── main_agent.py          # [Core] 마스터 파이프라인 실행 및 의사결정 통합 에이전트
│   ├── core_logic.py          # [V5.0/V6.0] Trend Template, VCP 수렴, Elliott Wave 및 삼각수렴 판별
│   ├── smart_money.py         # [V7.5] Force Index 기반 자금 흐름, VPA 매집봉, 나스닥 국면 분석
│   ├── options_engine.py      # [V8.0] 실시간 미국 옵션 체인 분석 (Max Pain, Call Walls, IV 프리미엄)
│   ├── conflict_resolver.py   # [V9.5] VCP와 옵션 데이터 간 충돌 회피 및 통계적 가중치 보정
│   ├── risk_management.py     # [V7.2] ATR 기반 동적 손절매(Stop-Loss) 계산기
│   ├── rrg_visualizer.py      # [RRG] Bloomberg 스타일의 섹터/종목 상대 회전 그래프 생성기
│   ├── data_fetcher.py        # [Data] yfinance 데이터 고속 다운로더 및 시장 지수 분석기
│   └── scan_us_market.py      # [Execution] 미국 시장 스캔 및 RRG 자동 생성 통합 실행 스크립트
├── rrg_sectors.png            # 실시간 생성된 섹터 RRG 차트 이미지
└── rrg_stocks.png             # 실시간 생성된 개별 종목 RRG 차트 이미지
```

---

## 🛠️ 2. 환경 설정 및 설치 방법 (Installation)

본 시스템은 Python 3.8 이상 환경에서 최적으로 동작합니다. 아래 단계를 따라 터미널(Terminal)에서 빠르게 설치를 진행할 수 있습니다.

### Step 1. 리포지토리 폴더로 이동
사용자의 터미널을 열고 본 프로젝트가 포함된 폴더로 이동합니다.
```bash
cd "/Users/hwani/00. Antigravity폴더/26. 미너비니_Qwen버전"
```

### Step 2. 필수 라이브러리 설치
주가 데이터 수집, 데이터 처리 및 시각화를 위한 핵심 패키지들을 설치합니다.
```bash
pip install yfinance pandas numpy matplotlib
```
*   `yfinance`: 야후 파이낸스 실시간 주가 및 옵션 체인 데이터 수집
*   `pandas` & `numpy`: 퀀트 지표 고속 연산 및 데이터 조작
*   `matplotlib`: 고품질 RRG 시각화 그래픽 렌더링

---

## 🚀 3. 프로그램 실행 방법 (Quick Start)

설치가 완료되면, 미국 주식 시장을 종합 분석하고 RRG 차트를 그리는 통합 실행 스크립트를 즉시 실행할 수 있습니다.

```bash
python 02_Source_Code/scan_us_market.py
```

### 💡 실행 시 진행 단계
1.  **시장 상태 판별 (Market Regime)**: S&P 500 (`SPY`) 지수가 50일선 위에 있는지 확인합니다. 만약 지수가 50일선 아래에 있으면 하락장으로 인지하여 자동으로 진입을 차단(Entry Restriction)하여 소중한 투자금을 보호합니다.
2.  **종목별 퀀트 분석**: `sector_stock_map`에 지정된 모든 종목의 기술적 정배열, VCP 수축 상태, 자금 유입도(VPA), 옵션 장벽을 순차적으로 초고속 분석합니다.
3.  **마스터 리포트 출력**: 가중치가 반영된 최종 스코어를 기준으로 순위를 매겨 추천 **BUY / WAIT** 목록과 함께 **적정 매수 가격 및 ATR 기반 동적 손절 라인**을 터미널에 시각적으로 뿌려줍니다.
4.  **RRG 차트 자동 저장**: 분석이 끝나면 최상위 경로에 `rrg_sectors.png`(섹터 궤적)와 `rrg_stocks.png`(종목 궤적)가 블룸버그 스타일의 미려한 차트로 즉시 렌더링되어 저장됩니다.

---

## 📊 4. 핵심 옵션 및 사용자 설정 가이드

사용자의 성향과 분석 목적에 맞게 소스 코드 내의 옵션을 변경하여 사용할 수 있습니다.

### ① RRG 꼬리 길이 조절 및 벤치마크 변경 (`rrg_visualizer.py` / `scan_us_market.py`)
`rrg_visualizer.py`는 기본적으로 S&P 500(`SPY`)을 벤치마크 기준으로 삼고, **최근 15일간의 회전 궤적**을 시각화합니다.
*   **꼬리 길이 변경**: `scan_us_market.py` 내의 `tail_len` 매개변수를 조절하여 분석 주기를 쉽게 늘리거나 줄일 수 있습니다.
    ```python
    # scan_us_market.py L37-38
    viz.generate_sector_rrg(sector_stock_map, rrg_sectors_path, tail_len=15) # 15일에서 다른 값(예: 30)으로 수정 가능
    ```

### ② 관심 섹터 및 종목 커스터마이징 (`scan_us_market.py`)
기본적으로 주요 주도 섹터(XLK: 기술, XLC: 통신, XLY: 임의소비재, XLE: 에너지, XLF: 금융)와 그 대표 주도주들(NVDA, MSFT, AAPL, PLTR, META, AMZN, TSLA, COIN, MSTR 등)이 기본 세팅되어 있습니다. 분석할 종목군을 변경하고 싶다면 `sector_stock_map`을 편집하세요.
```python
# scan_us_market.py L8-14
sector_stock_map = {
    'XLK': ['NVDA', 'AVGO', 'MSFT', 'AAPL', 'PLTR', 'PANW', 'ANET', 'VRT'],
    'XLC': ['GOOGL', 'META', 'NFLX'],
    'XLY': ['AMZN', 'TSLA', 'BROS'],
    # 원하는 섹터와 주식 티커를 자유롭게 추가/제거 가능합니다.
}
```

### ③ 한국 주식 분석 모드 자동 연동 (예외 처리 지원)
본 엔진은 글로벌 확장성을 완벽 지원합니다. 만약 종목 명에 `.KQ`(코스닥) 또는 `.KS`(코스피) 접미사가 붙어있는 한국 주식의 경우, 옵션 데이터가 부재하므로 **자동으로 거래량 분석 기반의 Fallback Volume Logic**으로 우회하여 분석을 완벽하게 끝마칩니다.
*   **한국 주식 분석 맵 예시**:
    ```python
    korean_portfolio = {
        'SEMICON': ['005930.KS', '000660.KS'], # 삼성전자, SK하이닉스
        'BATTERY': ['051910.KS', '373220.KS']  # LG화학, LG에너지솔루션
    }
    ```

---

## 📈 5. RRG(상대 회전 그래프) 사분면 해석법

생성된 `rrg_sectors.png` 및 `rrg_stocks.png` 이미지 차트는 블룸버그 터미널 스타일로 4가지 색상 사분면을 가집니다.

| 사분면 (Quadrant) | 배경색 | 의미 및 투자 전략 |
| :--- | :--- | :--- |
| **LEADING (주도)** | 🟢 연두색 | 시장 대비 추세(RS-Ratio)와 모멘텀(RS-Momentum)이 모두 최상인 상태. **적극 매수 및 홀딩 구간.** |
| **WEAKENING (약화)** | 🟡 노란색 | 추세는 양호하나 단기 모멘텀이 하락하며 힘이 빠지는 구간. **추세가 꺾이기 전 분할 익절 고려.** |
| **LAGGING (낙오)** | 🔴 분홍색 | 추세와 모멘텀 모두 시장을 언더퍼폼하는 소외 상태. **매수 기피 및 손절 구간.** |
| **IMPROVING (개선)** | 🔵 파란색 | 추세는 아직 시장 평균 이하이나 모멘텀이 급상승하며 치고 올라가는 단계. **가장 먼저 선취매 후보군으로 분류.** |

> 💡 **RRG 차트의 시각적 요소 특장점**
> *   **Fading Tail (점차 진해지는 꼬리)**: 과거(연하고 얇음)에서 현재(진하고 굵음)로의 흐름을 시각화합니다.
> *   **Trail Dots (트레일 닷)**: 꼬리 궤적 위에 표시된 점으로 날짜별 진행 속도(점 간격이 넓을수록 급격한 모멘텀 변화)를 보여줍니다.
> *   **Flow Arrow (화살표)**: 머리 부분의 화살표 방향을 통해 내일 어느 사분면으로 전이될지 방향을 즉시 투영합니다.

---

## 🛡️ 6. 퀀트 리스크 관리 규칙 (ATR Stop)
본 시스템은 단순 퍼센트(%) 손절이 아닌, 종목 고유의 변동성을 반영하는 **ATR-Buffer Stop (V7.2 리스크 엔진)**을 탑재하고 있습니다.
*   최근 20일간의 ATR(Average True Range) 변동폭을 연산하여, 주가의 일시적인 노이즈 파동에 털리지 않는 최적의 하단 손절선(`stop_loss`)을 자동으로 제시합니다.
*   **가중치 규칙**: 나스닥 50일 이동평균선 상회 여부에 따라 최종 보너스 점수에 가중치를 주어 하락장에서는 보수적인 점수(0.8배)를, 상승장에서는 적극적인 점수(1.2배)를 부여해 포트폴리오를 보호합니다.
