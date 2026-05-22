import numpy as np

class OrderBookAnalyzer:
    def __init__(self, depth_pct=0.015): # 현재가 대비 1.5% 이내 호가 분석
        self.depth_pct = depth_pct

    def analyze_walls(self, orderbook, current_price):
        """매수/매도 호가의 벽(Wall) 비중 분석"""
        if not orderbook:
            return {"bid_wall_score": 0, "ask_wall_score": 0, "status": "No Data"}

        limit_price_ask = current_price * (1 + self.depth_pct)
        limit_price_bid = current_price * (1 - self.depth_pct)

        # 매도벽 (Asks)
        asks = np.array(orderbook['asks'])
        relevant_asks = asks[asks[:, 0] <= limit_price_ask]
        ask_volume = np.sum(relevant_asks[:, 1]) if len(relevant_asks) > 0 else 0

        # 매수벽 (Bids)
        bids = np.array(orderbook['bids'])
        relevant_bids = bids[bids[:, 0] >= limit_price_bid]
        bid_volume = np.sum(relevant_bids[:, 1]) if len(relevant_bids) > 0 else 0

        # 비중 계산 (단순 비율)
        total_relevant_vol = ask_volume + bid_volume
        if total_relevant_vol == 0:
            return {"bid_wall_score": 50, "ask_wall_score": 50, "imbalance": 0}

        bid_ratio = (bid_volume / total_relevant_vol) * 100
        ask_ratio = (ask_volume / total_relevant_vol) * 100

        # 불균형 정도 (매수벽이 더 두꺼우면 상승 유리)
        imbalance = bid_ratio - ask_ratio

        return {
            "bid_ratio": round(bid_ratio, 2),
            "ask_ratio": round(ask_ratio, 2),
            "imbalance": round(imbalance, 2),
            "status": "Healthy" if abs(imbalance) < 20 else "Skewed"
        }
