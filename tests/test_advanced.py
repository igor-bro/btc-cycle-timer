# tests/test_advanced.py

import pytest
from datetime import datetime, timedelta
from btc_cycle_timer import (
    get_all_timers, get_btc_price, calculate_cycle_stats,
    plot_cycle_phases, localize, get_progress_bar
)
from btc_cycle_timer.chart import load_price_data, plot_pattern_projection
from btc_cycle_timer.config import (
    CYCLE_BOTTOM_DATE, FORECAST_PEAK_DATE, PREVIOUS_CYCLE_PEAK
)
import plotly.graph_objects as go

class TestEdgeCases:
    """Test edge cases and error conditions"""
    
    def test_empty_data_handling(self):
        """Test handling of empty or corrupted data"""
        # This would test how the app handles missing CSV files
        pass
    
    def test_invalid_dates(self):
        """Test handling of invalid date inputs"""
        from btc_cycle_timer.chart import get_price_on
        df = load_price_data()
        
        # Test with future date
        future_date = datetime.now() + timedelta(days=365)
        price = get_price_on(future_date, df)
        assert price is not None  # Should return last available price
    
    def test_pattern_projection_edge_cases(self):
        """Test pattern projection with edge cases"""
        fig = go.Figure()
        df = load_price_data()
        
        # Test with minimal data
        minimal_df = df.head(10)
        plot_pattern_projection(fig, minimal_df, lang="en")
        # Should handle gracefully without errors

class TestPerformance:
    """Test performance characteristics"""
    
    def test_data_loading_performance(self):
        """Test that data loading is fast enough"""
        import time
        start_time = time.time()
        df = load_price_data()
        load_time = time.time() - start_time
        
        assert load_time < 2.0, f"Data loading took {load_time:.2f}s, should be < 2s"
        assert len(df) > 0, "Data should not be empty"
    
    def test_chart_rendering_performance(self):
        """Test chart rendering performance"""
        import time
        start_time = time.time()
        fig = plot_cycle_phases(lang="en", show_projection=True)
        render_time = time.time() - start_time
        
        assert render_time < 5.0, f"Chart rendering took {render_time:.2f}s, should be < 5s"
        assert len(fig.data) > 0, "Chart should have data"

class TestLocalization:
    """Test localization features"""
    
    @pytest.mark.parametrize("lang", ["en", "ua", "fr"])
    def test_all_language_keys(self, lang):
        """Test that all required keys exist in all languages"""
        required_keys = [
            "app.title", "timer.halving", "timer.peak", "timer.bottom",
            "chart.title", "phase.accumulation", "phase.parabolic",
            "phase.distribution", "phase.capitulation", "disclaimer"
        ]
        
        for key in required_keys:
            value = localize(key, lang)
            assert value != key, f"Missing translation for {key} in {lang}"
    
    def test_fallback_to_english(self):
        """Test that missing translations fallback to English"""
        # Test with non-existent language
        value = localize("app.title", "xx")
        assert value != "app.title", "Should fallback to English"

class TestDataIntegrity:
    """Test data integrity and consistency"""
    
    def test_price_data_consistency(self):
        """Test that price data is consistent"""
        df = load_price_data()
        
        # Check for negative prices
        assert (df['close'] > 0).all(), "All prices should be positive"
        
        # Check for reasonable price range
        assert df['close'].min() > 1000, "Minimum price should be reasonable"
        assert df['close'].max() < 1000000, "Maximum price should be reasonable"
    
    def test_date_continuity(self):
        """Test that dates are continuous"""
        df = load_price_data()
        df_sorted = df.sort_values('date')
        
        # Check for gaps in dates
        date_diffs = df_sorted['date'].diff().dt.days
        assert (date_diffs <= 7).all(), "No gaps larger than 7 days should exist"

class TestConfiguration:
    """Test configuration and constants"""
    
    def test_config_consistency(self):
        """Test that configuration values are consistent"""
        from btc_cycle_timer.config import (
            LAST_HALVING, NEXT_HALVING, CYCLE_BOTTOM_DATE, FORECAST_PEAK_DATE
        )
        
        # Halvings should be 4 years apart
        halving_diff = (NEXT_HALVING - LAST_HALVING).days
        assert 1400 <= halving_diff <= 1500, "Halvings should be ~4 years apart"
        
        # Cycle dates should be reasonable
        assert CYCLE_BOTTOM_DATE < FORECAST_PEAK_DATE, "Bottom should be before peak"

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 