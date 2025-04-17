import os
import pickle
import logging
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from src.constants import ARTIFACT_DIR
from src.entity.estimator import MyModel

def ensure_production_model_exists():
    """
    Ensures that a production model exists for prediction.
    If no model is found, creates a dummy model.
    """
    # Define the path to the production model
    production_model_dir = os.path.join(ARTIFACT_DIR, "production_model")
    production_model_path = os.path.join(production_model_dir, "model.pkl")
    
    # Check if the production model directory exists
    if not os.path.exists(production_model_dir):
        logging.warning(f"Production model directory not found. Creating: {production_model_dir}")
        os.makedirs(production_model_dir, exist_ok=True)
    
    # Check if the production model file exists
    if not os.path.exists(production_model_path):
        logging.warning(f"Production model not found. Creating a dummy model at: {production_model_path}")
        
        # Create a simple preprocessing pipeline
        preprocessor = Pipeline([
            ('scaler', StandardScaler())
        ])
        
        # Create a simple model
        model = RandomForestClassifier(n_estimators=10, random_state=42)
        
        # Create a MyModel instance
        my_model = MyModel(preprocessing_object=preprocessor, trained_model_object=model)
        
        # Save the model
        with open(production_model_path, 'wb') as f:
            pickle.dump(my_model, f)
        
        logging.info(f"Dummy model created and saved at: {production_model_path}")
        return False
    
    logging.info(f"Production model found at: {production_model_path}")
    return True
