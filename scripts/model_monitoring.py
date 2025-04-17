"""
Model monitoring script for the Vehicle Insurance Prediction application.
This script monitors model performance and drift over time.
"""

import os
import sys
import pandas as pd
import numpy as np
import json
import logging
import time
from datetime import datetime
import requests
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import boto3
import pickle

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import project modules
from src.constants import ARTIFACT_DIR, MODEL_FILE_NAME
from src.entity.config_entity import ModelEvaluationConfig
from src.utils.main_utils import read_yaml_file

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/model_monitoring.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ModelMonitor:
    """Class for monitoring model performance and drift."""
    
    def __init__(self):
        """Initialize the model monitor."""
        self.model_path = os.path.join(ARTIFACT_DIR, "production_model", MODEL_FILE_NAME)
        self.config = ModelEvaluationConfig()
        self.s3_client = boto3.client('s3')
        self.metrics_history_file = "model_metrics_history.json"
        
        # Load model metrics history if it exists
        self.metrics_history = self._load_metrics_history()
        
    def _load_metrics_history(self):
        """Load model metrics history from file."""
        try:
            if os.path.exists(self.metrics_history_file):
                with open(self.metrics_history_file, 'r') as f:
                    return json.load(f)
            return []
        except Exception as e:
            logger.error(f"Error loading metrics history: {e}")
            return []
    
    def _save_metrics_history(self):
        """Save model metrics history to file."""
        try:
            with open(self.metrics_history_file, 'w') as f:
                json.dump(self.metrics_history, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving metrics history: {e}")
    
    def load_model(self):
        """Load the production model."""
        try:
            logger.info(f"Loading model from {self.model_path}")
            with open(self.model_path, 'rb') as f:
                return pickle.load(f)
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            return None
    
    def load_test_data(self):
        """Load test data for model evaluation."""
        try:
            # This is a placeholder - in a real application, you would load your test data
            # from a database or file
            test_data_path = os.path.join("data", "test_data.csv")
            if os.path.exists(test_data_path):
                return pd.read_csv(test_data_path)
            else:
                logger.warning(f"Test data file not found: {test_data_path}")
                return None
        except Exception as e:
            logger.error(f"Error loading test data: {e}")
            return None
    
    def evaluate_model(self, model, test_data):
        """Evaluate model performance on test data."""
        try:
            if model is None or test_data is None:
                logger.error("Model or test data is None, cannot evaluate")
                return None
            
            # Split features and target
            X = test_data.drop('Response', axis=1)
            y = test_data['Response']
            
            # Make predictions
            y_pred = model.predict(X)
            
            # Calculate metrics
            metrics = {
                'timestamp': datetime.now().isoformat(),
                'accuracy': accuracy_score(y, y_pred),
                'precision': precision_score(y, y_pred),
                'recall': recall_score(y, y_pred),
                'f1': f1_score(y, y_pred)
            }
            
            logger.info(f"Model evaluation metrics: {metrics}")
            return metrics
        except Exception as e:
            logger.error(f"Error evaluating model: {e}")
            return None
    
    def detect_drift(self, current_metrics):
        """Detect if there's significant drift in model performance."""
        try:
            if not self.metrics_history or current_metrics is None:
                logger.info("Not enough history to detect drift")
                return False
            
            # Get the last recorded metrics
            last_metrics = self.metrics_history[-1]
            
            # Calculate drift for each metric
            drift = {
                'accuracy': abs(current_metrics['accuracy'] - last_metrics['accuracy']),
                'precision': abs(current_metrics['precision'] - last_metrics['precision']),
                'recall': abs(current_metrics['recall'] - last_metrics['recall']),
                'f1': abs(current_metrics['f1'] - last_metrics['f1'])
            }
            
            # Check if any metric has drifted beyond threshold
            threshold = self.config.changed_threshold_score
            significant_drift = any(value > threshold for value in drift.values())
            
            if significant_drift:
                logger.warning(f"Significant model drift detected: {drift}")
            else:
                logger.info(f"No significant model drift detected: {drift}")
            
            return significant_drift
        except Exception as e:
            logger.error(f"Error detecting drift: {e}")
            return False
    
    def trigger_retraining(self):
        """Trigger model retraining if significant drift is detected."""
        try:
            logger.info("Triggering model retraining...")
            
            # Call the training endpoint
            response = requests.get("http://localhost:5050/train")
            
            if response.status_code == 200:
                logger.info("Model retraining triggered successfully")
                return True
            else:
                logger.error(f"Failed to trigger retraining: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Error triggering retraining: {e}")
            return False
    
    def run_monitoring(self):
        """Run the model monitoring process."""
        try:
            logger.info("Starting model monitoring")
            
            # Load model and test data
            model = self.load_model()
            test_data = self.load_test_data()
            
            if model is None or test_data is None:
                logger.error("Cannot run monitoring without model and test data")
                return
            
            # Evaluate model
            current_metrics = self.evaluate_model(model, test_data)
            
            if current_metrics:
                # Add to history
                self.metrics_history.append(current_metrics)
                self._save_metrics_history()
                
                # Check for drift
                if self.detect_drift(current_metrics):
                    # Trigger retraining if drift detected
                    self.trigger_retraining()
            
            logger.info("Model monitoring completed")
        except Exception as e:
            logger.error(f"Error in model monitoring: {e}")

def main():
    """Main function to run model monitoring."""
    monitor = ModelMonitor()
    monitor.run_monitoring()

if __name__ == "__main__":
    main()
