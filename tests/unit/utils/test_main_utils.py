import os
import sys
import pytest
import pandas as pd
import numpy as np
import json
from pathlib import Path

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

# Import utility functions
from src.utils.main_utils import read_yaml_file, write_yaml_file, save_numpy_array_data, load_numpy_array_data
from src.utils.main_utils import save_object, load_object

class TestMainUtils:
    """Test class for main utility functions"""

    def test_yaml_operations(self, tmp_path):
        """Test YAML read/write operations"""
        # Create a temporary YAML file
        test_data = {"test": "value", "nested": {"key": "value"}}
        test_file = tmp_path / "test.yaml"

        # Write test data to YAML file
        write_yaml_file(file_path=str(test_file), content=test_data)

        # Read data from YAML file
        read_data = read_yaml_file(file_path=str(test_file))

        # Verify data matches
        assert read_data == test_data

    def test_numpy_array_operations(self, tmp_path):
        """Test NumPy array save/load operations"""
        # Create a test NumPy array
        test_array = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        test_file = tmp_path / "test_array.npy"

        # Save array to file
        save_numpy_array_data(file_path=str(test_file), array=test_array)

        # Load array from file
        loaded_array = load_numpy_array_data(file_path=str(test_file))

        # Verify arrays are equal
        assert np.array_equal(test_array, loaded_array)

    def test_object_operations(self, tmp_path):
        """Test object save/load operations"""
        # Create a test object (using a simple dictionary)
        test_object = {"name": "test_model", "params": {"param1": 1, "param2": 2}}
        test_file = tmp_path / "test_object.pkl"

        # Save object to file
        save_object(file_path=str(test_file), obj=test_object)

        # Load object from file
        loaded_object = load_object(file_path=str(test_file))

        # Verify objects are equal
        assert test_object == loaded_object

    def test_json_operations(self, tmp_path):
        """Test JSON read/write operations"""
        # Create a test JSON object
        test_data = {"name": "test", "values": [1, 2, 3], "nested": {"key": "value"}}
        test_file = tmp_path / "test.json"

        # Write test data to JSON file
        with open(str(test_file), 'w') as f:
            json.dump(test_data, f)

        # Read data from JSON file
        with open(str(test_file), 'r') as f:
            read_data = json.load(f)

        # Verify data matches
        assert read_data == test_data
