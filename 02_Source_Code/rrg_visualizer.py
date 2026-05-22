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

    def _draw_concentric_circles(self, ax, x_min, x_max, y_min, y_max):
        """벤치마크 중심점(100, 100) 기준으로 블룸버그 스타일의 동심 가이드라인 그리기"""
        max_dist = max(abs(x_min - 100), abs(x_max - 100), abs(y_min - 100), abs(y_max - 100))
        if max_dist <= 0:
            max_dist = 1.0
            
        # 데이터 분산 수준에 맞춰 예쁜 반지름 스텝 설정
        if max_dist < 1.0:
            radii = [0.2, 0.4, 0.6, 0.8]
        elif max_dist < 3.0:
            radii = [0.5, 1.0, 1.5, 2.0, 2.5]
        elif max_dist < 6.0:
            radii = [1.0, 2.0, 3.0, 4.0, 5.0]
        else:
            step = np.ceil(max_dist / 5.0)
            radii = [step * i for i in range(1, 6)]
            
        for r in radii:
            # 동심 원형 패치 추가
            circle = patches.Circle((100, 100), r, fill=False, color='#555555', linestyle=':', linewidth=0.8, alpha=0.25)
            ax.add_patch(circle)
            # 45도 방향선 위에 반지름 라벨 표시 (축 눈금과 겹침 방지)
            ax.text(100 + r * 0.707, 100 + r * 0.707, f"{r:.1f}", 
                    fontsize=8, color='#777777', alpha=0.45, ha='center', va='center')

    def _setup_quadrants(self, ax, x_min, x_max, y_min, y_max):
        """사분면에 Bloomberg 스타일의 부드러운 파스텔톤 배경색 채우기 및 라벨 배치"""
        # Quadrant background fills (highly transparent)
        # Leading (Top Right): Green
        rect_leading = patches.Rectangle((100, 100), x_max - 100, y_max - 100, linewidth=0, facecolor='#E2F0D9', alpha=0.25)
        # Improving (Top Left): Blue
        rect_improving = patches.Rectangle((x_min, 100), 100 - x_min, y_max - 100, linewidth=0, facecolor='#D9E1F2', alpha=0.25)
        # Lagging (Bottom Left): Pink/Red
        rect_lagging = patches.Rectangle((x_min, y_min), 100 - x_min, 100 - y_min, linewidth=0, facecolor='#FCE4D6', alpha=0.25)
        # Weakening (Bottom Right): Yellow/Orange
        rect_weakening = patches.Rectangle((100, y_min), x_max - 100, 100 - y_min, linewidth=0, facecolor='#FFF2CC', alpha=0.25)

        ax.add_patch(rect_leading)
        ax.add_patch(rect_improving)
        ax.add_patch(rect_lagging)
        ax.add_patch(rect_weakening)

        # 동심 가이드라인 그리기
        self._draw_concentric_circles(ax, x_min, x_max, y_min, y_max)

        # Draw axis lines
        ax.axhline(100, color='#555555', linestyle='-', linewidth=1.5, alpha=0.6)
        ax.axvline(100, color='#555555', linestyle='-', linewidth=1.5, alpha=0.6)

        # Quadrant text labels
        ax.text(x_max - (x_max - 100)*0.4, y_max - (y_max - 100)*0.15, 'LEADING', 
                fontsize=16, color='#385723', fontweight='bold', alpha=0.85, ha='center')
        ax.text(x_min + (100 - x_min)*0.4, y_max - (y_max - 100)*0.15, 'IMPROVING', 
                fontsize=16, color='#1F4E79', fontweight='bold', alpha=0.85, ha='center')
        ax.text(x_min + (100 - x_min)*0.4, y_min + (100 - y_min)*0.15, 'LAGGING', 
                fontsize=16, color='#C65911', fontweight='bold', alpha=0.85, ha='center')
        ax.text(x_max - (x_max - 100)*0.4, y_min + (100 - y_min)*0.15, 'WEAKENING', 
                fontsize=16, color='#7F6000', fontweight='bold', alpha=0.85, ha='center')

    def _plot_tail_with_flow(self, ax, r_vals, m_vals, ticker, color, is_sector=False, label_text=None):
        """꼬리 부분에 그라데이션 투명도(Fading Tail), 트레일 닷(Trail Dots) 및 흐름(Flow) 효과 적용"""
        n_points = len(r_vals)
        if n_points < 2: return
 
        # 1. 꼬리가 점차 진해지는 페이딩 라인 그리기 (과거 -> 현재)
        for j in range(n_points - 1):
            alpha = (j + 1) / n_points * (0.85 if is_sector else 0.6)
            linewidth = 3.5 if is_sector else 1.8
            linestyle = '-' if is_sector else '--'
            ax.plot(r_vals[j:j+2], m_vals[j:j+2], color=color, alpha=alpha, 
                    linewidth=linewidth, linestyle=linestyle)
            
            # 1.5 꼬리에 미세 점(Trail Dots) 추가하여 블룸버그 느낌 극대화
            dot_alpha = (j + 1) / n_points * (0.6 if is_sector else 0.4)
            dot_size = (j + 1) / n_points * (25 if is_sector else 12)
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
                        arrowprops=dict(arrowstyle="->", color=color, lw=2.5 if is_sector else 1.5, mutation_scale=15 if is_sector else 10))
 
        # 3. 현재가 헤드 포인트 마킹
        marker_size = 180 if is_sector else 90
        marker_style = 'D' if is_sector else 'o'
        ax.scatter(r_vals[-1], m_vals[-1], color=color, s=marker_size, marker=marker_style, 
                   edgecolors='black', linewidths=1.2, zorder=5)
 
        # 4. 종목/섹터 라벨링
        font_size = 11 if is_sector else 8.5
        font_weight = 'bold' if is_sector else 'normal'
        display_label = label_text if label_text is not None else ticker
        ax.annotate(display_label, (r_vals[-1], m_vals[-1]), xytext=(5, 5), textcoords='offset points',
                    fontsize=font_size, fontweight=font_weight, zorder=6,
                    bbox=dict(boxstyle="round,pad=0.2", fc="white", ec=color, lw=1, alpha=0.8))

    def generate_sector_rrg(self, sector_stock_map, output_path, tail_len=15):
        """순수 섹터 ETF 흐름만 정밀 표기하는 Sector RRG 생성 (꼬리: 15일 고정)"""
        sectors = list(sector_stock_map.keys())
        print(f"📊 순수 섹터 RRG 차트 생성 중 (대상: {sectors}, 꼬리: {tail_len}일)...")
        
        # 데이터 수집
        data = yf.download(sectors + [self.benchmark], period='6mo', progress=False)['Close']
        
        fig, ax = plt.subplots(figsize=(12, 9))
        
        # 전체 데이터에 대한 RS-Ratio, RS-Momentum 계산
        all_r = {}
        all_m = {}
        for sector in sectors:
            ratio = (data[sector] / data[self.benchmark]) * 100
            rs_ratio = ratio.rolling(20).mean()
            rs_mom = rs_ratio.pct_change(10) * 100 + 100
            
            all_r[sector] = rs_ratio.tail(tail_len).values
            all_m[sector] = rs_mom.tail(tail_len).values

        # 사분면 범위 산출
        all_x = np.concatenate(list(all_r.values()))
        all_y = np.concatenate(list(all_m.values()))
        
        x_min, x_max = min(all_x) - 0.5, max(all_x) + 0.5
        y_min, y_max = min(all_y) - 0.5, max(all_y) + 0.5
        
        # 사분면 설정 적용
        self._setup_quadrants(ax, x_min, x_max, y_min, y_max)
        
        # 섹터별 궤적 플롯
        for i, sector in enumerate(sectors):
            color = self.sector_colors.get(sector, self.default_color_map(i % 10))
            self._plot_tail_with_flow(ax, all_r[sector], all_m[sector], sector, color, is_sector=True)
            
        ax.set_title(f'US Market Sector Rotation Graph (Relative to {self.benchmark}) - Tail: {tail_len} Days', 
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
        """종목별 소속 섹터 색상 매핑을 적용하되, 섹터 ETF를 제외하여 깔끔한 Stock RRG 생성 (꼬리: 15일 고정)"""
        all_tickers = []
        for stocks in sector_stock_map.values():
            all_tickers.extend(stocks)
            
        print(f"📊 개별 종목 RRG 차트 생성 중 (대상 종목: {len(all_tickers)}개, 꼬리: {tail_len}일)...")
        
        # 데이터 수집
        data = yf.download(all_tickers + [self.benchmark], period='6mo', progress=False)['Close']
        
        fig, ax = plt.subplots(figsize=(14, 10))
        
        all_r = {}
        all_m = {}
        for stock in all_tickers:
            ratio = (data[stock] / data[self.benchmark]) * 100
            rs_ratio = ratio.rolling(20).mean()
            rs_mom = rs_ratio.pct_change(10) * 100 + 100
            
            all_r[stock] = rs_ratio.tail(tail_len).values
            all_m[stock] = rs_mom.tail(tail_len).values

        # 사분면 범위 산출
        all_x = np.concatenate(list(all_r.values()))
        all_y = np.concatenate(list(all_m.values()))
        
        x_min, x_max = min(all_x) - 0.5, max(all_x) + 0.5
        y_min, y_max = min(all_y) - 0.5, max(all_y) + 0.5
        
        # 사분면 설정 적용
        self._setup_quadrants(ax, x_min, x_max, y_min, y_max)
        
        # 종목별 궤적 플롯 (소속 섹터의 고유 색상 적용)
        legend_patches = []
        for i, (sector, stocks) in enumerate(sector_stock_map.items()):
            color = self.sector_colors.get(sector, self.default_color_map(i % 10))
            
            # 범례 설정을 위한 패치 추가
            legend_patches.append(patches.Patch(color=color, label=f"{sector} Sector"))
            
            for stock in stocks:
                if stock in all_r:
                    label_text = f"{stock} ({sector})"
                    self._plot_tail_with_flow(ax, all_r[stock], all_m[stock], stock, color, is_sector=False, label_text=label_text)
            
        ax.set_title(f'US Stock Rotation Graph (Colored by Sector, Relative to {self.benchmark}) - Tail: {tail_len} Days', 
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

if __name__ == "__main__":
    # 테스트 구동부
    mapping = {
        'XLK': ['AAPL', 'NVDA', 'MSFT'],
        'XLC': ['GOOGL', 'META'],
        'XLY': ['TSLA', 'AMZN']
    }
    viz = RRGVisualizer()
    viz.generate_sector_rrg(mapping, './rrg_sectors.png')
    viz.generate_stock_rrg(mapping, './rrg_stocks.png')
