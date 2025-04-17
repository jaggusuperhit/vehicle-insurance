import os
import sys
import pytest

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

# Import entity classes
from src.entity.config_entity import (
    TrainingPipelineConfig,
    DataIngestionConfig,
    DataValidationConfig,
    DataTransformationConfig,
    ModelTrainerConfig,
    ModelEvaluationConfig,
    ModelPusherConfig
)

class TestConfigEntity:
    """Test class for configuration entity classes"""

    def test_training_pipeline_config(self):
        """Test TrainingPipelineConfig initialization"""
        config = TrainingPipelineConfig()

        # Verify artifact_dir is set correctly
        assert isinstance(config.artifact_dir, str)
        assert len(config.artifact_dir) > 0
        assert "artifact" in config.artifact_dir

    def test_data_ingestion_config(self):
        """Test DataIngestionConfig initialization"""
        config = DataIngestionConfig()

        # Verify attributes are set correctly
        assert isinstance(config.data_ingestion_dir, str)
        assert isinstance(config.feature_store_file_path, str)
        assert isinstance(config.training_file_path, str)
        assert isinstance(config.testing_file_path, str)
        assert isinstance(config.train_test_split_ratio, float)
        assert isinstance(config.collection_name, str)

        # Verify paths are correctly formed
        assert "artifact" in config.data_ingestion_dir
        assert "data_ingestion" in config.data_ingestion_dir
        assert config.feature_store_file_path.endswith(".csv")
        assert config.training_file_path.endswith(".csv")
        assert config.testing_file_path.endswith(".csv")

        # Verify ratio is in valid range
        assert 0 < config.train_test_split_ratio < 1

    def test_data_validation_config(self):
        """Test DataValidationConfig initialization"""
        config = DataValidationConfig()

        # Verify attributes are set correctly
        assert isinstance(config.data_validation_dir, str)
        assert isinstance(config.validation_report_file_path, str)

        # Verify paths are correctly formed
        assert "artifact" in config.data_validation_dir
        assert "data_validation" in config.data_validation_dir

    def test_data_transformation_config(self):
        """Test DataTransformationConfig initialization"""
        config = DataTransformationConfig()

        # Verify attributes are set correctly
        assert isinstance(config.data_transformation_dir, str)
        assert isinstance(config.transformed_train_file_path, str)
        assert isinstance(config.transformed_test_file_path, str)
        assert isinstance(config.transformed_object_file_path, str)

        # Verify paths are correctly formed
        assert "artifact" in config.data_transformation_dir
        assert "data_transformation" in config.data_transformation_dir
        assert config.transformed_train_file_path.endswith(".npy")
        assert config.transformed_test_file_path.endswith(".npy")
        assert config.transformed_object_file_path.endswith(".pkl")

    def test_model_trainer_config(self):
        """Test ModelTrainerConfig initialization"""
        config = ModelTrainerConfig()

        # Verify attributes are set correctly
        assert isinstance(config.model_trainer_dir, str)
        assert isinstance(config.trained_model_file_path, str)
        assert isinstance(config.expected_accuracy, float)
        assert isinstance(config.model_config_file_path, str)

        # Verify paths are correctly formed
        assert "artifact" in config.model_trainer_dir
        assert "model_trainer" in config.model_trainer_dir
        assert config.trained_model_file_path.endswith(".pkl")

        # Verify thresholds are in valid ranges
        assert 0 <= config.expected_accuracy <= 1

    def test_model_evaluation_config(self):
        """Test ModelEvaluationConfig initialization"""
        config = ModelEvaluationConfig()

        # Verify attributes are set correctly
        assert isinstance(config.changed_threshold_score, float)
        assert isinstance(config.bucket_name, str)
        assert isinstance(config.s3_model_key_path, str)

        # Verify threshold is in valid range
        assert 0 <= config.changed_threshold_score <= 1

    def test_model_pusher_config(self):
        """Test ModelPusherConfig initialization"""
        config = ModelPusherConfig()

        # Verify attributes are set correctly
        assert isinstance(config.bucket_name, str)
        assert isinstance(config.s3_model_key_path, str)
