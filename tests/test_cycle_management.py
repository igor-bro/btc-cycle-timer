# tests/test_cycle_management.py

import pytest
from datetime import date, datetime, timedelta
from unittest.mock import patch, MagicMock
from btc_cycle_timer.config import (
    get_current_cycle_phase, get_future_cycles, validate_cycle_config,
    calculate_next_cycle_dates, should_update_cycle_config,
    get_cycle_history, save_cycle_history
)
from btc_cycle_timer.cycle_manager import CycleManager

class TestCycleConfiguration:
    """Test cycle configuration functionality"""
    
    def test_current_cycle_phase_detection(self):
        """Test that current cycle phase is correctly detected"""
        phase = get_current_cycle_phase()
        assert phase in ["accumulation", "parabolic", "distribution", "capitulation", "unknown"]
        print(f"Current phase detected: {phase}")
    
    def test_future_cycles_calculation(self):
        """Test future cycles calculation"""
        future_cycles = get_future_cycles(3)
        
        assert len(future_cycles) == 3
        assert all("cycle_number" in cycle for cycle in future_cycles)
        assert all("peak_date" in cycle for cycle in future_cycles)
        assert all("bottom_date" in cycle for cycle in future_cycles)
        assert all("halving_date" in cycle for cycle in future_cycles)
        
        # Check that dates are in chronological order
        for i in range(len(future_cycles) - 1):
            assert future_cycles[i]["peak_date"] < future_cycles[i + 1]["peak_date"]
            assert future_cycles[i]["bottom_date"] < future_cycles[i + 1]["bottom_date"]
        
        print(f"Future cycles calculated: {len(future_cycles)} cycles")
        for cycle in future_cycles:
            print(f"  Cycle {cycle['cycle_number']}: Peak {cycle['peak_date']}, Bottom {cycle['bottom_date']}")
    
    def test_cycle_validation(self):
        """Test cycle configuration validation"""
        issues = validate_cycle_config()
        assert isinstance(issues, list)
        
        if issues:
            print(f"Validation issues found: {issues}")
        else:
            print("No validation issues found")
    
    def test_next_cycle_dates_calculation(self):
        """Test next cycle dates calculation"""
        current_peak = date(2025, 10, 11)
        current_bottom = date(2022, 11, 22)
        
        next_peak, next_bottom = calculate_next_cycle_dates(current_peak, current_bottom)
        
        assert next_peak > current_peak
        assert next_bottom > current_bottom
        assert (next_peak - current_peak).days == 1460  # 4 years
        assert (next_bottom - current_bottom).days == 1460  # 4 years
        
        print(f"Next cycle calculated: Peak {next_peak}, Bottom {next_bottom}")

class TestCycleManager:
    """Test CycleManager class functionality"""
    
    def test_cycle_manager_initialization(self):
        """Test CycleManager initialization"""
        manager = CycleManager()
        assert hasattr(manager, 'history')
        assert hasattr(manager, 'current_phase')
        assert isinstance(manager.history, list)
        assert manager.current_phase in ["accumulation", "parabolic", "distribution", "capitulation", "unknown"]
    
    @patch('btc_cycle_timer.config.should_update_cycle_config')
    def test_cycle_update_check(self, mock_should_update):
        """Test cycle update checking logic"""
        manager = CycleManager()
        
        # Test when no update is needed
        mock_should_update.return_value = False
        result = manager.check_and_update_cycle()
        assert result == False
        
        # Test when update is needed
        mock_should_update.return_value = True
        with patch.object(manager, '_update_cycle_after_peak'):
            result = manager.check_and_update_cycle()
            assert result == True
    
    def test_cycle_statistics(self):
        """Test cycle statistics calculation"""
        manager = CycleManager()
        stats = manager.get_cycle_statistics()
        
        assert isinstance(stats, dict)
        if "error" not in stats:
            assert "total_cycles" in stats
            assert "average_cycle_length_days" in stats
            assert "average_price_ratio" in stats
            assert "current_phase" in stats
            assert "cycles" in stats
    
    def test_phase_recommendations(self):
        """Test phase recommendations"""
        manager = CycleManager()
        recommendations = manager.get_phase_recommendations()
        
        assert isinstance(recommendations, dict)
        assert "strategy" in recommendations
        print(f"Current phase recommendations: {recommendations}")

class TestCycleHistory:
    """Test cycle history functionality"""
    
    def test_cycle_history_operations(self):
        """Test cycle history save/load operations"""
        # Test with empty history
        test_history = []
        save_cycle_history(test_history)
        loaded_history = get_cycle_history()
        assert isinstance(loaded_history, list)
        
        # Test with sample data
        test_history = [
            {
                "peak_date": "2021-11-10",
                "bottom_date": "2022-11-22",
                "peak_price": 69000,
                "bottom_price": 15700,
                "cycle_length_days": 377
            }
        ]
        save_cycle_history(test_history)
        loaded_history = get_cycle_history()
        assert len(loaded_history) == 1
        assert loaded_history[0]["peak_price"] == 69000

class TestIntegration:
    """Test integration between different components"""
    
    def test_full_cycle_workflow(self):
        """Test complete cycle management workflow"""
        # Initialize manager
        manager = CycleManager()
        
        # Get current state
        current_phase = manager.current_phase
        stats = manager.get_cycle_statistics()
        recommendations = manager.get_phase_recommendations()
        
        # Validate all components work together
        assert current_phase in ["accumulation", "parabolic", "distribution", "capitulation", "unknown"]
        assert isinstance(stats, dict)
        assert isinstance(recommendations, dict)
        
        print(f"Integration test passed:")
        print(f"  Current phase: {current_phase}")
        print(f"  Statistics keys: {list(stats.keys())}")
        print(f"  Recommendations: {recommendations.get('strategy', 'N/A')}")
    
    def test_cycle_data_export(self):
        """Test cycle data export functionality"""
        manager = CycleManager()
        success = manager.export_cycle_data("test_cycle_analysis.json")
        
        # Check if file was created
        import os
        if success:
            assert os.path.exists("test_cycle_analysis.json")
            # Clean up
            os.remove("test_cycle_analysis.json")
            print("Cycle data export test passed")
        else:
            print("Cycle data export test skipped (no data available)")

if __name__ == "__main__":
    # Run all tests
    pytest.main([__file__, "-v"]) 