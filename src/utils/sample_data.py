import os
import pandas as pd
import logging
from pathlib import Path

def get_sample_data():
    """
    Provides sample data when MongoDB is not available.
    Returns a DataFrame with sample insurance data.
    """
    try:
        # Check if we're in testing environment
        is_testing = os.getenv("ENVIRONMENT", "").lower() == "testing"
        
        if is_testing:
            logging.info("Running in testing environment, using sample data")
        
        # Try to find sample data in the repository
        sample_paths = [
            "data/data.csv",
            "sample_data/insurance_data.csv",
            "tests/data/sample.csv"
        ]
        
        for path in sample_paths:
            if Path(path).exists():
                logging.info(f"Loading sample data from {path}")
                return pd.read_csv(path)
        
        # If no sample data file found, create synthetic data
        logging.warning("No sample data file found, creating synthetic data")
        
        # Create synthetic data with the same schema as the real data
        data = {
            'id': list(range(1, 101)),
            'Gender': ['Male', 'Female'] * 50,
            'Age': [25 + i % 40 for i in range(100)],
            'Driving_License': [1] * 100,
            'Region_Code': [28.0, 3.0, 8.0, 36.0, 41.0] * 20,
            'Previously_Insured': [0, 1] * 50,
            'Vehicle_Age': ['< 1 Year', '1-2 Year', '> 2 Years'] * 34,
            'Vehicle_Damage': ['Yes', 'No'] * 50,
            'Annual_Premium': [10000 + i * 100 for i in range(100)],
            'Policy_Sales_Channel': [1, 2, 3, 4, 6, 7, 9, 12, 13, 14] * 10,
            'Vintage': [100 + i * 5 for i in range(100)],
            'Response': [0, 1] * 50
        }
        
        return pd.DataFrame(data)
    
    except Exception as e:
        logging.error(f"Error creating sample data: {str(e)}")
        # Return minimal dataset that won't break the application
        return pd.DataFrame({
            'id': list(range(1, 11)),
            'Gender': ['Male', 'Female'] * 5,
            'Age': [30] * 10,
            'Driving_License': [1] * 10,
            'Region_Code': [28.0] * 10,
            'Previously_Insured': [0] * 10,
            'Vehicle_Age': ['< 1 Year'] * 10,
            'Vehicle_Damage': ['Yes'] * 10,
            'Annual_Premium': [10000] * 10,
            'Policy_Sales_Channel': [1] * 10,
            'Vintage': [100] * 10,
            'Response': [0, 1] * 5
        })
