from src.exception import MyException
from src.entity.estimator import MyModel
from src.utils.main_utils import load_object
import sys
import os
from pandas import DataFrame
from src.logger import logging


class LocalInsuranceEstimator:
    """
    This class is used as a local alternative to the S3-based InsuranceEstimator
    It provides the same interface but works with local files instead of S3
    """

    def __init__(self, model_path):
        """
        :param model_path: Local path to the model file
        """
        self.model_path = model_path
        self.loaded_model: MyModel = None

    def is_model_present(self, model_path=None) -> bool:
        """
        Check if the model file exists locally
        """
        try:
            path_to_check = model_path if model_path else self.model_path
            return os.path.exists(path_to_check)
        except Exception as e:
            logging.error(f"Error checking if model exists: {str(e)}")
            return False

    def load_model(self) -> MyModel:
        """
        Load the model from the local path
        """
        try:
            if not self.is_model_present():
                logging.warning(f"Model not found at {self.model_path}")
                return None

            return load_object(self.model_path)
        except Exception as e:
            raise MyException(f"Error loading model from {self.model_path}: {str(e)}", sys)

    def predict(self, dataframe: DataFrame):
        """
        Make predictions using the loaded model
        """
        try:
            # Add an 'id' column if it doesn't exist
            if 'id' not in dataframe.columns:
                dataframe['id'] = 0  # Add a dummy id column
                logging.info("Added dummy 'id' column to dataframe for prediction")

            if self.loaded_model is None:
                self.loaded_model = self.load_model()
                if self.loaded_model is None:
                    logging.warning("No model available for prediction")
                    return None

            return self.loaded_model.predict(dataframe=dataframe)
        except Exception as e:
            raise MyException(f"Error during prediction: {str(e)}", sys)
