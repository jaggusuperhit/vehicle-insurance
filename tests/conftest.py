import os
import sys
import pytest
import pandas as pd
import numpy as np
from pathlib import Path

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@pytest.fixture(scope="session")
def sample_data():
    """Create a sample DataFrame for testing"""
    data = {
        'Gender': [1, 0, 1, 0, 1],
        'Age': [25, 30, 35, 40, 45],
        'Driving_License': [1, 1, 1, 1, 1],
        'Region_Code': [28.0, 28.0, 28.0, 28.0, 28.0],
        'Previously_Insured': [0, 1, 0, 1, 0],
        'Annual_Premium': [20000.0, 25000.0, 30000.0, 35000.0, 40000.0],
        'Policy_Sales_Channel': [152.0, 152.0, 152.0, 152.0, 152.0],
        'Vintage': [100, 200, 300, 400, 500],
        'Vehicle_Age_lt_1_Year': [1, 0, 0, 0, 0],
        'Vehicle_Age_gt_2_Years': [0, 0, 1, 1, 1],
        'Vehicle_Damage_Yes': [1, 0, 1, 0, 1],
        'Response': [1, 0, 1, 0, 1]
    }
    return pd.DataFrame(data)

@pytest.fixture(scope="session")
def create_test_dirs(tmp_path_factory):
    """Create test directories for artifacts"""
    base_dir = tmp_path_factory.mktemp("artifact")
    
    # Create subdirectories
    dirs = [
        "data_ingestion/feature_store",
        "data_ingestion/ingested_data",
        "data_validation/valid_data",
        "data_validation/invalid_data",
        "data_validation/drift_report",
        "data_transformation/transformed_data",
        "data_transformation/preprocessed",
        "model_trainer",
        "model_evaluation",
        "model_pusher",
        "production_model"
    ]
    
    for dir_path in dirs:
        path = base_dir / dir_path
        path.mkdir(parents=True, exist_ok=True)
    
    return base_dir

@pytest.fixture(scope="session")
def reports_dir():
    """Create directory for test reports"""
    path = Path("tests/reports")
    path.mkdir(parents=True, exist_ok=True)
    return path
