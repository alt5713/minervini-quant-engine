import time
import logging
import os
from datetime import datetime
from okx_fetcher import OKXFetcher
from crypto_vcp_engine import CryptoVCPEngine
from orderbook_analyzer import OrderBookAnalyzer

# 1. 로깅 설정 (24시간 가동 대비)
log_dir = "/Users/hwani/00. Antigravity폴더/26. 미너비니_Qwen버전/03_OKX_Crypto_Agent/logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(f"{log_dir}/trading_log_{datetime.now().strftime('%Y%m%d')}.log"),
        logging.StreamHandler()
    ]
)

class AntigravityCryptoAgent:
    def __init__(self, symbol='BTC/USDT:USDT', timeframe='15m'):
        self.symbol = symbol
        self.timeframe = timeframe
        self.fetcher = OKXFetcher() # API Key 없이 공용 데이터 조회 모드
        self.vcp_engine = CryptoVCPEngine()
        self.ob_analyzer = OrderBookAnalyzer()
        
        self.target_daily_profit = 0.01 # 1% 목표
        self.is_running = True

    def run_cycle(self):
        try:
            logging.info(f"--- {self.symbol} 분석 사이클 시작 ---")
            
            # 1. 데이터 수집
            df = self.fetcher.fetch_ohlcv(self.symbol, self.timeframe)
            orderbook = self.fetcher.fetch_order_book(self.symbol)
            funding_rate = self.fetcher.fetch_funding_rate(self.symbol)
            current_price = df['close'].iloc[-1]
            
            # 2. VCP 분석
            vcp_results = self.vcp_engine.analyze(df)
            
            # 3. 호가창 분석
            ob_results = self.ob_analyzer.analyze_walls(orderbook, current_price)
            
            # 4. 종합 판단 (Conflict Resolver 기초 버전)
            final_score = vcp_results['score']
            
            # 펀딩비 필터: 0.03% 이상이면 롱 진입 점수 감점 (과열 방지)
            if funding_rate > 0.0003:
                final_score -= 10
                logging.info(f"펀딩비 과열 감지: {funding_rate*100:.4f}% (-10점)")

            # 호가창 불균형 필터: 매도벽이 너무 두꺼우면 감점
            if ob_results['imbalance'] < -20:
                final_score -= 15
                logging.info(f"매도 저항벽 감지: Imbalance {ob_results['imbalance']}% (-15점)")

            # 5. 리포팅
            logging.info(f"현재가: {current_price} | VCP 점수: {vcp_results['score']} | 최종 점수: {final_score}")
            logging.info(f"상태: {vcp_results['status']} | 호가 불균형: {ob_results['imbalance']}%")
            
            if final_score >= 80:
                logging.warning(f"★★ 매수 신호 발생 (최종 점수 {final_score}) ★★")
                logging.info(f"가이드: 일일 1% 목표 진입 고려 / 손절가 {current_price * 0.993:.2f}")
            else:
                logging.info("진입 대기 중... (조건 미충족)")

        except Exception as e:
            logging.error(f"사이클 실행 중 오류 발생: {str(e)}")

    def start(self):
        logging.info("Antigravity Crypto Agent 가동 시작 (MacBook 24시간 모드)")
        while self.is_running:
            self.run_cycle()
            # 15분 봉 기준이므로 1분마다 체크하여 새로운 데이터 확인
            time.sleep(60) 

if __name__ == "__main__":
    agent = AntigravityCryptoAgent(symbol='BTC/USDT:USDT')
    agent.start()
