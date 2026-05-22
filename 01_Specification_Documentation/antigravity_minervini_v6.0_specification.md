# 🤖 Antigravity Minervini Algorithm - V6.0 Implementation Specification

⚠️ **주의사항**: 이 문서는 교육 및 연구용입니다. 실제 투자 시에는 충분한 백테스팅과 리스크 관리가 필수적입니다.

## 1. 📋 Executive Summary (최종 전략 요약)
| 항목 | 내용 |
| :--- | :--- |
| **전략명** | Antigravity Minervini Algorithm V6.0 |
| **목표** | 마크 미너버니의 SEPA & VCP 전략을 알고리즘으로 정량화하여 초성장주 발굴 시스템 구현 |
| **구조** | 3단계 파이프라인: [V5.0] 기초 → [V6.0] 전략 → [V7.2] 실행 |
| **핵심 강점** | 기관 매집 패턴, 변동성 수축, 동적 손절 (ATR 기반) 을 정량화 |

## 2. 🎯 Step 1: V5.0 기초 체력 및 트렌드 검증 (The Foundation)
| 체크포인트 | 현재 로직 | 개선 제안 |
| :--- | :--- | :--- |
| **Trend Template** | MA50 > MA150 > MA200 정배열 | ✅ 기존 유지<br>➕ 추가: EMA(50) 상승 기울기 > 0.5% 체크 |
| **RS Intensity 2.0** | 지수 대비 최근 3개월 성과 2배 탄력 | 📉 명확화: 3개월 성장률 / SPY_3개월 성장률 ≥ 1.5 |
| **Fundamental Acceleration** | EPS 성장률 가속화 확인 | 🔢 정량화: 최근 분기 대비 전 분기 성장률 증가분 ≥ +5% |
| **VCP Pattern** | 변동폭 줄어듦 & 거래량 고갈 | 🧮 대안 지표:<br>1. 20일 ATR vs 1년 평균 ATR ≤ 30%<br>2. 거래량 감소율 ≥ 40% (Dry-up) |

## 3. 🌊 Step 2: V6.0 파동 위치 및 안전마진 (Strategic Wave)
| 체크포인트 | 현재 로직 | 개선 제안 |
| :--- | :--- | :--- |
| **Elliott Wave Cycle** | 웨이브 위치 (1/3/5) 판별 | ⚠️ 수정: 고점 수 (Peak Count) 기반으로 자동 분류<br>예: 저점은 유지되지만 고점이 낮아지는 패턴 = Triangle (Wave 1) |
| **Triangle Classification** | 하향/대칭형 구분 | 📊 추가 신호: 현재 구간 내 양봉 비율 ≥ 70% 시 Wave 3 진입 조건으로 간주 |
| **RRG Sector Momentum** | 섹터 주도성 확인 | 🌐 정량화: 섹터 상위 30 종목 PER > 전체 시장 PER × 1.2 시 Leading 로 간주 |

## 4. 🛡️ Step 3: V7.2 적응형 실행 및 리스크 엔진 (Adaptive Execution)
| 체크포인트 | 현재 로직 | 개선 제안 |
| :--- | :--- | :--- |
| **Tennis Ball RS Filter** | 시장 급락 시 버티는 종목 | 🔮 구체화: RSI(14) < 20 후 회복 신호 또는 종가 > SMA20 & MA50 < SMMA20 버티기 패턴 |
| **Apex Maturity Index** | 수렴 완성도 측정 | 📐 수식: ATR 밴드 내 위치 = (High - Close) / (High - Low)<br>값이 0.2 이하 시 "완성도 90%"로 간주 |
| **ATR-Buffer Stop** | 고유의 변동성 기반 손절 | ⏳ 추가: 진입 후 3일간 Stop-Loss 이동 불가 Lock 로 불필요한 퇴출 방지 |
| **Momentum Decay** | 에너지 둔화 포착 시 익절 | 📉 트리거: RSI(14) > 70 후 하락 전환 + 거래량 감소 또는 EMA50 하향 교차 |

## 5. 🛠️ 구현 우선순위 (Implementation Priority)
1. **🔴 1위: VCP 및 Elliott Wave 정량화 (Critical)** - 알고리즘 구현 시 가장 어렵고 데이터 기반 대안 마련 필수
2. **🟡 2위: ATR 기반 동적 손절 로직 구체화 (High)** - 고정 퍼센트 대비 ATR 반영이 장기 수익률 향상 핵심
3. **🟠 3위: 백테스팅 및 거래 비용 계산 (Medium)** - 수수료, 슬리피지, 세금 고려하여 실제 수익률 검증 필요
4. **🔵 4위: 실시간 데이터 지연 시간 체크 (Medium)** - VCP는 순간 돌파 중요하므로 15분봉/초봉 데이터 접근성 확인

## 6. 📦 기술 스택 및 설치 가이드
```bash
# 필수 라이브러리 설치
pip install yfinance pandas numpy matplotlib plotly

# 백테스팅을 위한 선택 라이브러리 (선택사항)
pip install backtrader vectorbt alpaca-trade-api

# 시각화를 위한 선택 라이브러리
pip install mplfinance
```

## 7. 🧪 백테스팅 가이드 (Python 예제)
```python
"""
Backtest Framework: Antigravity Minervini V6.0
"""
from backtrader import Cerebro, Analyzer
import backtrader as bt

# cerebro 초기화
cerebro = Cerebro()

# 전략 데이터 로드
# data1 = bt.feeds.YahooDailyData(dataname='AAPL')
# cerebro.adddata(data1)

# 전략 실행
# results = cerebro.run()
```

## 8. 📌 최종 구현 체크리스트 (Checklist)
- [ ] ✅ V5.0 기초 체력 로직 구현 (MA, EPS, ATR 등 정량화 완료)
- [ ] ✅ V6.0 파동 위치 및 안전마진 로직 구현 (Triangle 패턴, Sector 분석 포함)
- [ ] ✅ V7.2 적응형 실행 로직 구현 (ATR 손절, Momentum Decay 포함)
- [ ] ⬜ 백테스팅 환경 구축 (Backtrader 또는 Zipline 사용 권장)
- [ ] ⬜ 거래소 API 연동 (선택) (Alpaca, Interactive Brokers 등)
- [ ] ⬜ 시각화 및 리포팅 시스템 (차트, 수익률 곡선 작성)

## 9. 📈 성과 지표 및 모니터링
| 지표 | 목표 기준 | 계산식 |
| :--- | :--- | :--- |
| **Win Rate** | ≥ 50% | 성공 매매 횟수 / 총 매매 횟수 |
| **Profit Factor** | ≥ 1.5 | (순이익 + 이익) / (손실 - 비용) |
| **Sharpe Ratio** | ≥ 1.2 | 초과 수익률 / 변동성 |
| **Max Drawdown** | ≤ 10% | 최고 가격에서 최저 가격까지 손실 비율 |

## 10. ⚠️ 리스크 관리 및 주의사항 (Mandatory)
- 개인 계좌정보, API 키는 절대 공유 금지
- 실제 투자 전에는 Paper Trading 모드로 최소 3개월 테스트 필수
- 손절 로직은 동적止损 (ATR) 기반으로 설정
- 한 종목당 포트폴리오 노출 비율 최대 2% 제한 권장
- 시장 변동성 급변 시 수동 개입을 위해 모니터링 시스템 유지

## 11. 🔄 버전 관리 및 변경 로그
- **V1.0**: 초기 전략 설계 완료
- **V5.0**: 기초 체력 (Fundamentals) 로직 추가
- **V6.0**: 파동 위치 및 안전마진 필터 추가
- **V7.2**: 적응형 실행 및 리스크 엔진 완성 (2026-05-14)
