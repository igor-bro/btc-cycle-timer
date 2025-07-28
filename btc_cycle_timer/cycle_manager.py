# cycle_manager.py

from datetime import date, datetime, timedelta
from typing import Dict, List, Optional
import json
from pathlib import Path
from btc_cycle_timer.logger import logger
from btc_cycle_timer.config import (
    CYCLE_PEAK, CYCLE_BOTTOM, CYCLE_BOTTOM_DATE,
    get_cycle_history, save_cycle_history, calculate_next_cycle_dates,
    get_current_cycle_phase, should_update_cycle_config, get_future_cycles,
    validate_cycle_config
)

class CycleManager:
    """Manages Bitcoin cycle data and automatic updates"""
    
    def __init__(self):
        self.history = get_cycle_history()
        self.current_phase = get_current_cycle_phase()
        logger.info(f"CycleManager initialized. Current phase: {self.current_phase}")
    
    def check_and_update_cycle(self) -> bool:
        """Check if cycle needs updating and perform update if needed"""
        if not should_update_cycle_config():
            logger.debug("No cycle update needed")
            return False
        
        logger.info("Cycle update needed - performing update")
        
        # Get current BTC price to determine if we've reached peak
        from btc_cycle_timer.price import get_btc_price
        current_price = get_btc_price()
        
        today = date.today()
        
        # Check if we've passed the peak date
        if today > CYCLE_PEAK:
            self._update_cycle_after_peak(current_price)
        elif today > CYCLE_BOTTOM:
            self._update_cycle_after_bottom()
        
        return True
    
    def _update_cycle_after_peak(self, peak_price: Optional[float]):
        """Update cycle configuration after peak is reached"""
        logger.info("Updating cycle configuration after peak")
        
        # Save current cycle to history
        cycle_data = {
            "peak_date": CYCLE_PEAK.isoformat(),
            "bottom_date": CYCLE_BOTTOM_DATE.date().isoformat(),
            "peak_price": peak_price,
            "bottom_price": 15700,  # Historical bottom price
            "cycle_length_days": (CYCLE_PEAK - CYCLE_BOTTOM_DATE.date()).days
        }
        
        self.history.append(cycle_data)
        save_cycle_history(self.history)
        
        # Calculate next cycle dates
        next_peak, next_bottom = calculate_next_cycle_dates(CYCLE_PEAK, CYCLE_BOTTOM_DATE.date())
        
        logger.info(f"Next cycle forecast: Peak {next_peak}, Bottom {next_bottom}")
        
        # Update configuration (this would require config file modification)
        self._update_config_file(next_peak, next_bottom)
    
    def _update_cycle_after_bottom(self):
        """Update cycle configuration after bottom is reached"""
        logger.info("Updating cycle configuration after bottom")
        
        # Get actual bottom price
        from btc_cycle_timer.price import get_btc_price
        bottom_price = get_btc_price()
        
        # Save bottom data
        bottom_data = {
            "bottom_date": CYCLE_BOTTOM.isoformat(),
            "bottom_price": bottom_price,
            "confirmed": True
        }
        
        # Update the last cycle entry with bottom data
        if self.history:
            self.history[-1].update(bottom_data)
            save_cycle_history(self.history)
    
    def _update_config_file(self, next_peak: date, next_bottom: date):
        """Update configuration file with new cycle dates"""
        config_file = Path(__file__).parent / "config.py"
        
        if not config_file.exists():
            logger.error("Config file not found")
            return
        
        try:
            # Read current config
            with open(config_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Update cycle dates
            content = content.replace(
                f"CYCLE_PEAK = date({CYCLE_PEAK.year}, {CYCLE_PEAK.month}, {CYCLE_PEAK.day})",
                f"CYCLE_PEAK = date({next_peak.year}, {next_peak.month}, {next_peak.day})"
            )
            
            content = content.replace(
                f"CYCLE_BOTTOM = date({CYCLE_BOTTOM.year}, {CYCLE_BOTTOM.month}, {CYCLE_BOTTOM.day})",
                f"CYCLE_BOTTOM = date({next_bottom.year}, {next_bottom.month}, {next_bottom.day})"
            )
            
            # Write updated config
            with open(config_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info("Configuration file updated successfully")
            
        except Exception as e:
            logger.error(f"Failed to update config file: {e}")
    
    def get_cycle_statistics(self) -> Dict:
        """Get comprehensive cycle statistics"""
        if not self.history:
            return {"error": "No cycle history available"}
        
        # Calculate average cycle length
        cycle_lengths = [cycle.get("cycle_length_days", 0) for cycle in self.history if cycle.get("cycle_length_days")]
        avg_cycle_length = sum(cycle_lengths) / len(cycle_lengths) if cycle_lengths else 0
        
        # Calculate price ratios
        price_ratios = []
        for cycle in self.history:
            if cycle.get("peak_price") and cycle.get("bottom_price"):
                ratio = cycle["peak_price"] / cycle["bottom_price"]
                price_ratios.append(ratio)
        
        avg_price_ratio = sum(price_ratios) / len(price_ratios) if price_ratios else 0
        
        return {
            "total_cycles": len(self.history),
            "average_cycle_length_days": avg_cycle_length,
            "average_price_ratio": avg_price_ratio,
            "current_phase": self.current_phase,
            "cycles": self.history
        }
    
    def get_phase_recommendations(self) -> Dict:
        """Get recommendations based on current cycle phase"""
        recommendations = {
            "accumulation": {
                "strategy": "Accumulate BTC gradually",
                "risk_level": "Low",
                "timeframe": "Long-term (2-4 years)",
                "key_indicators": ["Price consolidation", "Low volume", "Fear sentiment"]
            },
            "parabolic": {
                "strategy": "Hold and monitor for distribution signals",
                "risk_level": "Medium-High",
                "timeframe": "Medium-term (6-18 months)",
                "key_indicators": ["Rapid price increase", "High volume", "FOMO sentiment"]
            },
            "distribution": {
                "strategy": "Consider taking profits gradually",
                "risk_level": "High",
                "timeframe": "Short-term (3-6 months)",
                "key_indicators": ["Price volatility", "Divergence patterns", "Smart money selling"]
            },
            "capitulation": {
                "strategy": "Prepare for accumulation phase",
                "risk_level": "Very High",
                "timeframe": "Short-term (1-3 months)",
                "key_indicators": ["Sharp price decline", "Panic selling", "Extreme fear"]
            }
        }
        
        return recommendations.get(self.current_phase, {"strategy": "Monitor market conditions"})
    
    def export_cycle_data(self, filename: str = "cycle_analysis.json"):
        """Export cycle data for external analysis"""
        data = {
            "current_phase": self.current_phase,
            "statistics": self.get_cycle_statistics(),
            "recommendations": self.get_phase_recommendations(),
            "future_cycles": get_future_cycles(5),
            "export_date": datetime.now().isoformat()
        }
        
        export_file = Path(filename)
        try:
            with open(export_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            logger.info(f"Cycle data exported to {filename}")
            return True
        except Exception as e:
            logger.error(f"Failed to export cycle data: {e}")
            return False

# Create global instance
cycle_manager = CycleManager()

# Export functions
__all__ = ['CycleManager', 'cycle_manager'] 