# Antigravity Crypto V1.0: Intraday Minervini for OKX

## 1. 개요 (Overview)
본 시스템은 기존 Minervini V9.5 (주식용) 로직을 암호화폐 시장의 특성(24/7 가동, 고변동성, 레버리지)에 맞춰 변형한 자동 매매 알고리즘입니다. 목표는 나스닥 선물 수준의 변동성을 활용하여 **일일 1% 복리 수익**을 추구합니다.

## 2. 핵심 로직: Intraday VCP (Volatility Contraction Pattern)
암호화폐 시장의 15분/1시간 봉에서도 주가 수축 패턴은 유효합니다.

- **Phase 1: Market Regime Gate (Crypto)**
  - BTC/USDT 1시간 봉 기준 20EMA 상단 여부.
  - 펀딩비(Funding Rate) 분석: 0.03% 이상 과열 시 롱 진입 제한 (반대로 -0.03% 이하면 숏 주의).
- **Phase 2: Intraday VCP Setup**
  - 최근 20~50개 캔들 내 변동성(ATR)이 점진적으로 감소하는 구간 포착.
  - 거래량이 평균(Z-Score) 대비 낮아지며 에너지를 응축하는 'Quiet period' 탐색.
- **Phase 3: Liquidity Insight (OKX Order Flow)**
  - OKX Order Book Depth 분석: 현재가 상하단 1% 이내의 매수/매도 벽(Walls) 비중 계산.
  - 미체결약정(OI) 변화율 분석: 가격 상승 + OI 상승 = 강력한 추세 확인.
- **Phase 4: Conflict Resolver (Statistical)**
  - VCP 신호와 오더북 저항이 충돌할 경우, Z-Score를 통해 진입 강도 조절.

## 3. 매매 전략 (Execution Strategy)
- **대상**: BTC/USDT, ETH/USDT (무기한 선물)
- **타임프레임**: 15분 (주 진입), 1시간 (추세 확인)
- **목표 수익**: 1% (익절 라인 설정)
- **손절 라인**: 진입가 기준 -0.5% ~ -0.7% (ATR 기반 타이트한 손절)
- **레버리지**: 3x ~ 5x 권장 (1% 목표 수익 달성을 위한 최적화)

## 4. 파일 구조 (File Structure)
- `okx_fetcher.py`: CCXT를 이용한 실시간 데이터 수집.
- `crypto_vcp_engine.py`: 15분봉 기반 변동성 수축(VCP) 분석 엔진.
- `orderbook_analyzer.py`: OKX 오더북 매수/매도벽 불균형 분석.
- `okx_main_agent.py`: 24시간 가동 루프, 로깅, 최종 의사결정 로직.
- `test_one_cycle.py`: 단일 사이클 작동 테스트용 스크립트.

## 5. 실행 방법 (How to Run)
1. **필수 라이브러리 설치:** `python3 -m pip install ccxt pandas numpy`
2. **테스트 실행:** `python3 test_one_cycle.py` (단일 분석 결과 확인)
3. **24시간 가동:** `python3 okx_main_agent.py` (로그는 `./logs/` 폴더에 저장됨)

## 6. 맥북 에어 M2 최적화 (24/7 모드)
- 시스템 리소스 사용을 최소화하기 위해 1분 단위로 상태를 체크하며, 데이터 수집 시에만 활성화됩니다.
- 네트워크 단절 시 자동 재시도 로직이 포함되어 있어 24시간 안정적인 테스트가 가능합니다.
