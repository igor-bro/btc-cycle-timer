#!/usr/bin/env python3
"""
Main script to run all monitoring systems
"""

import argparse
import sys
from pathlib import Path
from btc_cycle_timer.logger import logger
from btc_cycle_timer.price import fetch_all_historical_data
from btc_cycle_timer.monitoring import monitoring_system
from btc_cycle_timer.ml_predictor import ml_predictor

def setup_historical_data():
    """Download all historical data"""
    print("📊 Setting up historical data...")
    try:
        total_files, total_records = fetch_all_historical_data()
        print(f"✅ Historical data setup completed: {total_files} files, {total_records} records")
        return True
    except Exception as e:
        print(f"❌ Error setting up historical data: {e}")
        return False

def setup_ml_model():
    """Setup and train ML model"""
    print("🤖 Setting up ML model...")
    try:
        from btc_cycle_timer.chart import load_price_data
        
        # Load data
        df = load_price_data()
        print(f"📈 Loaded {len(df)} data points for ML training")
        
        # Train model
        metrics = ml_predictor.train_model(df)
        print(f"✅ ML model trained successfully")
        print(f"   Test R²: {metrics['test_r2']:.3f}")
        print(f"   Test MAE: ${metrics['test_mae']:,.2f}")
        
        return True
    except Exception as e:
        print(f"❌ Error setting up ML model: {e}")
        return False

def test_monitoring():
    """Test monitoring system"""
    print("🧪 Testing monitoring system...")
    try:
        # Test daily report
        print("📅 Testing daily report...")
        monitoring_system.run_once("daily")
        
        # Test weekly report
        print("📊 Testing weekly report...")
        monitoring_system.run_once("weekly")
        
        # Test ML report
        print("🤖 Testing ML report...")
        try:
            ml_report = ml_predictor.generate_ml_report()
            print("ML Report preview:")
            print(ml_report[:500] + "..." if len(ml_report) > 500 else ml_report)
        except Exception as e:
            print(f"ML report test failed: {e}")
        
        print("✅ Monitoring system test completed")
        return True
    except Exception as e:
        print(f"❌ Error testing monitoring: {e}")
        return False

def start_monitoring():
    """Start the monitoring system"""
    print("🚀 Starting monitoring system...")
    print("📅 Daily reports: 8:00 AM")
    print("📊 Weekly reports: Saturday 9:00 AM")
    print("🔄 Phase change notifications: Every hour")
    print("🤖 ML predictions: Available on demand")
    print("\nPress Ctrl+C to stop...")
    
    try:
        monitoring_system.start_monitoring()
    except KeyboardInterrupt:
        print("\n🛑 Monitoring stopped by user")
    except Exception as e:
        print(f"❌ Error in monitoring: {e}")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="BTC Cycle Timer - Monitoring System")
    parser.add_argument("--setup", action="store_true", help="Setup historical data and ML model")
    parser.add_argument("--test", action="store_true", help="Test monitoring system")
    parser.add_argument("--start", action="store_true", help="Start monitoring system")
    parser.add_argument("--all", action="store_true", help="Setup, test, and start monitoring")
    
    args = parser.parse_args()
    
    if not any([args.setup, args.test, args.start, args.all]):
        parser.print_help()
        return
    
    print("🚀 BTC Cycle Timer - Monitoring System")
    print("=" * 50)
    
    try:
        if args.setup or args.all:
            print("\n🔧 Setup Phase")
            print("-" * 20)
            
            # Setup historical data
            if not setup_historical_data():
                print("❌ Historical data setup failed")
                return
            
            # Setup ML model
            if not setup_ml_model():
                print("❌ ML model setup failed")
                return
            
            print("✅ Setup completed successfully")
        
        if args.test or args.all:
            print("\n🧪 Test Phase")
            print("-" * 20)
            
            if not test_monitoring():
                print("❌ Monitoring test failed")
                return
            
            print("✅ Tests completed successfully")
        
        if args.start or args.all:
            print("\n🚀 Start Phase")
            print("-" * 20)
            
            start_monitoring()
        
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        logger.error(f"Fatal error in main: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 