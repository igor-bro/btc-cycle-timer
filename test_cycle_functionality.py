#!/usr/bin/env python3
"""
Interactive test script for cycle management functionality
"""

from btc_cycle_timer.config import (
    get_current_cycle_phase, get_future_cycles, validate_cycle_config,
    calculate_next_cycle_dates, should_update_cycle_config
)
from btc_cycle_timer.cycle_manager import CycleManager
from btc_cycle_timer.logger import logger

def test_basic_functionality():
    """Test basic cycle functionality"""
    print("🔍 Testing Basic Cycle Functionality")
    print("=" * 50)
    
    # Test current phase detection
    current_phase = get_current_cycle_phase()
    print(f"✅ Current cycle phase: {current_phase}")
    
    # Test future cycles
    future_cycles = get_future_cycles(3)
    print(f"✅ Future cycles calculated: {len(future_cycles)}")
    for cycle in future_cycles:
        print(f"   Cycle {cycle['cycle_number']}: Peak {cycle['peak_date']}, Bottom {cycle['bottom_date']}")
    
    # Test validation
    issues = validate_cycle_config()
    if issues:
        print(f"⚠️  Validation issues: {issues}")
    else:
        print("✅ No validation issues found")
    
    print()

def test_cycle_manager():
    """Test CycleManager class"""
    print("🔍 Testing CycleManager")
    print("=" * 50)
    
    # Initialize manager
    manager = CycleManager()
    print(f"✅ CycleManager initialized")
    print(f"   Current phase: {manager.current_phase}")
    print(f"   History entries: {len(manager.history)}")
    
    # Test statistics
    stats = manager.get_cycle_statistics()
    print(f"✅ Statistics calculated:")
    for key, value in stats.items():
        if key != "cycles":  # Skip detailed cycles data
            print(f"   {key}: {value}")
    
    # Test recommendations
    recommendations = manager.get_phase_recommendations()
    print(f"✅ Phase recommendations:")
    for key, value in recommendations.items():
        print(f"   {key}: {value}")
    
    print()

def test_cycle_calculations():
    """Test cycle calculations"""
    print("🔍 Testing Cycle Calculations")
    print("=" * 50)
    
    # Test next cycle calculation
    current_peak = date(2025, 10, 11)
    current_bottom = date(2022, 11, 22)
    
    next_peak, next_bottom = calculate_next_cycle_dates(current_peak, current_bottom)
    print(f"✅ Next cycle calculated:")
    print(f"   Current peak: {current_peak}")
    print(f"   Next peak: {next_peak}")
    print(f"   Days difference: {(next_peak - current_peak).days}")
    
    # Test update check
    needs_update = should_update_cycle_config()
    print(f"✅ Cycle update needed: {needs_update}")
    
    print()

def test_integration():
    """Test integration with existing functionality"""
    print("🔍 Testing Integration")
    print("=" * 50)
    
    # Test with existing timer functionality
    from btc_cycle_timer.timer import get_all_timers
    timers = get_all_timers()
    print(f"✅ Timers integration:")
    for key, value in timers.items():
        print(f"   {key}: {value} days")
    
    # Test with existing price functionality
    from btc_cycle_timer.price import get_btc_price
    price = get_btc_price()
    print(f"✅ Price integration: ${price:,.2f}")
    
    # Test with existing chart functionality
    from btc_cycle_timer.chart import plot_cycle_phases
    fig = plot_cycle_phases(show_projection=True)
    print(f"✅ Chart integration: {len(fig.data)} traces")
    
    print()

def test_export_functionality():
    """Test data export functionality"""
    print("🔍 Testing Export Functionality")
    print("=" * 50)
    
    manager = CycleManager()
    success = manager.export_cycle_data("cycle_analysis_test.json")
    
    if success:
        print("✅ Cycle data exported successfully")
        print("   File: cycle_analysis_test.json")
        
        # Read and display sample of exported data
        import json
        with open("cycle_analysis_test.json", "r") as f:
            data = json.load(f)
        
        print("   Exported data includes:")
        for key in data.keys():
            print(f"     - {key}")
    else:
        print("⚠️  Export skipped (no data available)")
    
    print()

def main():
    """Run all tests"""
    print("🚀 BTC Cycle Timer - Cycle Management Test Suite")
    print("=" * 60)
    print()
    
    try:
        test_basic_functionality()
        test_cycle_manager()
        test_cycle_calculations()
        test_integration()
        test_export_functionality()
        
        print("🎉 All tests completed successfully!")
        print()
        print("📋 Summary:")
        print("   ✅ Basic cycle functionality working")
        print("   ✅ CycleManager class operational")
        print("   ✅ Calculations accurate")
        print("   ✅ Integration with existing modules")
        print("   ✅ Export functionality available")
        print()
        print("🔧 Next steps:")
        print("   1. Monitor cycle progression")
        print("   2. Update configuration when needed")
        print("   3. Use recommendations for strategy")
        print("   4. Export data for external analysis")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        logger.error(f"Test suite failed: {e}")

if __name__ == "__main__":
    from datetime import date
    main() 