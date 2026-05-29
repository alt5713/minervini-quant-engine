import os
import sys
from datetime import datetime
from main_agent import AntigravityMasterV95
from rrg_visualizer import RRGVisualizer

def main():
    # Define our list of Magnificient Big 7 stocks across core sectors
    sector_stock_map = {
        'XLK': ['AAPL', 'MSFT', 'NVDA'],
        'XLC': ['GOOGL', 'META'],
        'XLY': ['AMZN', 'TSLA']
    }

    print("=" * 80)
    print("🚀 Running Antigravity Minervini V9.5 Custom US Market Scan")
    print(f"Target Stocks Count: {sum(len(v) for v in sector_stock_map.values())} tickers across {len(sector_stock_map)} sectors")
    print("=" * 80)

    # Initialize the master agent
    master = AntigravityMasterV95()

    # Run the main pipeline
    # This will fetch data, analyze trend templates, VCP signals, smart money, options wall, and conflict resolution
    master.run_strategy_pipeline(sector_stock_map)

    # Additionally, generate a custom RRG report to visually present sector and stock trajectories
    print("\n" + "=" * 80)
    print("📊 Generating Relative Rotation Graph (RRG) visualization...")
    print("=" * 80)
    
    date_str = datetime.now().strftime('%Y-%m-%d')
    rrg_sectors_path = f'./rrg_charts/rrg_sectors_{date_str}.png'
    rrg_stocks_path = f'./rrg_charts/rrg_stocks_{date_str}.png'
    try:
        viz = RRGVisualizer()
        viz.generate_sector_rrg(sector_stock_map, rrg_sectors_path, tail_len=15)
        viz.generate_stock_rrg(sector_stock_map, rrg_stocks_path, tail_len=15)
        print(f"🎉 Sector RRG chart successfully saved to: {rrg_sectors_path}")
        print(f"🎉 Stock RRG chart successfully saved to: {rrg_stocks_path}")
    except Exception as e:
        print(f"⚠️ RRG Generation failed: {e}")

if __name__ == "__main__":
    main()
