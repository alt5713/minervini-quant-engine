import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.patches as patches

class RRGVisualizer:
    def __init__(self):
        self.benchmark = 'SPY'
        # Modern color palette for sectors and stocks
        self.sector_colors = {
            'XLK': '#1f77b4',  # Deep Blue
            'XLC': '#ff7f0e',  # Vibrant Orange
            'XLY': '#2ca02c',  # Forest Green
            'XLE': '#d62728',  # Crimson Red
            'XLF': '#9467bd',  # Purple
            'XLI': '#8c564b',  # Brown
            'XLB': '#e377c2',  # Pink
            'XLV': '#bcbd22',  # Olive
            'XLU': '#17becf'   # Teal
        }
        self.default_color_map = plt.colormaps.get_cmap('tab10')

    def _draw_concentric_ellipses(self, ax, half_width_x, half_width_y):
        """벤치마크 중심점(100, 100) 기준으로 가로/세로 비율에 맞춘 동심 타원형 그리드 그리기"""
        max_val = max(half_width_x, half_width_y)
        if max_val < 1.0:
            steps = [0.2, 0.4, 0.6, 0.8]
        elif max_val < 3.0:
            steps = [0.5, 1.0, 1.5, 2.0, 2.5]
        elif max_val < 6.0:
            steps = [1.0, 2.0, 3.0, 4.0, 5.0]
        else:
            step = np.ceil(max_val / 5.0)
            steps = [step * i for i in range(1, 6)]
            
        for s in steps:
            # s의 스케일에 비례하여 가로 반지름 rx, 세로 반지름 ry 계산
            rx = s * (half_width_x / max_val)
            ry = s * (half_width_y / max_val)
            
            if rx > half_width_x or ry > half_width_y:
                continue
                
            # 동심 타원형 패치 추가 (width=2*rx, height=2*ry)
            ellipse = patches.Ellipse((100, 100), width=2*rx, height=2*ry, fill=False, 
                                      color='#555555', linestyle=':', linewidth=0.8, alpha=0.2)
            ax.add_patch(ellipse)
            # 45도 방향선 위에 반지름 라벨 표시 (눈금 가독성 확보)
            ax.text(100 + rx * 0.707, 100 + ry * 0.707, f"{s:.1f}", 
                    fontsize=8, color='#777777', alpha=0.45, ha='center', va='center')

    def _setup_quadrants(self, ax, half_width_x, half_width_y):
        """사분면에 Bloomberg 스타일의 부드러운 파스텔톤 배경색 채우기 및 상세 전략 라벨 배치"""
        x_min = 100 - half_width_x
        x_max = 100 + half_width_x
        y_min = 100 - half_width_y
        y_max = 100 + half_width_y

        # Quadrant background fills (highly transparent)
        # Leading (Top Right): Green
        rect_leading = patches.Rectangle((100, 100), half_width_x, half_width_y, linewidth=0, facecolor='#E2F0D9', alpha=0.25)
        # Improving (Top Left): Blue
        rect_improving = patches.Rectangle((x_min, 100), half_width_x, half_width_y, linewidth=0, facecolor='#D9E1F2', alpha=0.25)
        # Lagging (Bottom Left): Pink/Red
        rect_lagging = patches.Rectangle((x_min, y_min), half_width_x, half_width_y, linewidth=0, facecolor='#FCE4D6', alpha=0.25)
        # Weakening (Bottom Right): Yellow/Orange
        rect_weakening = patches.Rectangle((100, y_min), half_width_x, half_width_y, linewidth=0, facecolor='#FFF2CC', alpha=0.25)

        ax.add_patch(rect_leading)
        ax.add_patch(rect_improving)
        ax.add_patch(rect_lagging)
        ax.add_patch(rect_weakening)

        # 동심 타원 그리드 그리기
        self._draw_concentric_ellipses(ax, half_width_x, half_width_y)

        # Draw axis lines
        ax.axhline(100, color='#555555', linestyle='-', linewidth=1.5, alpha=0.6)
        ax.axvline(100, color='#555555', linestyle='-', linewidth=1.5, alpha=0.6)

        # Quadrant text labels & Detailed strategies (Pure English to prevent font rendering errors)
        # 1. LEADING (Top Right)
        ax.text(100 + half_width_x * 0.5, 100 + half_width_y * 0.82, 'LEADING', 
                fontsize=15, color='#385723', fontweight='bold', alpha=0.9, ha='center', va='center')
        ax.text(100 + half_width_x * 0.5, 100 + half_width_y * 0.64, 'Market Leaders\n[Active Buy / Hold]\n(Active Buy / Hold)', 
                fontsize=8.5, color='#2c421b', fontweight='bold', alpha=0.85, ha='center', va='center',
                bbox=dict(boxstyle="round,pad=0.3", facecolor='#f4fbf1', edgecolor='#385723', lw=0.6, alpha=0.8))

        # 2. IMPROVING (Top Left)
        ax.text(100 - half_width_x * 0.5, 100 + half_width_y * 0.82, 'IMPROVING', 
                fontsize=15, color='#1F4E79', fontweight='bold', alpha=0.9, ha='center', va='center')
        ax.text(100 - half_width_x * 0.5, 100 + half_width_y * 0.64, 'Trend Reversal\n[Watch / Accumulate]\n(Watch / Accumulate)', 
                fontsize=8.5, color='#183c5e', fontweight='bold', alpha=0.85, ha='center', va='center',
                bbox=dict(boxstyle="round,pad=0.3", facecolor='#f2f6fc', edgecolor='#1F4E79', lw=0.6, alpha=0.8))

        # 3. LAGGING (Bottom Left)
        ax.text(100 - half_width_x * 0.5, 100 - half_width_y * 0.82, 'LAGGING', 
                fontsize=15, color='#C65911', fontweight='bold', alpha=0.9, ha='center', va='center')
        ax.text(100 - half_width_x * 0.5, 100 - half_width_y * 0.64, 'Underperforming\n[Avoid / Stop-Loss]\n(Avoid / Stop-Loss)', 
                fontsize=8.5, color='#94420c', fontweight='bold', alpha=0.85, ha='center', va='center',
                bbox=dict(boxstyle="round,pad=0.3", facecolor='#fff7f2', edgecolor='#C65911', lw=0.6, alpha=0.8))

        # 4. WEAKENING (Bottom Right)
        ax.text(100 + half_width_x * 0.5, 100 - half_width_y * 0.82, 'WEAKENING', 
                fontsize=15, color='#7F6000', fontweight='bold', alpha=0.9, ha='center', va='center')
        ax.text(100 + half_width_x * 0.5, 100 - half_width_y * 0.64, 'Momentum Slowdown\n[Take Profit / Caution]\n(Take Profit / Caution)', 
                fontsize=8.5, color='#614900', fontweight='bold', alpha=0.85, ha='center', va='center',
                bbox=dict(boxstyle="round,pad=0.3", facecolor='#fffdf2', edgecolor='#7F6000', lw=0.6, alpha=0.8))

    def _plot_tail_with_flow(self, ax, r_vals, m_vals, ticker, color, is_sector=False, label_text=None):
        """꼬리 부분에 그라데이션 투명도(Fading Tail), 트레일 닷(Trail Dots) 및 흐름(Flow) 효과 적용"""
        n_points = len(r_vals)
        if n_points < 2: return
 
        # 1. 꼬리가 점차 진해지는 페이딩 라인 그리기 (과거 -> 현재)
        for j in range(n_points - 1):
            alpha = (j + 1) / n_points * (0.85 if is_sector else 0.65)
            linewidth = 3.5 if is_sector else 2.2
            linestyle = '-' if is_sector else '--'
            ax.plot(r_vals[j:j+2], m_vals[j:j+2], color=color, alpha=alpha, 
                    linewidth=linewidth, linestyle=linestyle)
            
            # 1.5 꼬리에 미세 점(Trail Dots) 추가하여 블룸버그 느낌 극대화
            dot_alpha = (j + 1) / n_points * (0.6 if is_sector else 0.45)
            dot_size = (j + 1) / n_points * (25 if is_sector else 15)
            ax.scatter(r_vals[j], m_vals[j], color=color, s=dot_size, alpha=dot_alpha, edgecolors='none', zorder=3)
 
        # 2. 현재 머리 부분에 진행 방향 화살표(Flow Arrow) 그리기
        dx = r_vals[-1] - r_vals[-2]
        dy = m_vals[-1] - m_vals[-2]
        norm = np.sqrt(dx**2 + dy**2)
        if norm > 1e-5:
            # 꼬리 길이 대비 화살표 크기 조절
            arrow_scale = 0.15 if is_sector else 0.08
            ax.annotate('', xy=(r_vals[-1], m_vals[-1]), 
                        xytext=(r_vals[-1] - dx/norm*arrow_scale, m_vals[-1] - dy/norm*arrow_scale),
                        arrowprops=dict(arrowstyle="->", color=color, lw=2.5 if is_sector else 1.8, mutation_scale=15 if is_sector else 11))
 
        # 3. 현재가 헤드 포인트 마킹
        marker_size = 180 if is_sector else 100
        marker_style = 'D' if is_sector else 'o'
        ax.scatter(r_vals[-1], m_vals[-1], color=color, s=marker_size, marker=marker_style, 
                   edgecolors='black', linewidths=1.2, zorder=5)
 
        # 4. 종목/섹터 라벨링
        font_size = 11 if is_sector else 9
        font_weight = 'bold' if is_sector else 'semibold'
        display_label = label_text if label_text is not None else ticker
        ax.annotate(display_label, (r_vals[-1], m_vals[-1]), xytext=(5, 5), textcoords='offset points',
                    fontsize=font_size, fontweight=font_weight, zorder=6,
                    bbox=dict(boxstyle="round,pad=0.2", fc="white", ec=color, lw=1, alpha=0.85))

    def generate_sector_rrg(self, sector_stock_map, output_path, tail_len=15):
        """순수 섹터 ETF 흐름만 정밀 표기하는 Sector RRG 생성 (꼬리: 15일 고정, 가로세로 독립 대칭형 스케일)"""
        sectors = list(sector_stock_map.keys())
        print(f"📊 순수 섹터 RRG 차트 생성 중 (대상: {sectors}, 꼬리: {tail_len}일)...")
        
        # 데이터 수집
        data = yf.download(sectors + [self.benchmark], period='6mo', progress=False)['Close']
        
        # 최신 거래일 추출 (조회 날짜)
        as_of_date = data.index[-1].strftime('%Y-%m-%d')
        
        fig, ax = plt.subplots(figsize=(12, 10))
        
        # 피어그룹 정규화 (섹터 그룹 내 상대강도 정규화 적용)
        raw_rs = {}
        for sector in sectors:
            raw_rs[sector] = data[sector] / data[self.benchmark]
            
        rs_df = pd.DataFrame(raw_rs)
        rs_avg = rs_df.mean(axis=1)
        
        all_r = {}
        all_m = {}
        for sector in sectors:
            rs_norm = (rs_df[sector] / rs_avg) * 100
            rs_ratio = rs_norm.rolling(20).mean()
            rs_mom = rs_ratio.pct_change(10) * 100 + 100
            
            all_r[sector] = rs_ratio.tail(tail_len).values
            all_m[sector] = rs_mom.tail(tail_len).values

        # 사분면 범위 산출
        all_x = np.concatenate(list(all_r.values()))
        all_y = np.concatenate(list(all_m.values()))
        
        # 가로축과 세로축의 최대 편차를 통합 계산하여 완벽한 상하좌우 대칭형(정사각형 비율) 스케일 구현 (100 원점 대칭 유지 및 극단적 아웃라이어 차단)
        max_dev = max(max(abs(all_x - 100)), max(abs(all_y - 100)))
        max_dev = np.clip(max_dev, 2.0, 15.0) # 섹터는 변동성이 작으므로 15.0으로 컴팩트하게 제한
        
        half_width_x = max_dev * 1.15
        half_width_y = max_dev * 1.15
        
        x_min, x_max = 100 - half_width_x, 100 + half_width_x
        y_min, y_max = 100 - half_width_y, 100 + half_width_y
        
        # 사분면 및 상세 텍스트 가이드 설정 적용
        self._setup_quadrants(ax, half_width_x, half_width_y)
        
        # 섹터별 궤적 플롯 (경계면 클리핑 적용)
        for i, sector in enumerate(sectors):
            color = self.sector_colors.get(sector, self.default_color_map(i % 10))
            clipped_r = np.clip(all_r[sector], x_min + 0.2, x_max - 0.2)
            clipped_m = np.clip(all_m[sector], y_min + 0.2, y_max - 0.2)
            self._plot_tail_with_flow(ax, clipped_r, clipped_m, sector, color, is_sector=True)
            
        ax.set_title(f'US Market Sector Rotation Graph (Relative to {self.benchmark}) - {as_of_date}\nTail: {tail_len} Days', 
                     fontsize=15, fontweight='bold', pad=15)
        ax.set_xlabel('RS-Ratio (Medium-Term Trend)', fontsize=12, fontweight='bold')
        ax.set_ylabel('RS-Momentum (Short-Term Velocity)', fontsize=12, fontweight='bold')
        ax.set_xlim(x_min, x_max)
        ax.set_ylim(y_min, y_max)
        ax.grid(True, alpha=0.15, linestyle=':')
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=150)
        plt.close()
        print(f"🎉 섹터 RRG 차트 저장 완료: {output_path}")

    def generate_stock_rrg(self, sector_stock_map, output_path, tail_len=15):
        """종목별 소속 섹터 색상 매핑을 적용하여 깔끔한 Stock RRG 생성 (꼬리: 15일 고정, 가로세로 독립 대칭형 스케일)"""
        all_tickers = []
        for stocks in sector_stock_map.values():
            all_tickers.extend(stocks)
            
        print(f"📊 개별 종목 RRG 차트 생성 중 (대상 종목: {len(all_tickers)}개, 꼬리: {tail_len}일)...")
        
        # 데이터 수집
        data = yf.download(all_tickers + [self.benchmark], period='6mo', progress=False)['Close']
        
        # 최신 거래일 추출 (조회 날짜)
        as_of_date = data.index[-1].strftime('%Y-%m-%d')
        
        fig, ax = plt.subplots(figsize=(14, 11))
        
        # 피어그룹 정규화 (전체 종목 그룹 내 상대강도 정규화 적용)
        raw_rs = {}
        for stock in all_tickers:
            raw_rs[stock] = data[stock] / data[self.benchmark]
            
        rs_df = pd.DataFrame(raw_rs)
        rs_avg = rs_df.mean(axis=1) # 피어그룹 평균 상대강도 계산 (가운데 종목이 퍼지도록 중심 고정)
        
        all_r = {}
        all_m = {}
        for stock in all_tickers:
            rs_norm = (rs_df[stock] / rs_avg) * 100
            rs_ratio = rs_norm.rolling(60).mean()
            rs_mom = rs_ratio.pct_change(10) * 100 + 100
            
            all_r[stock] = rs_ratio.tail(tail_len).values
            all_m[stock] = rs_mom.tail(tail_len).values

        # 가로축은 70~130, 세로축은 85~115 범위로 각각 다르게 고정하여 가독성 극대화 (100 원점 대칭 유지)
        half_width_x = 30.0
        half_width_y = 15.0
        
        x_min, x_max = 70.0, 130.0
        y_min, y_max = 85.0, 115.0
        
        # 사분면 및 상세 텍스트 가이드 설정 적용
        self._setup_quadrants(ax, half_width_x, half_width_y)
        
        # 종목별 궤적 플롯 (소속 섹터의 고유 색상 적용)
        legend_patches = []
        for i, (sector, stocks) in enumerate(sector_stock_map.items()):
            color = self.sector_colors.get(sector, self.default_color_map(i % 10))
            
            # 범례 설정을 위한 패치 추가
            legend_patches.append(patches.Patch(color=color, label=f"{sector} Sector"))
            
            for stock in stocks:
                if stock in all_r:
                    label_text = f"{stock} ({sector})"
                    # 뚫고 나가는 종목은 그래프 모서리 상단/하단 꼭지점이나 가장자리에 예쁘게 걸치도록 가로 70.5~129.5, 세로 85.5~114.5 범위로 클리핑 수행
                    clipped_r = np.clip(all_r[stock], 70.5, 129.5)
                    clipped_m = np.clip(all_m[stock], 85.5, 114.5)
                    self._plot_tail_with_flow(ax, clipped_r, clipped_m, stock, color, is_sector=False, label_text=label_text)
            
        ax.set_title(f'US Stock Rotation Graph (Colored by Sector, Relative to {self.benchmark}) - {as_of_date}\nTail: {tail_len} Days', 
                     fontsize=16, fontweight='bold', pad=15)
        ax.set_xlabel('RS-Ratio (Trend strength)', fontsize=12, fontweight='bold')
        ax.set_ylabel('RS-Momentum (Momentum strength)', fontsize=12, fontweight='bold')
        ax.set_xlim(x_min, x_max)
        ax.set_ylim(y_min, y_max)
        ax.grid(True, alpha=0.15, linestyle=':')
        
        # 섹터 매핑 정보를 보여주는 범례 배치
        ax.legend(handles=legend_patches, loc='upper left', framealpha=0.9, fontsize=10, 
                  title="Sector Coding Map", title_fontsize=11)
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=150)
        plt.close()
        print(f"🎉 종목 RRG 차트 저장 완료: {output_path}")

    def get_latest_rrg_stats(self, sector_stock_map):
        """각 종목의 최종 거래일 기준 RS-Ratio, RS-Momentum 및 사분면 위치 정보를 계산하여 반환합니다."""
        all_tickers = []
        for stocks in sector_stock_map.values():
            all_tickers.extend(stocks)
        
        if not all_tickers:
            return {}

        print(f"📊 실시간 RRG 정밀 매칭 분석 수행 중 (대상 종목: {len(all_tickers)}개)...")
        try:
            data = yf.download(all_tickers + [self.benchmark], period='6mo', progress=False)['Close']
            
            # 피어그룹 정규화 (전체 종목 그룹 내 상대강도 정규화 동일 적용)
            raw_rs = {}
            for stock in all_tickers:
                if stock not in data.columns or data[stock].dropna().empty:
                    continue
                raw_rs[stock] = data[stock] / data[self.benchmark]
            
            rs_df = pd.DataFrame(raw_rs)
            rs_avg = rs_df.mean(axis=1)
            
            stats = {}
            for stock in all_tickers:
                if stock not in rs_df.columns:
                    continue
                rs_norm = (rs_df[stock] / rs_avg) * 100
                rs_ratio = rs_norm.rolling(60).mean()
                rs_mom = rs_ratio.pct_change(10) * 100 + 100
                
                latest_ratio = rs_ratio.iloc[-1]
                latest_mom = rs_mom.iloc[-1]
                
                if np.isnan(latest_ratio) or np.isnan(latest_mom):
                    continue
                
                # 사분면 정의
                if latest_ratio > 100 and latest_mom > 100:
                    quadrant = "LEADING"
                elif latest_ratio <= 100 and latest_mom > 100:
                    quadrant = "IMPROVING"
                elif latest_ratio <= 100 and latest_mom <= 100:
                    quadrant = "LAGGING"
                else:
                    quadrant = "WEAKENING"
                    
                stats[stock] = {
                    'rs_ratio': latest_ratio,
                    'rs_momentum': latest_mom,
                    'quadrant': quadrant
                }
            return stats
        except Exception as e:
            print(f"⚠️ RRG 최신 스탯 계산 실패: {e}")
            return {}

if __name__ == "__main__":
    # 테스트 구동부
    mapping = {
        'XLK': ['AAPL', 'NVDA', 'MSFT'],
        'XLC': ['GOOGL', 'META'],
        'XLY': ['TSLA', 'AMZN']
    }
    viz = RRGVisualizer()
    viz.generate_sector_rrg(mapping, './rrg_charts/rrg_sectors.png')
    viz.generate_stock_rrg(mapping, './rrg_charts/rrg_stocks.png')
