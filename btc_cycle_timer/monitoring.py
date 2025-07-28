# monitoring.py

import schedule
import time
import threading
from datetime import datetime, date
from typing import Dict, List
from btc_cycle_timer.logger import logger
from btc_cycle_timer.cycle_manager import cycle_manager
from btc_cycle_timer.config import get_current_cycle_phase, get_future_cycles
from btc_cycle_timer.timer import get_all_timers, get_forecast_dates
from btc_cycle_timer.price import get_btc_price
from btc_cycle_timer.calc import calculate_cycle_stats
from btc_cycle_timer.telegram import send_telegram_message
from btc_cycle_timer.utils import localize
from btc_cycle_timer.dynamic_predictor import dynamic_predictor
from btc_cycle_timer.forecast_updater import forecast_updater

class MonitoringSystem:
    """Automated monitoring system for BTC cycles"""
    
    def __init__(self, telegram_enabled=True, language="en"):
        self.telegram_enabled = telegram_enabled
        self.language = language
        self.last_phase = None
        self.phase_change_notified = False
        logger.info("Monitoring system initialized")
    
    def daily_morning_report(self):
        """Send daily morning report at 8:00 AM"""
        logger.info("Generating daily morning report")
        
        try:
            # Get current data
            current_price = get_btc_price()
            current_phase = get_current_cycle_phase()
            timers = get_all_timers()
            recommendations = cycle_manager.get_phase_recommendations()
            
            # Check for phase change
            if self.last_phase and self.last_phase != current_phase:
                self.phase_change_notified = False
                logger.info(f"Phase change detected: {self.last_phase} -> {current_phase}")
            
            # Create message
            message = self._create_daily_message(
                current_price, current_phase, timers, recommendations
            )
            
            # Send to Telegram
            if self.telegram_enabled:
                self._send_telegram_message(message, "daily")
            
            # Update last phase
            self.last_phase = current_phase
            
            logger.info("Daily morning report sent successfully")
            
        except Exception as e:
            logger.error(f"Error in daily morning report: {e}")
    
    def weekly_saturday_report(self):
        """Send weekly statistical report every Saturday"""
        logger.info("Generating weekly Saturday report")
        
        try:
            # Get comprehensive data
            current_price = get_btc_price()
            current_phase = get_current_cycle_phase()
            timers = get_all_timers()
            stats = calculate_cycle_stats()
            cycle_stats = cycle_manager.get_cycle_statistics()
            future_cycles = get_future_cycles(3)
            
            # Get dynamic predictions
            try:
                dynamic_prediction = dynamic_predictor.make_ensemble_prediction()
            except Exception as e:
                logger.warning(f"Dynamic prediction failed: {e}")
                dynamic_prediction = None
            
            try:
                forecast_update = forecast_updater.generate_update_report()
            except Exception as e:
                logger.warning(f"Forecast update failed: {e}")
                forecast_update = None
            
            # Create message
            message = self._create_weekly_message(
                current_price, current_phase, timers, stats, 
                cycle_stats, future_cycles, dynamic_prediction, forecast_update
            )
            
            # Send to Telegram
            if self.telegram_enabled:
                self._send_telegram_message(message, "weekly")
            
            logger.info("Weekly Saturday report sent successfully")
            
        except Exception as e:
            logger.error(f"Error in weekly Saturday report: {e}")
    
    def phase_change_notification(self):
        """Send notification when cycle phase changes"""
        if self.phase_change_notified:
            return
        
        current_phase = get_current_cycle_phase()
        if self.last_phase and self.last_phase != current_phase:
            logger.info(f"Sending phase change notification: {self.last_phase} -> {current_phase}")
            
            try:
                current_price = get_btc_price()
                recommendations = cycle_manager.get_phase_recommendations()
                
                message = self._create_phase_change_message(
                    self.last_phase, current_phase, current_price, recommendations
                )
                
                if self.telegram_enabled:
                    self._send_telegram_message(message, "phase_change")
                
                self.phase_change_notified = True
                logger.info("Phase change notification sent")
                
            except Exception as e:
                logger.error(f"Error in phase change notification: {e}")
    
    def _create_daily_message(self, price: float, phase: str, timers: Dict, recommendations: Dict) -> str:
        """Create daily morning message"""
        emoji_map = {
            "accumulation": "🟢",
            "parabolic": "🟡", 
            "distribution": "🟠",
            "capitulation": "🔴"
        }
        
        message = f"""
🌅 *Доброго ранку! BTC Cycle Update*

💰 *Ціна BTC:* ${price:,.2f}
{emoji_map.get(phase, "⚪")} *Фаза циклу:* {phase.upper()}

⏰ *Таймери:*
• До халвінгу: {timers['halving']} днів
• До піку: {timers['peak']} днів  
• До дна: {timers['bottom']} днів

💡 *Рекомендація:* {recommendations['strategy']}
⚠️ *Рівень ризику:* {recommendations['risk_level']}
⏱️ *Часові рамки:* {recommendations['timeframe']}

📊 *Ключові індикатори:*
"""
        
        for indicator in recommendations['key_indicators']:
            message += f"• {indicator}\n"
        
        message += f"\n🕐 {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        return message
    
    def _create_weekly_message(self, price: float, phase: str, timers: Dict, 
                             stats: Dict, cycle_stats: Dict, future_cycles: List, 
                             dynamic_prediction: Dict = None, forecast_update: str = None) -> str:
        """Create weekly statistical message"""
        message = f"""
📊 *Щотижнева статистика BTC Cycle*

💰 *Ціна BTC:* ${price:,.2f}
🔄 *Фаза циклу:* {phase.upper()}

⏰ *Таймери:*
• До халвінгу: {timers['halving']} днів
• До піку: {timers['peak']} днів
• До дна: {timers['bottom']} днів

📈 *Статистика циклу:*
• ROI від дна: {stats['roi_from_bottom']:.2f}%
• Прогрес циклу: {stats['percent_progress']:.2f}%
• Прогнозований пік: ${stats['forecast_peak_price']:,}

🔮 *Майбутні цикли:*
"""
        
        for cycle in future_cycles[:2]:  # Show next 2 cycles
            message += f"• Цикл {cycle['cycle_number']}: Пік {cycle['peak_date']}\n"
        
        if "error" not in cycle_stats:
            message += f"\n📊 *Історична статистика:*\n"
            message += f"• Середня тривалість: {cycle_stats.get('average_cycle_length_days', 'N/A')} днів\n"
            message += f"• Середнє зростання: {cycle_stats.get('average_price_ratio', 'N/A'):.1f}x"
        
        message += f"\n\n🕐 {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        return message
    
    def _create_phase_change_message(self, old_phase: str, new_phase: str, 
                                   price: float, recommendations: Dict) -> str:
        """Create phase change notification message"""
        emoji_map = {
            "accumulation": "🟢",
            "parabolic": "🟡",
            "distribution": "🟠", 
            "capitulation": "🔴"
        }
        
        message = f"""
🚨 *ЗМІНА ФАЗИ ЦИКЛУ!*

{emoji_map.get(old_phase, "⚪")} {old_phase.upper()} → {emoji_map.get(new_phase, "⚪")} {new_phase.upper()}

💰 *Ціна BTC:* ${price:,.2f}

💡 *Нова стратегія:* {recommendations['strategy']}
⚠️ *Рівень ризику:* {recommendations['risk_level']}
⏱️ *Часові рамки:* {recommendations['timeframe']}

📊 *Ключові індикатори:*
"""
        
        for indicator in recommendations['key_indicators']:
            message += f"• {indicator}\n"
        
        message += f"\n🕐 {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        return message
    
    def _send_telegram_message(self, message: str, report_type: str):
        """Send message to Telegram"""
        try:
            # Use existing telegram function with enhanced message
            # For now, we'll use a simplified approach
            logger.info(f"Sending {report_type} report to Telegram")
            # send_telegram_message(message)  # Uncomment when ready
            print(f"📱 Telegram message ({report_type}):\n{message}")
        except Exception as e:
            logger.error(f"Failed to send Telegram message: {e}")
    
    def start_monitoring(self):
        """Start the monitoring system"""
        logger.info("Starting monitoring system")
        
        # Schedule daily morning report at 8:00 AM
        schedule.every().day.at("08:00").do(self.daily_morning_report)
        
        # Schedule weekly Saturday report at 9:00 AM
        schedule.every().saturday.at("09:00").do(self.weekly_saturday_report)
        
        # Schedule phase change check every hour
        schedule.every().hour.do(self.phase_change_notification)
        
        # Run initial phase detection
        self.last_phase = get_current_cycle_phase()
        
        print("🔄 Monitoring system started!")
        print("📅 Daily reports: 8:00 AM")
        print("📊 Weekly reports: Saturday 9:00 AM")
        print("🔄 Phase change notifications: Every hour")
        
        # Run the scheduler
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    def run_once(self, report_type="daily"):
        """Run a single report (for testing)"""
        if report_type == "daily":
            self.daily_morning_report()
        elif report_type == "weekly":
            self.weekly_saturday_report()
        elif report_type == "phase_change":
            self.phase_change_notification()

# Create global instance
monitoring_system = MonitoringSystem()

# Export functions
__all__ = ['MonitoringSystem', 'monitoring_system'] 