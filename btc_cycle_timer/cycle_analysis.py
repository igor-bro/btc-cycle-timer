# cycle_analysis.py

import pandas as pd
from datetime import datetime, date
from typing import Dict, List
from btc_cycle_timer.chart import load_price_data
from btc_cycle_timer.logger import logger

class CycleAnalyzer:
    """Analyze Bitcoin cycles based on halving events"""
    
    def __init__(self):
        self.halving_dates = [
            datetime(2012, 11, 28),  # 1st halving
            datetime(2016, 7, 9),    # 2nd halving  
            datetime(2020, 5, 11),   # 3rd halving
            datetime(2024, 4, 20),   # 4th halving
            datetime(2028, 4, 20),   # 5th halving (forecasted)
        ]
        
        # Historical cycle peaks (approximate)
        self.cycle_peaks = [
            datetime(2013, 11, 29),  # ~$1,163
            datetime(2017, 12, 17),  # ~$19,783
            datetime(2021, 11, 10),  # ~$69,000
            datetime(2025, 10, 11),  # ~$200,000 (forecasted)
        ]
        
        # Historical cycle bottoms (approximate)
        self.cycle_bottoms = [
            datetime(2015, 1, 14),   # ~$152
            datetime(2018, 12, 15),  # ~$3,122
            datetime(2022, 11, 22),  # ~$15,700
            datetime(2026, 10, 30),  # ~$75,000 (forecasted)
        ]
        
        logger.info("Cycle Analyzer initialized")
    
    def get_cycle_structure(self) -> Dict:
        """Get the correct Bitcoin cycle structure"""
        cycles = []
        
        for i in range(len(self.halving_dates) - 1):
            halving_start = self.halving_dates[i]
            halving_end = self.halving_dates[i + 1]
            
            # Find peak and bottom within this cycle
            peak = None
            bottom = None
            
            if i < len(self.cycle_peaks):
                peak = self.cycle_peaks[i]
            if i < len(self.cycle_bottoms):
                bottom = self.cycle_bottoms[i]
            
            cycle = {
                'cycle_number': i + 1,
                'halving_start': halving_start,
                'halving_end': halving_end,
                'peak_date': peak,
                'bottom_date': bottom,
                'cycle_length_days': (halving_end - halving_start).days,
                'description': f"Cycle {i + 1} ({halving_start.year}-{halving_end.year})"
            }
            
            cycles.append(cycle)
        
        return {
            'total_cycles': len(cycles),
            'cycles': cycles,
            'current_cycle': len(cycles) - 1,  # 0-based index
            'next_halving': self.halving_dates[-1]
        }
    
    def analyze_historical_cycles(self) -> Dict:
        """Analyze historical cycle patterns"""
        logger.info("Analyzing historical cycles")
        
        # Load price data
        df = load_price_data()
        df['date'] = pd.to_datetime(df['date'])
        
        analysis = {}
        
        for i, cycle in enumerate(self.get_cycle_structure()['cycles'][:-1]):  # Exclude current cycle
            if cycle['peak_date'] and cycle['bottom_date']:
                # Get price data for this cycle
                cycle_start = cycle['halving_start']
                cycle_end = cycle['halving_end']
                
                cycle_data = df[
                    (df['date'] >= cycle_start) & 
                    (df['date'] <= cycle_end)
                ].copy()
                
                if len(cycle_data) > 0:
                    # Calculate cycle metrics
                    peak_price = cycle_data['close'].max()
                    bottom_price = cycle_data['close'].min()
                    price_ratio = peak_price / bottom_price if bottom_price > 0 else 0
                    
                    # Find actual peak and bottom dates
                    peak_idx = cycle_data['close'].idxmax()
                    bottom_idx = cycle_data['close'].idxmin()
                    
                    actual_peak_date = cycle_data.loc[peak_idx, 'date']
                    actual_bottom_date = cycle_data.loc[bottom_idx, 'date']
                    
                    # Days from halving to peak
                    days_to_peak = (actual_peak_date - cycle_start).days if hasattr(actual_peak_date, 'days') else (actual_peak_date - cycle_start).dt.days.iloc[0]
                    
                    analysis[f'cycle_{i+1}'] = {
                        'cycle_period': f"{cycle_start.year}-{cycle_end.year}",
                        'peak_date': actual_peak_date.strftime('%Y-%m-%d'),
                        'bottom_date': actual_bottom_date.strftime('%Y-%m-%d'),
                        'peak_price': peak_price,
                        'bottom_price': bottom_price,
                        'price_ratio': price_ratio,
                        'days_to_peak': days_to_peak,
                        'cycle_length_days': (cycle_end - cycle_start).days,
                        'total_records': len(cycle_data)
                    }
        
        return analysis
    
    def print_cycle_structure(self):
        """Print detailed cycle structure"""
        structure = self.get_cycle_structure()
        
        print("🔄 Bitcoin Cycle Structure (Based on Halvings)")
        print("=" * 60)
        
        for cycle in structure['cycles']:
            print(f"\n📊 {cycle['description']}")
            print(f"   🗓️  Halving Period: {cycle['halving_start'].strftime('%Y-%m-%d')} → {cycle['halving_end'].strftime('%Y-%m-%d')}")
            print(f"   📈 Cycle Length: {cycle['cycle_length_days']} days (~{cycle['cycle_length_days']/365:.1f} years)")
            
            if cycle['peak_date']:
                print(f"   🏔️  Peak Date: {cycle['peak_date'].strftime('%Y-%m-%d')}")
            if cycle['bottom_date']:
                print(f"   📉 Bottom Date: {cycle['bottom_date'].strftime('%Y-%m-%d')}")
        
        print(f"\n🎯 Current Cycle: {structure['current_cycle'] + 1}")
        print(f"🔮 Next Halving: {structure['next_halving'].strftime('%Y-%m-%d')}")
    
    def print_historical_analysis(self):
        """Print historical cycle analysis"""
        analysis = self.analyze_historical_cycles()
        
        print("\n📊 Historical Cycle Analysis")
        print("=" * 60)
        
        for cycle_key, cycle_data in analysis.items():
            print(f"\n🔄 {cycle_data['cycle_period']}")
            print(f"   📈 Peak: ${cycle_data['peak_price']:,.0f} ({cycle_data['peak_date']})")
            print(f"   📉 Bottom: ${cycle_data['bottom_price']:,.0f} ({cycle_data['bottom_date']})")
            print(f"   📊 Price Ratio: {cycle_data['price_ratio']:.1f}x")
            print(f"   ⏰ Days to Peak: {cycle_data['days_to_peak']} days")
            print(f"   📅 Cycle Length: {cycle_data['cycle_length_days']} days")
        
        # Calculate averages
        if analysis:
            avg_price_ratio = sum(c['price_ratio'] for c in analysis.values()) / len(analysis)
            avg_days_to_peak = sum(c['days_to_peak'] for c in analysis.values()) / len(analysis)
            avg_cycle_length = sum(c['cycle_length_days'] for c in analysis.values()) / len(analysis)
            
            print(f"\n📊 Averages:")
            print(f"   📈 Average Price Ratio: {avg_price_ratio:.1f}x")
            print(f"   ⏰ Average Days to Peak: {avg_days_to_peak:.0f} days")
            print(f"   📅 Average Cycle Length: {avg_cycle_length:.0f} days")
    
    def get_current_cycle_info(self) -> Dict:
        """Get information about the current cycle"""
        structure = self.get_cycle_structure()
        current_cycle = structure['cycles'][-1]  # Current cycle
        
        return {
            'cycle_number': current_cycle['cycle_number'],
            'halving_start': current_cycle['halving_start'],
            'halving_end': current_cycle['halving_end'],
            'peak_date': current_cycle['peak_date'],
            'bottom_date': current_cycle['bottom_date'],
            'days_elapsed': (datetime.now() - current_cycle['halving_start']).days,
            'days_remaining': (current_cycle['halving_end'] - datetime.now()).days,
            'progress_percent': ((datetime.now() - current_cycle['halving_start']).days / 
                               (current_cycle['halving_end'] - current_cycle['halving_start']).days) * 100
        }

# Create global instance
cycle_analyzer = CycleAnalyzer()

# Export functions
__all__ = ['CycleAnalyzer', 'cycle_analyzer'] 