import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from datetime import datetime

class OptionsVisualizer:
    def __init__(self):
        # Premium Dark Theme Palette
        self.colors = {
            'bg': '#0b0f19',            # Deep space navy background
            'panel_bg': '#101625',      # Dark glass navy for axis background
            'grid': '#1f293d',          # Soft blue-grey for gridlines
            'border': '#1f293d',        # Border lines
            'text': '#e2e8f0',          # Primary text
            'text_sub': '#94a3b8',      # Secondary/muted text
            'call': '#0df5e3',          # Bright neon cyan for Calls
            'put': '#ff1773',           # Bright neon pink/coral for Puts
            'max_pain': '#ffd700',      # Gold for Max Pain
            'spot': '#ffffff',          # White/cyan for current price
            'sigma_fill': '#38bdf8',    # Sky blue for 1-Sigma shaded range
            'support_fill': '#ef4444',  # Red shaded support
            'resistance_fill': '#10b981' # Green shaded resistance
        }

    def generate_dashboard(self, options_data, output_path):
        """
        Generates a premium, 3-panel options analysis dashboard and saves it as a PNG.
        """
        ticker = options_data['ticker']
        current_price = options_data['current_price']
        expiry = options_data['selected_expiry']
        dte = options_data['days_to_expiry']
        max_pain = options_data['max_pain']
        call_wall = options_data['call_wall']
        put_wall = options_data['put_wall']
        calls = pd.DataFrame(options_data['calls'])
        puts = pd.DataFrame(options_data['puts'])
        exp_profile = options_data['expirations_profile']

        # Set up matplotlib style properties dynamically
        plt.rcParams['text.color'] = self.colors['text']
        plt.rcParams['axes.labelcolor'] = self.colors['text']
        plt.rcParams['xtick.color'] = self.colors['text_sub']
        plt.rcParams['ytick.color'] = self.colors['text_sub']
        plt.rcParams['font.family'] = 'sans-serif'

        # Initialize the figure with 3 panels: Left is tall, Right has two stacked panels
        fig = plt.figure(figsize=(18, 11), facecolor=self.colors['bg'])
        gs = fig.add_gridspec(2, 2, width_ratios=[1.2, 1.0], height_ratios=[1.0, 1.0], wspace=0.22, hspace=0.25)

        ax_oi = fig.add_subplot(gs[:, 0])        # Open Interest Profile (Vertical Strike Axis)
        ax_smile = fig.add_subplot(gs[0, 1])     # Volatility Smile / Skew
        ax_month = fig.add_subplot(gs[1, 1])     # Option Month / Expirations Profile

        # Set axis backgrounds
        for ax in [ax_oi, ax_smile, ax_month]:
            ax.set_facecolor(self.colors['panel_bg'])
            ax.grid(True, color=self.colors['grid'], linestyle=':', alpha=0.6)
            for spine in ax.spines.values():
                spine.set_color(self.colors['border'])
                spine.set_linewidth(1.2)

        # ----------------------------------------------------
        # PANEL 1: Open Interest Profile (Left Panel)
        # ----------------------------------------------------
        # Filter strikes within +/- 20% of spot price for clean visuals
        strike_min = current_price * 0.80
        strike_max = current_price * 1.20
        calls_filt = calls[(calls['strike'] >= strike_min) & (calls['strike'] <= strike_max)]
        puts_filt = puts[(puts['strike'] >= strike_min) & (puts['strike'] <= strike_max)]
        
        # Unique strikes in range
        strikes = sorted(list(set(calls_filt['strike']) | set(puts_filt['strike'])))
        
        # Calculate strike spacing for bar heights
        strike_diffs = np.diff(strikes)
        bar_height = (min(strike_diffs) * 0.4) if len(strike_diffs) > 0 else 2.0

        # Plot Bars (Puts to the left/negative, Calls to the right/positive)
        for s in strikes:
            c_val = calls_filt[calls_filt['strike'] == s]['openInterest'].values
            p_val = puts_filt[puts_filt['strike'] == s]['openInterest'].values
            c_oi = c_val[0] if len(c_val) > 0 else 0
            p_oi = p_val[0] if len(p_val) > 0 else 0

            # Draw bars
            if c_oi > 0:
                ax_oi.barh(s, c_oi, height=bar_height, color=self.colors['call'], alpha=0.85, 
                           edgecolor=self.colors['call'], linewidth=0.5, zorder=3)
            if p_oi > 0:
                ax_oi.barh(s, -p_oi, height=bar_height, color=self.colors['put'], alpha=0.85, 
                           edgecolor=self.colors['put'], linewidth=0.5, zorder=3)

        # Plot Shaded 1-Sigma Expected Move Band (Normalized 30d)
        ax_oi.axhspan(options_data['one_sigma_lower_30d'], options_data['one_sigma_upper_30d'], 
                      color=self.colors['sigma_fill'], alpha=0.08, zorder=1, label='1-Sigma Expected Move (30d)')

        # Plot Expiry-specific 1-Sigma Bounds
        ax_oi.axhline(options_data['one_sigma_lower'], color='#f472b6', linestyle=':', linewidth=1.5, alpha=0.9,
                      label=f'Lower 1-Sigma ({dte}d): ${options_data["one_sigma_lower"]:.2f}')
        ax_oi.axhline(options_data['one_sigma_upper'], color='#34d399', linestyle=':', linewidth=1.5, alpha=0.9,
                      label=f'Upper 1-Sigma ({dte}d): ${options_data["one_sigma_upper"]:.2f}')

        # Plot Key Price Level Lines
        ax_oi.axhline(current_price, color=self.colors['spot'], linestyle='--', linewidth=2.0, zorder=5,
                      label=f'Current Spot: ${current_price:.2f}')
        ax_oi.axhline(max_pain, color=self.colors['max_pain'], linestyle='-.', linewidth=1.8, zorder=5,
                      label=f'Max Pain: ${max_pain:.2f}')
        if call_wall and strike_min <= call_wall <= strike_max:
            ax_oi.axhline(call_wall, color='#10b981', linestyle='-', linewidth=1.2, alpha=0.8, zorder=4,
                          label=f'Call Wall (Resistance): ${call_wall:.2f}')
        if put_wall and strike_min <= put_wall <= strike_max:
            ax_oi.axhline(put_wall, color='#ef4444', linestyle='-', linewidth=1.2, alpha=0.8, zorder=4,
                          label=f'Put Wall (Support): ${put_wall:.2f}')

        # Labels, ticks and limits
        ax_oi.set_title(f'🎯 Options Open Interest Profile ({expiry} Expiry)\nTicker: {ticker} | Spot: ${current_price:.2f} | DTE: {dte}d', 
                        fontsize=14, fontweight='bold', pad=15)
        ax_oi.set_ylabel('Strike Price ($)', fontsize=12, fontweight='bold')
        ax_oi.set_xlabel('← Put Open Interest (Contracts)   |   Call Open Interest (Contracts) →', fontsize=11, fontweight='bold')
        
        # Set symmetric X limits and absolute positive tick labels
        x_max = max(calls_filt['openInterest'].max(), puts_filt['openInterest'].max()) * 1.15 if not calls_filt.empty and not puts_filt.empty else 1000
        ax_oi.set_xlim(-x_max, x_max)
        ticks = ax_oi.get_xticks()
        ax_oi.set_xticks(ticks)
        ax_oi.set_xticklabels([f"{abs(t):,.0f}" for t in ticks])
        ax_oi.set_ylim(strike_min, strike_max)

        # Place Legend on left panel
        ax_oi.legend(loc='upper right', framealpha=0.9, facecolor=self.colors['panel_bg'], edgecolor=self.colors['border'], fontsize=9.5)

        # Add visual watermark text box for the plan zones
        buy_zone_top = min(put_wall if put_wall else current_price, options_data['one_sigma_lower_30d'])
        sell_zone_bottom = max(call_wall if call_wall else current_price, options_data['one_sigma_upper_30d'])
        
        # Cap the y-positions of the watermark text boxes within the visible strike limits 
        # to prevent stretching the saved figure size with bbox_inches='tight'
        buy_text_y = buy_zone_top - (strike_max - strike_min) * 0.03
        if buy_text_y < strike_min + (strike_max - strike_min) * 0.02 or buy_text_y > strike_max:
            buy_text_y = strike_min + (strike_max - strike_min) * 0.05
            
        sell_text_y = sell_zone_bottom + (strike_max - strike_min) * 0.03
        if sell_text_y > strike_max - (strike_max - strike_min) * 0.02 or sell_text_y < strike_min:
            sell_text_y = strike_max - (strike_max - strike_min) * 0.15
            
        props_buy = dict(boxstyle='round,pad=0.4', facecolor='#dc2626', alpha=0.15, edgecolor='#dc2626')
        ax_oi.text(-x_max * 0.9, buy_text_y, "📈 Optimal Buy Accumulation Zone\n(Statistical Support)", 
                   fontsize=9, fontweight='bold', color='#fca5a5', bbox=props_buy, va='top')

        props_sell = dict(boxstyle='round,pad=0.4', facecolor='#059669', alpha=0.15, edgecolor='#059669')
        ax_oi.text(x_max * 0.1, sell_text_y, "💰 Short-Term Profit Target Zone\n(Statistical Resistance)", 
                   fontsize=9, fontweight='bold', color='#a7f3d0', bbox=props_sell, va='bottom')

        # ----------------------------------------------------
        # PANEL 2: Implied Volatility Smile & Skew (Top Right)
        # ----------------------------------------------------
        # Clean data for IV plot
        calls_iv = calls_filt[calls_filt['impliedVolatility'] > 0]
        puts_iv = puts_filt[puts_filt['impliedVolatility'] > 0]

        ax_smile.plot(calls_iv['strike'], calls_iv['impliedVolatility'] * 100, color=self.colors['call'], 
                      marker='o', markersize=4, linestyle='-', linewidth=1.5, alpha=0.85, label='Call IV')
        ax_smile.plot(puts_iv['strike'], puts_iv['impliedVolatility'] * 100, color=self.colors['put'], 
                      marker='o', markersize=4, linestyle='-', linewidth=1.5, alpha=0.85, label='Put IV')
        
        # Draw vertical Spot line
        ax_smile.axvline(current_price, color=self.colors['spot'], linestyle='--', linewidth=1.5, alpha=0.8,
                         label=f'Spot (${current_price:.2f})')
        ax_smile.axvline(max_pain, color=self.colors['max_pain'], linestyle='-.', linewidth=1.5, alpha=0.8,
                         label=f'Max Pain (${max_pain:.2f})')

        ax_smile.set_title(f'⚡ Implied Volatility Smile & Market Skew', fontsize=12, fontweight='bold', pad=10)
        ax_smile.set_xlabel('Strike Price ($)', fontsize=10)
        ax_smile.set_ylabel('Implied Volatility (%)', fontsize=10)
        ax_smile.set_xlim(strike_min, strike_max)
        
        # Compute dynamic y limits for IV
        all_ivs = pd.concat([calls_iv['impliedVolatility'], puts_iv['impliedVolatility']]) * 100
        if not all_ivs.empty:
            ax_smile.set_ylim(max(0, all_ivs.min() * 0.8), all_ivs.max() * 1.1)

        ax_smile.legend(loc='upper right', framealpha=0.9, facecolor=self.colors['panel_bg'], edgecolor=self.colors['border'], fontsize=8.5)

        # ----------------------------------------------------
        # PANEL 3: Option Month Expirations Profile (Bottom Right)
        # ----------------------------------------------------
        if exp_profile:
            exp_df = pd.DataFrame(exp_profile)
            # Reformat expirations for presentation
            exp_df['short_date'] = exp_df['expiry'].apply(lambda x: datetime.strptime(x, "%Y-%m-%d").strftime("%b %d"))
            
            x_indices = np.arange(len(exp_df))
            bar_w = 0.35

            # Side by side bars for Calls vs Puts OI on upcoming expirations
            ax_month.bar(x_indices - bar_w/2, exp_df['calls_oi'], width=bar_w, color=self.colors['call'], alpha=0.8, label='Call OI')
            ax_month.bar(x_indices + bar_w/2, exp_df['puts_oi'], width=bar_w, color=self.colors['put'], alpha=0.8, label='Put OI')

            # Highlight selected expiration
            if expiry in exp_df['expiry'].values:
                sel_idx = exp_df[exp_df['expiry'] == expiry].index[0]
                # Draw a golden neon border around the selected expiration bar group
                max_y = max(exp_df['calls_oi'].max(), exp_df['puts_oi'].max()) * 1.15
                rect = patches.Rectangle((sel_idx - 0.45, 0), 0.9, max_y, linewidth=1.5, 
                                         edgecolor=self.colors['max_pain'], facecolor='none', linestyle='--', alpha=0.9, zorder=5)
                ax_month.add_patch(rect)
                ax_month.text(sel_idx, max_y * 0.95, "ACTIVE MONTH", ha='center', color=self.colors['max_pain'], 
                              fontweight='bold', fontsize=8, bbox=dict(boxstyle='round,pad=0.2', facecolor=self.colors['bg'], alpha=0.8))

            ax_month.set_title(f'📅 Option Month Liquidity Profile (Upcoming Expirations)', fontsize=12, fontweight='bold', pad=10)
            ax_month.set_xticks(x_indices)
            ax_month.set_xticklabels(exp_df['short_date'], rotation=0, fontsize=9.5)
            ax_month.set_ylabel('Open Interest (Contracts)', fontsize=10)
            ax_month.set_xlabel('Expiration Date', fontsize=10)
            ax_month.legend(loc='upper right', framealpha=0.9, facecolor=self.colors['panel_bg'], edgecolor=self.colors['border'], fontsize=8.5)
        else:
            ax_month.text(0.5, 0.5, "Expiration profile data unavailable", ha='center', va='center', color=self.colors['text_sub'])

        # Main Title Header (종목이름 + 오늘 날짜 추가)
        today_str = datetime.now().strftime('%Y-%m-%d')
        fig.suptitle(f'ANTIGRAVITY QUANT ENGINE - OPTIONS DASHBOARD: {ticker} ({today_str})', 
                     color='#ffffff', fontsize=16, fontweight='bold', y=0.97)

        # Save to output path
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        plt.savefig(output_path, dpi=160, facecolor=self.colors['bg'], bbox_inches='tight')
        plt.close()
        print(f"🎉 Breathtaking Options dashboard saved successfully: {output_path}")

# Quick testing block
if __name__ == "__main__":
    from options_engine import OptionsInsightEngine
    engine = OptionsInsightEngine()
    data = engine.analyze_options_data("TSLA")
    if data:
        viz = OptionsVisualizer()
        viz.generate_dashboard(data, "./options_charts/test_tsla.png")
