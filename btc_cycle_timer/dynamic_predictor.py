# dynamic_predictor.py

import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta
from typing import Dict, List, Tuple, Optional
import json
from pathlib import Path
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib
from btc_cycle_timer.logger import logger
from btc_cycle_timer.chart import load_price_data
from btc_cycle_timer.cycle_analysis import cycle_analyzer

class DynamicPredictor:
    """
    Dynamic prediction system with adaptive algorithms and forecast analysis
    """
    
    def __init__(self):
        self.models = {
            'random_forest': RandomForestRegressor(n_estimators=100, random_state=42),
            'gradient_boosting': GradientBoostingRegressor(n_estimators=100, random_state=42),
            'linear': LinearRegression()
        }
        self.scalers = {}
        self.feature_columns = []
        self.predictions_history = []
        self.forecast_accuracy = {}
        self.model_path = Path(__file__).parent / "models"
        self.model_path.mkdir(exist_ok=True)
        logger.info("Dynamic Predictor initialized")
        
        # Try to load existing models
        self.load_models()
    
    def prepare_advanced_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Prepare optimized features for dynamic prediction (reduced to avoid overfitting)
        """
        logger.info("Preparing optimized features for dynamic prediction")
        
        # Convert date to datetime
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        
        # Essential price features (reduced)
        df['price_change'] = df['close'].pct_change()
        df['price_change_30d'] = df['close'].pct_change(30)
        
        # Key moving averages
        df['ma_20'] = df['close'].rolling(20).mean()
        df['ma_50'] = df['close'].rolling(50).mean()
        df['ma_200'] = df['close'].rolling(200).mean()
        
        # Price ratios to moving averages
        df['price_ma20_ratio'] = df['close'] / df['ma_20']
        df['price_ma50_ratio'] = df['close'] / df['ma_50']
        
        # Pivot points (simplified)
        df['pivot'] = (df['high'] + df['low'] + df['close']) / 3
        df['support_1'] = 2 * df['pivot'] - df['high']
        df['resistance_1'] = 2 * df['pivot'] - df['low']
        
        # RSI
        df['rsi_14'] = self._calculate_rsi(df['close'], 14)
        
        # MACD
        df['macd'] = self._calculate_macd(df['close'])
        
        # Volume features (if available)
        if 'volume' in df.columns:
            df['volume_ma_20'] = df['volume'].rolling(20).mean()
            df['volume_ratio'] = df['volume'] / df['volume_ma_20']
        else:
            # Create dummy volume features if not available
            df['volume_ma_20'] = 1.0
            df['volume_ratio'] = 1.0
        
        # Cycle-based features (essential)
        cycle_structure = cycle_analyzer.get_cycle_structure()
        current_cycle = cycle_structure['cycles'][-1]
        
        # Days since halving
        df['days_since_halving'] = (df['date'] - current_cycle['halving_start']).dt.days
        
        # Cycle progress percentage
        total_cycle_days = (current_cycle['halving_end'] - current_cycle['halving_start']).days
        df['cycle_progress'] = df['days_since_halving'] / total_cycle_days * 100
        
        # Target: price in 30 days
        df['target_30d'] = df['close'].shift(-30)
        
        # Remove NaN values
        df = df.dropna()
        
        # Select optimized feature columns (reduced from 19+ to 12)
        self.feature_columns = [
            'price_change', 'price_change_30d',
            'ma_20', 'ma_50', 'ma_200',
            'price_ma20_ratio', 'price_ma50_ratio',
            'pivot', 'support_1', 'resistance_1',
            'rsi_14', 'macd',
            'volume_ratio',
            'days_since_halving', 'cycle_progress'
        ]
        
        logger.info(f"Prepared {len(self.feature_columns)} optimized features")
        return df
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate RSI indicator"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def _calculate_macd(self, prices: pd.Series, fast: int = 12, slow: int = 26) -> pd.Series:
        """Calculate MACD indicator"""
        ema_fast = prices.ewm(span=fast).mean()
        ema_slow = prices.ewm(span=slow).mean()
        macd = ema_fast - ema_slow
        return macd
    
    def _calculate_bollinger_bands(self, prices: pd.Series, period: int = 20, std_dev: int = 2) -> Tuple[pd.Series, pd.Series]:
        """Calculate Bollinger Bands"""
        sma = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()
        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)
        return upper_band, lower_band
    
    def train_ensemble_models(self, df: pd.DataFrame) -> Dict:
        """
        Train ensemble of models for robust predictions
        """
        logger.info("Training ensemble models")
        
        # Prepare features
        df = self.prepare_advanced_features(df)
        
        # Split data
        train_size = int(len(df) * 0.8)
        train_df = df[:train_size]
        test_df = df[train_size:]
        
        results = {}
        
        for model_name, model in self.models.items():
            logger.info(f"Training {model_name} model")
            
            # Prepare training data
            X_train = train_df[self.feature_columns]
            y_train = train_df['target_30d']
            
            X_test = test_df[self.feature_columns]
            y_test = test_df['target_30d']
            
            # Scale features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            self.scalers[model_name] = scaler
            
            # Train model
            model.fit(X_train_scaled, y_train)
            
            # Make predictions
            y_pred_train = model.predict(X_train_scaled)
            y_pred_test = model.predict(X_test_scaled)
            
            # Calculate metrics
            metrics = {
                'train_mae': mean_absolute_error(y_train, y_pred_train),
                'test_mae': mean_absolute_error(y_test, y_pred_test),
                'train_rmse': np.sqrt(mean_squared_error(y_train, y_pred_train)),
                'test_rmse': np.sqrt(mean_squared_error(y_test, y_pred_test)),
                'train_r2': r2_score(y_train, y_pred_train),
                'test_r2': r2_score(y_test, y_pred_test)
            }
            
            results[model_name] = metrics
            logger.info(f"{model_name} - Test R²: {metrics['test_r2']:.3f}, MAE: ${metrics['test_mae']:,.2f}")
        
        # Save models
        self.save_models()
        
        return results
    
    def make_ensemble_prediction(self, days_ahead: int = 30) -> Dict:
        """
        Make ensemble prediction using all trained models
        """
        if not self.models or not self.scalers:
            logger.error("Models not trained. Please train models first.")
            return None
        
        try:
            # Load latest data
            df = load_price_data()
            df = self.prepare_advanced_features(df)
            
            # Get latest features
            latest_features = df[self.feature_columns].iloc[-1:]
            
            predictions = {}
            ensemble_prediction = 0
            weights = {'random_forest': 0.4, 'gradient_boosting': 0.4, 'linear': 0.2}
            
            for model_name, model in self.models.items():
                if model_name in self.scalers:
                    # Scale features
                    latest_features_scaled = self.scalers[model_name].transform(latest_features)
                    
                    # Make prediction
                    prediction = model.predict(latest_features_scaled)[0]
                    predictions[model_name] = prediction
                    
                    # Weighted ensemble
                    ensemble_prediction += prediction * weights[model_name]
            
            current_price = df['close'].iloc[-1]
            
            # Calculate confidence intervals
            predictions_list = list(predictions.values())
            prediction_std = np.std(predictions_list)
            
            result = {
                'current_price': current_price,
                'ensemble_prediction': ensemble_prediction,
                'individual_predictions': predictions,
                'predicted_change': ((ensemble_prediction - current_price) / current_price) * 100,
                'confidence_interval': [
                    ensemble_prediction - 1.96 * prediction_std,
                    ensemble_prediction + 1.96 * prediction_std
                ],
                'prediction_date': datetime.now().isoformat(),
                'target_date': (datetime.now() + timedelta(days=days_ahead)).isoformat(),
                'model_agreement': 1 - (prediction_std / ensemble_prediction) if ensemble_prediction > 0 else 0
            }
            
            # Save prediction to history
            self.predictions_history.append(result)
            self.save_predictions_history()
            
            logger.info(f"Ensemble prediction: ${ensemble_prediction:,.2f} ({result['predicted_change']:+.2f}%)")
            
            return result
            
        except Exception as e:
            logger.error(f"Error making ensemble prediction: {e}")
            return None
    
    def analyze_forecast_accuracy(self) -> Dict:
        """
        Analyze accuracy of past forecasts and update model weights
        """
        logger.info("Analyzing forecast accuracy")
        
        if not self.predictions_history:
            return {"error": "No predictions to analyze"}
        
        # Load actual prices
        df = load_price_data()
        df['date'] = pd.to_datetime(df['date'])
        
        accuracy_analysis = {}
        
        for pred in self.predictions_history:
            try:
                pred_date = datetime.fromisoformat(pred['prediction_date'])
                target_date = datetime.fromisoformat(pred['target_date'])
                
                # Find actual price at target date
                actual_data = df[df['date'] >= target_date].iloc[0] if len(df[df['date'] >= target_date]) > 0 else None
                
                if actual_data is not None:
                    actual_price = actual_data['close']
                    predicted_price = pred['ensemble_prediction']
                    
                    error = abs(actual_price - predicted_price)
                    error_percent = (error / actual_price) * 100
                    accuracy = max(0, 100 - error_percent)
                    
                    # Analyze individual model accuracy
                    model_accuracy = {}
                    for model_name, model_pred in pred['individual_predictions'].items():
                        model_error = abs(actual_price - model_pred)
                        model_accuracy[model_name] = max(0, 100 - (model_error / actual_price) * 100)
                    
                    accuracy_analysis[pred_date.isoformat()] = {
                        'predicted_price': predicted_price,
                        'actual_price': actual_price,
                        'error': error,
                        'error_percent': error_percent,
                        'accuracy': accuracy,
                        'model_accuracy': model_accuracy
                    }
                    
            except Exception as e:
                logger.error(f"Error analyzing prediction: {e}")
        
        # Calculate overall metrics
        if accuracy_analysis:
            avg_accuracy = np.mean([a['accuracy'] for a in accuracy_analysis.values()])
            avg_error_percent = np.mean([a['error_percent'] for a in accuracy_analysis.values()])
            
            # Calculate model performance
            model_performance = {}
            for model_name in self.models.keys():
                accuracies = [a['model_accuracy'].get(model_name, 0) for a in accuracy_analysis.values()]
                model_performance[model_name] = np.mean(accuracies) if accuracies else 0
            
            self.forecast_accuracy = {
                'total_predictions': len(accuracy_analysis),
                'average_accuracy': avg_accuracy,
                'average_error_percent': avg_error_percent,
                'model_performance': model_performance,
                'detailed_analysis': accuracy_analysis
            }
            
            logger.info(f"Forecast accuracy analysis: {avg_accuracy:.1f}% average accuracy")
        
        return self.forecast_accuracy
    
    def adaptive_model_update(self) -> bool:
        """
        Adaptively update models based on recent performance
        """
        logger.info("Performing adaptive model update")
        
        # Analyze recent accuracy
        accuracy_data = self.analyze_forecast_accuracy()
        
        if 'error' in accuracy_data:
            logger.warning("Cannot update models - no accuracy data available")
            return False
        
        # Check if update is needed (accuracy below threshold)
        if accuracy_data['average_accuracy'] < 70:
            logger.info("Accuracy below threshold, retraining models")
            
            # Retrain with more recent data
            df = load_price_data()
            self.train_ensemble_models(df)
            
            return True
        
        return False
    
    def save_models(self):
        """Save trained models"""
        try:
            for model_name, model in self.models.items():
                model_file = self.model_path / f"dynamic_{model_name}.joblib"
                joblib.dump(model, model_file)
            
            # Save scalers
            scaler_file = self.model_path / "dynamic_scalers.joblib"
            joblib.dump(self.scalers, scaler_file)
            
            logger.info("Dynamic models saved successfully")
            
        except Exception as e:
            logger.error(f"Error saving dynamic models: {e}")
    
    def load_models(self):
        """Load trained models"""
        try:
            for model_name in self.models.keys():
                model_file = self.model_path / f"dynamic_{model_name}.joblib"
                if model_file.exists():
                    self.models[model_name] = joblib.load(model_file)
            
            # Load scalers
            scaler_file = self.model_path / "dynamic_scalers.joblib"
            if scaler_file.exists():
                self.scalers = joblib.load(scaler_file)
            
            logger.info("Dynamic models loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error loading dynamic models: {e}")
            return False
    
    def save_predictions_history(self):
        """Save predictions history"""
        try:
            history_file = self.model_path / "dynamic_predictions_history.json"
            with open(history_file, 'w') as f:
                json.dump(self.predictions_history, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving predictions history: {e}")
    
    def load_predictions_history(self):
        """Load predictions history"""
        try:
            history_file = self.model_path / "dynamic_predictions_history.json"
            if history_file.exists():
                with open(history_file, 'r') as f:
                    self.predictions_history = json.load(f)
        except Exception as e:
            logger.error(f"Error loading predictions history: {e}")
    
    def generate_dynamic_report(self) -> str:
        """
        Generate comprehensive dynamic prediction report
        """
        logger.info("Generating dynamic prediction report")
        
        # Load history if not loaded
        if not self.predictions_history:
            self.load_predictions_history()
        
        # Get current prediction
        current_prediction = self.make_ensemble_prediction()
        
        # Get accuracy analysis
        accuracy_data = self.analyze_forecast_accuracy()
        
        # Create report
        report = f"""
🤖 *Dynamic Prediction Report*

📊 *Current Ensemble Prediction (30 days):*
• Current Price: ${current_prediction['current_price']:,.2f}
• Predicted Price: ${current_prediction['ensemble_prediction']:,.2f}
• Expected Change: {current_prediction['predicted_change']:+.2f}%
• Model Agreement: {current_prediction['model_agreement']:.1%}

📈 *Individual Model Predictions:*
"""
        
        for model_name, prediction in current_prediction['individual_predictions'].items():
            change = ((prediction - current_prediction['current_price']) / current_prediction['current_price']) * 100
            report += f"• {model_name.title()}: ${prediction:,.2f} ({change:+.2f}%)\n"
        
        report += f"\n📊 *Forecast Accuracy:*\n"
        report += f"• Total Predictions: {accuracy_data.get('total_predictions', 'N/A')}\n"
        report += f"• Average Accuracy: {accuracy_data.get('average_accuracy', 'N/A'):.1f}%\n"
        report += f"• Average Error: {accuracy_data.get('average_error_percent', 'N/A'):.1f}%\n"

        report += f"\n🔍 *Model Performance:*\n"
        
        for model_name, performance in accuracy_data.get('model_performance', {}).items():
            report += f"• {model_name.title()}: {performance:.1f}%\n"
        
        report += f"\n🕐 {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        return report

# Create global instance
dynamic_predictor = DynamicPredictor()

# Export functions
__all__ = ['DynamicPredictor', 'dynamic_predictor'] 