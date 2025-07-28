# forecast_updater.py

import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional
import json
from pathlib import Path
from btc_cycle_timer.logger import logger
from btc_cycle_timer.chart import load_price_data
from btc_cycle_timer.cycle_analysis import cycle_analyzer
from btc_cycle_timer.dynamic_predictor import dynamic_predictor
from btc_cycle_timer.config import get_current_cycle_phase, get_future_cycles

class ForecastUpdater:
    """
    Automated forecast update system with dynamic recalculation
    """
    
    def __init__(self):
        self.update_history = []
        self.forecast_changes = []
        self.last_update = None
        self.update_threshold = 0.05  # 5% change threshold
        self.data_path = Path(__file__).parent / "forecast_data"
        self.data_path.mkdir(exist_ok=True)
        logger.info("Forecast Updater initialized")
    
    def check_forecast_update_needed(self) -> bool:
        """
        Check if forecast update is needed based on recent data
        """
        logger.info("Checking if forecast update is needed")
        
        try:
            # Get current market conditions
            current_price = self._get_current_price()
            current_phase = get_current_cycle_phase()
            
            # Get latest prediction
            latest_prediction = dynamic_predictor.make_ensemble_prediction()
            
            if not latest_prediction:
                return False
            
            # Check for significant changes
            price_change = abs(latest_prediction['predicted_change'])
            model_agreement = latest_prediction['model_agreement']
            
            # Update conditions
            needs_update = (
                price_change > 10 or  # Significant price movement expected
                model_agreement < 0.7 or  # Low model agreement
                self._days_since_last_update() > 7  # Weekly update
            )
            
            logger.info(f"Forecast update needed: {needs_update} (price_change: {price_change:.1f}%, agreement: {model_agreement:.1%})")
            
            return needs_update
            
        except Exception as e:
            logger.error(f"Error checking forecast update: {e}")
            return False
    
    def perform_forecast_update(self) -> Dict:
        """
        Perform comprehensive forecast update
        """
        logger.info("Performing forecast update")
        
        try:
            # Get current data
            current_price = self._get_current_price()
            current_phase = get_current_cycle_phase()
            
            # Get previous forecast
            previous_forecast = self._get_previous_forecast()
            
            # Update dynamic models if needed
            if dynamic_predictor.adaptive_model_update():
                logger.info("Dynamic models updated")
            
            # Generate new forecast
            new_forecast = self._generate_comprehensive_forecast()
            
            # Calculate changes
            forecast_changes = self._calculate_forecast_changes(previous_forecast, new_forecast)
            
            # Save update
            update_record = {
                'update_date': datetime.now().isoformat(),
                'previous_forecast': previous_forecast,
                'new_forecast': new_forecast,
                'changes': forecast_changes,
                'current_price': current_price,
                'current_phase': current_phase
            }
            
            self.update_history.append(update_record)
            self._save_update_history()
            
            # Log significant changes
            if forecast_changes['significant_changes']:
                logger.warning(f"Significant forecast changes detected: {forecast_changes['significant_changes']}")
            
            self.last_update = datetime.now()
            
            logger.info("Forecast update completed successfully")
            return update_record
            
        except Exception as e:
            logger.error(f"Error performing forecast update: {e}")
            return None
    
    def _generate_comprehensive_forecast(self) -> Dict:
        """
        Generate comprehensive forecast using multiple methods
        """
        logger.info("Generating comprehensive forecast")
        
        # Dynamic ML prediction
        ml_prediction = dynamic_predictor.make_ensemble_prediction()
        
        # Cycle-based prediction
        cycle_prediction = self._get_cycle_based_prediction()
        
        # Technical analysis prediction
        technical_prediction = self._get_technical_prediction()
        
        # Combine predictions
        combined_forecast = self._combine_predictions(
            ml_prediction, cycle_prediction, technical_prediction
        )
        
        return combined_forecast
    
    def _get_cycle_based_prediction(self) -> Dict:
        """
        Generate prediction based on cycle analysis
        """
        try:
            current_cycle_info = cycle_analyzer.get_current_cycle_info()
            current_phase = get_current_cycle_phase()
            
            # Get historical cycle data
            historical_analysis = cycle_analyzer.analyze_historical_cycles()
            
            # Calculate cycle-based prediction
            if historical_analysis:
                avg_price_ratio = np.mean([c['price_ratio'] for c in historical_analysis.values()])
                current_price = self._get_current_price()
                
                # Estimate peak price based on historical patterns
                estimated_peak = current_price * avg_price_ratio
                
                return {
                    'method': 'cycle_analysis',
                    'estimated_peak': estimated_peak,
                    'current_phase': current_phase,
                    'cycle_progress': current_cycle_info['progress_percent'],
                    'confidence': 0.8
                }
            
            return {'method': 'cycle_analysis', 'error': 'No historical data'}
            
        except Exception as e:
            logger.error(f"Error in cycle-based prediction: {e}")
            return {'method': 'cycle_analysis', 'error': str(e)}
    
    def _get_technical_prediction(self) -> Dict:
        """
        Generate prediction based on technical analysis
        """
        try:
            df = load_price_data()
            df['date'] = pd.to_datetime(df['date'])
            
            # Calculate technical indicators
            df['sma_20'] = df['close'].rolling(20).mean()
            df['sma_50'] = df['close'].rolling(50).mean()
            df['rsi'] = self._calculate_rsi(df['close'])
            
            current_price = df['close'].iloc[-1]
            sma_20 = df['sma_20'].iloc[-1]
            sma_50 = df['sma_50'].iloc[-1]
            rsi = df['rsi'].iloc[-1]
            
            # Technical analysis logic
            bullish_signals = 0
            bearish_signals = 0
            
            if current_price > sma_20:
                bullish_signals += 1
            else:
                bearish_signals += 1
            
            if current_price > sma_50:
                bullish_signals += 1
            else:
                bearish_signals += 1
            
            if 30 < rsi < 70:
                bullish_signals += 1
            elif rsi > 70:
                bearish_signals += 1
            elif rsi < 30:
                bullish_signals += 1
            
            # Calculate prediction
            signal_strength = (bullish_signals - bearish_signals) / 3
            predicted_change = signal_strength * 0.1  # 10% max change
            predicted_price = current_price * (1 + predicted_change)
            
            return {
                'method': 'technical_analysis',
                'predicted_price': predicted_price,
                'predicted_change': predicted_change * 100,
                'bullish_signals': bullish_signals,
                'bearish_signals': bearish_signals,
                'confidence': abs(signal_strength)
            }
            
        except Exception as e:
            logger.error(f"Error in technical prediction: {e}")
            return {'method': 'technical_analysis', 'error': str(e)}
    
    def _combine_predictions(self, ml_pred: Dict, cycle_pred: Dict, tech_pred: Dict) -> Dict:
        """
        Combine predictions from different methods
        """
        predictions = []
        weights = []
        
        # Add ML prediction
        if ml_pred and 'ensemble_prediction' in ml_pred:
            predictions.append(ml_pred['ensemble_prediction'])
            weights.append(0.5)  # 50% weight to ML
        
        # Add cycle prediction
        if cycle_pred and 'estimated_peak' in cycle_pred:
            predictions.append(cycle_pred['estimated_peak'])
            weights.append(0.3)  # 30% weight to cycle analysis
        
        # Add technical prediction
        if tech_pred and 'predicted_price' in tech_pred:
            predictions.append(tech_pred['predicted_price'])
            weights.append(0.2)  # 20% weight to technical analysis
        
        if not predictions:
            return {'error': 'No valid predictions available'}
        
        # Calculate weighted average
        total_weight = sum(weights)
        weighted_prediction = sum(p * w for p, w in zip(predictions, weights)) / total_weight
        
        current_price = self._get_current_price()
        
        return {
            'combined_prediction': weighted_prediction,
            'predicted_change': ((weighted_prediction - current_price) / current_price) * 100,
            'method_weights': dict(zip(['ml', 'cycle', 'technical'], weights)),
            'individual_predictions': {
                'ml': ml_pred.get('ensemble_prediction'),
                'cycle': cycle_pred.get('estimated_peak'),
                'technical': tech_pred.get('predicted_price')
            },
            'forecast_date': datetime.now().isoformat(),
            'confidence': self._calculate_combined_confidence(ml_pred, cycle_pred, tech_pred)
        }
    
    def _calculate_combined_confidence(self, ml_pred: Dict, cycle_pred: Dict, tech_pred: Dict) -> float:
        """
        Calculate combined confidence score
        """
        confidences = []
        
        if ml_pred and 'model_agreement' in ml_pred:
            confidences.append(ml_pred['model_agreement'])
        
        if cycle_pred and 'confidence' in cycle_pred:
            confidences.append(cycle_pred['confidence'])
        
        if tech_pred and 'confidence' in tech_pred:
            confidences.append(tech_pred['confidence'])
        
        return np.mean(confidences) if confidences else 0.5
    
    def _calculate_forecast_changes(self, previous: Dict, current: Dict) -> Dict:
        """
        Calculate changes between forecasts
        """
        if not previous or 'error' in previous:
            return {'significant_changes': False, 'changes': {}}
        
        changes = {}
        significant_changes = []
        
        # Compare predictions
        if 'combined_prediction' in current and 'combined_prediction' in previous:
            price_change = abs(current['combined_prediction'] - previous['combined_prediction'])
            price_change_percent = (price_change / previous['combined_prediction']) * 100
            
            changes['price_change'] = price_change_percent
            
            if price_change_percent > self.update_threshold * 100:
                significant_changes.append(f"Price prediction changed by {price_change_percent:.1f}%")
        
        # Compare confidence
        if 'confidence' in current and 'confidence' in previous:
            confidence_change = current['confidence'] - previous['confidence']
            changes['confidence_change'] = confidence_change
            
            if abs(confidence_change) > 0.1:
                significant_changes.append(f"Confidence changed by {confidence_change:.1%}")
        
        return {
            'significant_changes': len(significant_changes) > 0,
            'changes': changes,
            'change_details': significant_changes
        }
    
    def _get_current_price(self) -> float:
        """Get current BTC price"""
        try:
            from btc_cycle_timer.price import get_btc_price
            return get_btc_price() or 0
        except Exception as e:
            logger.error(f"Error getting current price: {e}")
            return 0
    
    def _get_previous_forecast(self) -> Optional[Dict]:
        """Get previous forecast from history"""
        if self.update_history:
            return self.update_history[-1]['new_forecast']
        return None
    
    def _days_since_last_update(self) -> int:
        """Calculate days since last update"""
        if self.last_update:
            return (datetime.now() - self.last_update).days
        return 999  # Large number to force update
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate RSI indicator"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def _save_update_history(self):
        """Save update history to file"""
        try:
            history_file = self.data_path / "forecast_updates.json"
            with open(history_file, 'w') as f:
                json.dump(self.update_history, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving update history: {e}")
    
    def load_update_history(self):
        """Load update history from file"""
        try:
            history_file = self.data_path / "forecast_updates.json"
            if history_file.exists():
                with open(history_file, 'r') as f:
                    self.update_history = json.load(f)
        except Exception as e:
            logger.error(f"Error loading update history: {e}")
    
    def generate_update_report(self) -> str:
        """
        Generate comprehensive update report
        """
        logger.info("Generating forecast update report")
        
        # Load history if not loaded
        if not self.update_history:
            self.load_update_history()
        
        # Perform update if needed
        if self.check_forecast_update_needed():
            update_result = self.perform_forecast_update()
        else:
            update_result = None
        
        # Get latest forecast
        latest_forecast = self._get_previous_forecast()
        
        # Create report
        report = f"""
🔄 *Forecast Update Report*

📊 *Latest Forecast:*
"""
        
        if latest_forecast and 'error' not in latest_forecast:
            report += f"• Predicted Price: ${latest_forecast['combined_prediction']:,.2f}\n"
            report += f"• Expected Change: {latest_forecast['predicted_change']:+.2f}%\n"
            report += f"• Confidence: {latest_forecast['confidence']:.1%}\n"
            
            report += f"\n🔍 *Method Weights:*\n"
            for method, weight in latest_forecast['method_weights'].items():
                report += f"• {method.title()}: {weight:.1%}\n"
        else:
            report += "• No valid forecast available\n"
        
        if update_result:
            report += f"\n🔄 *Update Status:*\n"
            report += f"• Update Performed: ✅\n"
            if update_result['changes']['significant_changes']:
                report += f"• Significant Changes: ⚠️\n"
                for change in update_result['changes']['change_details']:
                    report += f"  - {change}\n"
            else:
                report += f"• Significant Changes: ❌\n"
        else:
            report += f"\n🔄 *Update Status:*\n"
            report += f"• Update Performed: ❌ (not needed)\n"
        
        report += f"\n📈 *Update History:*\n"
        report += f"• Total Updates: {len(self.update_history)}\n"
        if self.last_update:
            report += f"• Last Update: {self.last_update.strftime('%Y-%m-%d %H:%M')}\n"
        
        report += f"\n🕐 {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        return report

# Create global instance
forecast_updater = ForecastUpdater()

# Export functions
__all__ = ['ForecastUpdater', 'forecast_updater'] 