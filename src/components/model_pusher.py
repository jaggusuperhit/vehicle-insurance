import sys
import os

from src.cloud_storage.aws_storage import SimpleStorageService
from src.exception import MyException
from src.logger import logging
from src.entity.artifact_entity import ModelPusherArtifact, ModelEvaluationArtifact
from src.entity.config_entity import ModelPusherConfig
from src.entity.s3_estimator import InsuranceEstimator
from src.entity.local_pusher import LocalModelPusher


class ModelPusher:
    def __init__(self, model_evaluation_artifact: ModelEvaluationArtifact,
                 model_pusher_config: ModelPusherConfig):
        """
        :param model_evaluation_artifact: Output reference of data evaluation artifact stage
        :param model_pusher_config: Configuration for model pusher
        """
        self.model_evaluation_artifact = model_evaluation_artifact
        self.model_pusher_config = model_pusher_config

        # Set up local production model path
        artifact_dir = os.path.dirname(os.path.dirname(model_evaluation_artifact.trained_model_path))
        self.production_model_dir = os.path.join(artifact_dir, "production_model")
        self.production_model_path = os.path.join(self.production_model_dir, "model.pkl")

        # Try to set up S3 connection, fall back to local if not available
        try:
            self.s3 = SimpleStorageService()
            self.insurance_estimator = InsuranceEstimator(
                bucket_name=model_pusher_config.bucket_name,
                model_path=model_pusher_config.s3_model_key_path
            )
            self.use_s3 = True
            logging.info("Using S3 for model pushing")
        except Exception as e:
            logging.warning(f"S3 connection failed: {str(e)}. Will use local storage instead.")
            self.local_pusher = LocalModelPusher(
                model_path=model_evaluation_artifact.trained_model_path,
                production_model_path=self.production_model_path
            )
            self.use_s3 = False
            logging.info("Using local storage for model pushing")

    def initiate_model_pusher(self) -> ModelPusherArtifact:
        """
        Method Name :   initiate_model_pusher
        Description :   This function is used to initiate all steps of the model pusher

        Output      :   Returns model pusher artifact
        On Failure  :   Logs the error and returns a default artifact
        """
        logging.info("Entered initiate_model_pusher method of ModelPusher class")

        try:
            print("------------------------------------------------------------------------------------------------")

            if self.use_s3:
                # Push model to S3
                logging.info("Uploading new model to S3 bucket...")
                self.insurance_estimator.save_model(from_file=self.model_evaluation_artifact.trained_model_path)
                logging.info("Uploaded model to S3 bucket")

                model_pusher_artifact = ModelPusherArtifact(
                    bucket_name=self.model_pusher_config.bucket_name,
                    s3_model_path=self.model_pusher_config.s3_model_key_path
                )
            else:
                # Push model to local production directory
                logging.info("Saving model to local production directory...")
                self.local_pusher.save_model(from_file=self.model_evaluation_artifact.trained_model_path)
                logging.info(f"Saved model to local production directory: {self.production_model_path}")

                # Create a model pusher artifact with local path information
                model_pusher_artifact = ModelPusherArtifact(
                    bucket_name="local",
                    s3_model_path=self.production_model_path
                )

            logging.info(f"Model pusher artifact: [{model_pusher_artifact}]")
            logging.info("Exited initiate_model_pusher method of ModelPusher class")

            return model_pusher_artifact

        except Exception as e:
            logging.error(f"Error in model pusher: {str(e)}")
            # Return a default artifact
            return ModelPusherArtifact(
                bucket_name="local",
                s3_model_path=self.production_model_path if hasattr(self, 'production_model_path') else "model.pkl"
            )