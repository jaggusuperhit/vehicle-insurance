# Apply patch for scikit-learn deprecation warnings
from src.utils.sklearn_patch import apply_sklearn_patches

# Apply the patch before importing any scikit-learn or imbalanced-learn modules
apply_sklearn_patches()

# --------------------------------------------------------------------------------
# Below code is commented out as it was used for testing logging and exception handling
# --------------------------------------------------------------------------------
# from src.logger import logging
# logging.debug("This is a debug message.")
# logging.info("This is an info message.")
# logging.warning("This is a warning message.")
# logging.error("This is an error message.")
# logging.critical("This is a critical message.")

# from src.exception import MyException
# import sys
# try:
#     a = 1 + "Z"
# except Exception as e:
#     logging.info(e)
#     raise MyException(e, sys) from e
# --------------------------------------------------------------------------------

from src.pipeline.training_pipeline import TrainPipeline

pipline = TrainPipeline()
pipline.run_pipeline()
