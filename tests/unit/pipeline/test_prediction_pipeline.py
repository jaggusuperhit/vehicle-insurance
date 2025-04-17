import os
import sys
import pytest
import pandas as pd
import numpy as np

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

# Import prediction pipeline
from src.pipeline.prediction_pipeline import VehicleData, VehicleDataClassifier

class TestPredictionPipeline:
    """Test class for prediction pipeline"""

    def test_vehicle_data_initialization(self):
        """Test VehicleData class initialization"""
        # Create a test instance
        vehicle_data = VehicleData(
            Gender=1,
            Age=35,
            Driving_License=1,
            Region_Code=28.0,
            Previously_Insured=0,
            Annual_Premium=30000.0,
            Policy_Sales_Channel=152.0,
            Vintage=100,
            Vehicle_Age_lt_1_Year=1,
            Vehicle_Age_gt_2_Years=0,
            Vehicle_Damage_Yes=1
        )

        # Verify attributes are set correctly
        assert vehicle_data.Gender == 1
        assert vehicle_data.Age == 35
        assert vehicle_data.Driving_License == 1
        assert vehicle_data.Region_Code == 28.0
        assert vehicle_data.Previously_Insured == 0
        assert vehicle_data.Annual_Premium == 30000.0
        assert vehicle_data.Policy_Sales_Channel == 152.0
        assert vehicle_data.Vintage == 100
        assert vehicle_data.Vehicle_Age_lt_1_Year == 1
        assert vehicle_data.Vehicle_Age_gt_2_Years == 0
        assert vehicle_data.Vehicle_Damage_Yes == 1

    def test_get_vehicle_input_data_frame(self):
        """Test get_vehicle_input_data_frame method"""
        # Create a test instance
        vehicle_data = VehicleData(
            Gender=1,
            Age=35,
            Driving_License=1,
            Region_Code=28.0,
            Previously_Insured=0,
            Annual_Premium=30000.0,
            Policy_Sales_Channel=152.0,
            Vintage=100,
            Vehicle_Age_lt_1_Year=1,
            Vehicle_Age_gt_2_Years=0,
            Vehicle_Damage_Yes=1
        )

        # Get DataFrame
        df = vehicle_data.get_vehicle_input_data_frame()

        # Verify DataFrame structure
        assert isinstance(df, pd.DataFrame)
        assert df.shape == (1, 12)  # 1 row, 12 columns (including id column)

        # Verify column names
        expected_columns = [
            'id', 'Gender', 'Age', 'Driving_License', 'Region_Code', 'Previously_Insured',
            'Annual_Premium', 'Policy_Sales_Channel', 'Vintage', 'Vehicle_Age_lt_1_Year',
            'Vehicle_Age_gt_2_Years', 'Vehicle_Damage_Yes'
        ]
        assert set(df.columns) == set(expected_columns)

        # Verify values
        assert df.iloc[0]['Gender'] == 1
        assert df.iloc[0]['Age'] == 35
        assert df.iloc[0]['Annual_Premium'] == 30000.0

    @pytest.mark.skipif(not os.path.exists(os.path.join("artifact", "production_model", "model.pkl")),
                       reason="Production model not available")
    def test_vehicle_data_classifier(self):
        """Test VehicleDataClassifier class (skip if model not available)"""
        # Create a test instance
        classifier = VehicleDataClassifier()

        # Create test data
        test_data = pd.DataFrame({
            'Gender': [1],
            'Age': [35],
            'Driving_License': [1],
            'Region_Code': [28.0],
            'Previously_Insured': [0],
            'Annual_Premium': [30000.0],
            'Policy_Sales_Channel': [152.0],
            'Vintage': [100],
            'Vehicle_Age_lt_1_Year': [1],
            'Vehicle_Age_gt_2_Years': [0],
            'Vehicle_Damage_Yes': [1]
        })

        # Make prediction
        prediction = classifier.predict(test_data)

        # Verify prediction structure
        assert isinstance(prediction, np.ndarray)
        assert prediction.shape == (1,)
        assert prediction[0] in [0, 1]  # Binary classification
