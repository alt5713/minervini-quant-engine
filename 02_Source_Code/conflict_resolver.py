import numpy as np

class AdvancedConflictResolver:
    """
    V9.5: Dynamic Weighting & Volatility Normalization Engine
    """
    def __init__(self, historical_vcp_stats=None):
        # 과거 통계가 없을 경우 기본값 (평균 60, 표준편차 15)
        self.historical_vcp = historical_vcp_stats or {'mean': 60, 'std': 15}

    def resolve(self, vcp_score, options_data, fallback_signal=None, market_regime=None):
        adj_weight = 1.0
        decision = "HOLD"
        
        # 1. Market Regime Safety Filter (하락장 강제 제한)
        if market_regime and market_regime.get('state') == 'Bearish':
            return "WAIT", 0.6
            
        # 2. Wall Resistance Logic (Volatility Based)
        wall_pressure = self._calculate_wall_pressure(options_data)
        
        if wall_pressure['is_critical']:
            decision = "WAIT"
            # 저항벽 강도(0~1)에 따라 가중치를 선형적으로 축소 (최대 0.5까지)
            adj_weight = max(0.5, 1.0 - (wall_pressure['strength'] * 0.5))
        else:
            # 3. VCP Strength Normalization (Z-Score 적용)
            z_score = (vcp_score - self.historical_vcp['mean']) / self.historical_vcp['std']
            
            # 통계적으로 유의미한 돌파 신호 (Z-Score > 1.0)
            if vcp_score >= 70 and z_score > 1.0:
                adj_weight += 0.2
                
                # 수급 확증 신호 추가 (Confirmations)
                if fallback_signal == 'STRONG_SIGNAL' or (options_data and options_data.get('avg_iv', 0) < 0.6):
                    decision = "BUY"
                    adj_weight += 0.2
            else:
                decision = "HOLD"

        # 4. Final Risk Adjustment (Market Volatility Cap)
        if market_regime:
            vol_factor = market_regime.get('volatility_factor', 1.0)
            # 변동성이 높을수록 가중치를 제한하여 리스크 관리 (1/vol_factor)
            adj_weight = min(1.5, adj_weight * (1.0 / vol_factor))
            
        return decision, adj_weight

    def _calculate_wall_pressure(self, options_data):
        if not options_data or not options_data.get('call_walls'):
            return {'is_critical': False, 'strength': 0}
            
        current_price = options_data['current_price']
        call_walls = options_data['call_walls']
        total_oi = options_data.get('total_call_oi', 1)
        
        # 가장 가까운 저항벽 찾기
        closest_wall = min(call_walls, key=lambda x: abs(x['strike'] - current_price))
        dist_pct = abs(closest_wall['strike'] - current_price) / current_price
        
        # 해당 벽의 집중도 (OI 비중)
        oi_concentration = closest_wall['open_interest'] / total_oi if total_oi > 0 else 0
        
        # 4% 이내에 있고, 전체 OI의 20% 이상이 집중된 벽일 경우 'Critical'로 간주
        is_critical = dist_pct < 0.04 and oi_concentration > 0.2
        
        return {'is_critical': is_critical, 'strength': oi_concentration}
