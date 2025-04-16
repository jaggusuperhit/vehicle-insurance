import os
import shutil
from src.exception import MyException
from src.logger import logging
import sys


class LocalModelPusher:
    """
    This class is used as a local alternative to the S3-based model pusher
    It provides the same interface but works with local files instead of S3
    """

    def __init__(self, model_path=None, production_model_path=None):
        """
        :param model_path: Path to the model file to be pushed
        :param production_model_path: Path where the production model will be stored
        """
        self.model_path = model_path
        self.production_model_path = production_model_path

    def save_model(self, from_file, remove=False):
        """
        Save the model to the production model path
        :param from_file: Path to the source model file
        :param remove: Whether to remove the source file after copying
        """
        try:
            if not os.path.exists(from_file):
                logging.error(f"Source model file {from_file} does not exist")
                return False
                
            # Create the directory if it doesn't exist
            os.makedirs(os.path.dirname(self.production_model_path), exist_ok=True)
            
            # Copy the model file
            shutil.copy2(from_file, self.production_model_path)
            logging.info(f"Model copied from {from_file} to {self.production_model_path}")
            
            # Remove the source file if requested
            if remove and os.path.exists(from_file):
                os.remove(from_file)
                logging.info(f"Removed source file {from_file}")
                
            return True
        except Exception as e:
            logging.error(f"Error saving model: {str(e)}")
            raise MyException(f"Error saving model: {str(e)}", sys)
