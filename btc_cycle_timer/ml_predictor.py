# ml_predictor.py

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import json
from pathlib import Path
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error
import joblib
from btc_cycle_timer.logger import logger
from btc_cycle_timer.chart import load_price_data
from btc_cycle_timer.config import get_current_cycle_phase

class MLPredictor:
    """Machine Learning predictor for BTC cycle analysis"""
    
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.feature_columns = []
        self.predictions_history = []
        self.model_path = Path(__file__).parent / "models"
        self.model_path.mkdir(exist_ok=True)
        logger.info("ML Predictor initialized")
    
    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prepare features for ML model"""
        logger.info("Preparing features for ML model")
        
        # Convert date to datetime
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        
        # Basic price features
        df['price_change'] = df['close'].pct_change()
        df['price_change_7d'] = df['close'].pct_change(7)
        df['price_change_30d'] = df['close'].pct_change(30)
        df['price_change_90d'] = df['close'].pct_change(90)
        
        # Moving averages
        df['ma_7'] = df['close'].rolling(7).mean()
        df['ma_30'] = df['close'].rolling(30).mean()
        df['ma_90'] = df['close'].rolling(90).mean()
        df['ma_200'] = df['close'].rolling(200).mean()
        
        # Price ratios
        df['price_ma7_ratio'] = df['close'] / df['ma_7']
        df['price_ma30_ratio'] = df['close'] / df['ma_30']
        df['price_ma90_ratio'] = df['close'] / df['ma_90']
        df['price_ma200_ratio'] = df['close'] / df['ma_200']
        
        # Volatility features
        df['volatility_7d'] = df['price_change'].rolling(7).std()
        df['volatility_30d'] = df['price_change'].rolling(30).std()
        
        # Cycle phase features (simplified)
        df['days_since_2022_bottom'] = (df['date'] - pd.to_datetime('2022-11-22')).dt.days
        
        # Halving cycle features
        halving_dates = ['2012-11-28', '2016-07-09', '2020-05-11', '2024-04-20']
        for i, halving_date in enumerate(halving_dates):
            df[f'days_since_halving_{i}'] = (df['date'] - pd.to_datetime(halving_date)).dt.days
        
        # Target: price in 30 days
        df['target_30d'] = df['close'].shift(-30)
        
        # Remove NaN values
        df = df.dropna()
        
        # Select feature columns
        self.feature_columns = [
            'price_change', 'price_change_7d', 'price_change_30d', 'price_change_90d',
            'ma_7', 'ma_30', 'ma_90', 'ma_200',
            'price_ma7_ratio', 'price_ma30_ratio', 'price_ma90_ratio', 'price_ma200_ratio',
            'volatility_7d', 'volatility_30d',
            'days_since_2022_bottom'
        ] + [f'days_since_halving_{i}' for i in range(len(halving_dates))]
        
        logger.info(f"Prepared {len(self.feature_columns)} features")
        return df
    
    def train_model(self, df: pd.DataFrame) -> Dict:
        """Train the ML model"""
        logger.info("Training ML model")
        
        # Prepare features
        df = self.prepare_features(df)
        
        # Split data
        train_size = int(len(df) * 0.8)
        train_df = df[:train_size]
        test_df = df[train_size:]
        
        # Prepare training data
        X_train = train_df[self.feature_columns]
        y_train = train_df['target_30d']
        
        X_test = test_df[self.feature_columns]
        y_test = test_df['target_30d']
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train model
        self.model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        
        self.model.fit(X_train_scaled, y_train)
        
        # Make predictions
        y_pred_train = self.model.predict(X_train_scaled)
        y_pred_test = self.model.predict(X_test_scaled)
        
        # Calculate metrics
        metrics = {
            'train_mae': mean_absolute_error(y_train, y_pred_train),
            'test_mae': mean_absolute_error(y_test, y_pred_test),
            'train_rmse': np.sqrt(mean_squared_error(y_train, y_pred_train)),
            'test_rmse': np.sqrt(mean_squared_error(y_test, y_pred_test)),
            'train_r2': self.model.score(X_train_scaled, y_train),
            'test_r2': self.model.score(X_test_scaled, y_test),
            'feature_importance': dict(zip(self.feature_columns, self.model.feature_importances_))
        }
        
        logger.info(f"Model trained successfully. Test R²: {metrics['test_r2']:.3f}")
        
        # Save model
        self.save_model()
        
        return metrics
    
    def predict_price(self, days_ahead: int = 30) -> Dict:
        """Predict BTC price for given days ahead"""
        if self.model is None:
            logger.error("Model not trained. Please train the model first.")
            return None
        
        try:
            # Load latest data
            df = load_price_data()
            df = self.prepare_features(df)
            
            # Get latest features
            latest_features = df[self.feature_columns].iloc[-1:]
            latest_features_scaled = self.scaler.transform(latest_features)
            
            # Make prediction
            prediction = self.model.predict(latest_features_scaled)[0]
            current_price = df['close'].iloc[-1]
            
            # Calculate confidence interval (simplified)
            confidence = 0.95
            prediction_std = np.std(df['target_30d'] - df['close']) * 0.1  # Simplified
            
            result = {
                'current_price': current_price,
                'predicted_price': prediction,
                'predicted_change': ((prediction - current_price) / current_price) * 100,
                'confidence_interval': [
                    prediction - 1.96 * prediction_std,
                    prediction + 1.96 * prediction_std
                ],
                'prediction_date': datetime.now().isoformat(),
                'target_date': (datetime.now() + timedelta(days=days_ahead)).isoformat(),
                'model_confidence': confidence
            }
            
            # Save prediction to history
            self.predictions_history.append(result)
            self.save_predictions_history()
            
            logger.info(f"Price prediction: ${prediction:,.2f} ({result['predicted_change']:+.2f}%)")
            
            return result
            
        except Exception as e:
            logger.error(f"Error making prediction: {e}")
            return None
    
    def evaluate_predictions(self) -> Dict:
        """Evaluate accuracy of past predictions"""
        logger.info("Evaluating past predictions")
        
        if not self.predictions_history:
            return {"error": "No predictions to evaluate"}
        
        # Load actual prices
        df = load_price_data()
        df['date'] = pd.to_datetime(df['date'])
        
        evaluations = []
        
        for pred in self.predictions_history:
            try:
                pred_date = datetime.fromisoformat(pred['prediction_date'])
                target_date = datetime.fromisoformat(pred['target_date'])
                
                # Find actual price at target date
                actual_data = df[df['date'] >= target_date].iloc[0] if len(df[df['date'] >= target_date]) > 0 else None
                
                if actual_data is not None:
                    actual_price = actual_data['close']
                    predicted_price = pred['predicted_price']
                    
                    error = abs(actual_price - predicted_price)
                    error_percent = (error / actual_price) * 100
                    
                    evaluation = {
                        'prediction_date': pred_date.isoformat(),
                        'target_date': target_date.isoformat(),
                        'predicted_price': predicted_price,
                        'actual_price': actual_price,
                        'error': error,
                        'error_percent': error_percent,
                        'accuracy': max(0, 100 - error_percent)
                    }
                    
                    evaluations.append(evaluation)
                    
            except Exception as e:
                logger.error(f"Error evaluating prediction: {e}")
        
        if not evaluations:
            return {"error": "No valid evaluations"}
        
        # Calculate overall metrics
        avg_error = np.mean([e['error'] for e in evaluations])
        avg_error_percent = np.mean([e['error_percent'] for e in evaluations])
        avg_accuracy = np.mean([e['accuracy'] for e in evaluations])
        
        result = {
            'total_predictions': len(evaluations),
            'average_error': avg_error,
            'average_error_percent': avg_error_percent,
            'average_accuracy': avg_accuracy,
            'evaluations': evaluations
        }
        
        logger.info(f"Prediction evaluation: {avg_accuracy:.1f}% accuracy")
        
        return result
    
    def get_feature_importance(self) -> Dict:
        """Get feature importance from the model"""
        if self.model is None:
            return {"error": "Model not trained"}
        
        importance = dict(zip(self.feature_columns, self.model.feature_importances_))
        return dict(sorted(importance.items(), key=lambda x: x[1], reverse=True))
    
    def save_model(self):
        """Save the trained model"""
        try:
            model_file = self.model_path / "btc_predictor.joblib"
            scaler_file = self.model_path / "btc_scaler.joblib"
            
            joblib.dump(self.model, model_file)
            joblib.dump(self.scaler, scaler_file)
            
            logger.info("Model saved successfully")
            
        except Exception as e:
            logger.error(f"Error saving model: {e}")
    
    def load_model(self):
        """Load the trained model"""
        try:
            model_file = self.model_path / "btc_predictor.joblib"
            scaler_file = self.model_path / "btc_scaler.joblib"
            
            if model_file.exists() and scaler_file.exists():
                self.model = joblib.load(model_file)
                self.scaler = joblib.load(scaler_file)
                logger.info("Model loaded successfully")
                return True
            else:
                logger.warning("No saved model found")
                return False
                
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            return False
    
    def save_predictions_history(self):
        """Save predictions history to file"""
        try:
            history_file = self.model_path / "predictions_history.json"
            with open(history_file, 'w') as f:
                json.dump(self.predictions_history, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving predictions history: {e}")
    
    def load_predictions_history(self):
        """Load predictions history from file"""
        try:
            history_file = self.model_path / "predictions_history.json"
            if history_file.exists():
                with open(history_file, 'r') as f:
                    self.predictions_history = json.load(f)
        except Exception as e:
            logger.error(f"Error loading predictions history: {e}")
    
    def generate_ml_report(self) -> str:
        """Generate comprehensive ML report"""
        logger.info("Generating ML report")
        
        # Load history if not loaded
        if not self.predictions_history:
            self.load_predictions_history()
        
        # Get current prediction
        current_prediction = self.predict_price()
        
        # Get evaluation
        evaluation = self.evaluate_predictions()
        
        # Get feature importance
        feature_importance = self.get_feature_importance()
        
        # Create report
        report = f"""
🤖 *ML Prediction Report*

📊 *Current Prediction (30 days):*
• Current Price: ${current_prediction['current_price']:,.2f}
• Predicted Price: ${current_prediction['predicted_price']:,.2f}
• Expected Change: {current_prediction['predicted_change']:+.2f}%
• Confidence: {current_prediction['model_confidence']*100:.0f}%

📈 *Prediction Accuracy:*
• Total Predictions: {evaluation.get('total_predictions', 'N/A')}
• Average Accuracy: {evaluation.get('average_accuracy', 'N/A'):.1f}%
• Average Error: {evaluation.get('average_error_percent', 'N/A'):.1f}%

🔍 *Top Features:*
"""
        
        # Add top 5 features
        if isinstance(feature_importance, dict) and 'error' not in feature_importance:
            top_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)[:5]
            for feature, importance in top_features:
                report += f"• {feature}: {importance:.3f}\n"
        
        report += f"\n🕐 {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        return report

# Create global instance
ml_predictor = MLPredictor()

# Export functions
__all__ = ['MLPredictor', 'ml_predictor'] 