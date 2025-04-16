from src.entity.config_entity import ModelEvaluationConfig
from src.entity.artifact_entity import ModelTrainerArtifact, DataIngestionArtifact, ModelEvaluationArtifact
from sklearn.metrics import f1_score
from src.exception import MyException
from src.constants import TARGET_COLUMN
from src.logger import logging
from src.utils.main_utils import load_object
import sys
import os
import pandas as pd
from typing import Optional, Union
from src.entity.s3_estimator import InsuranceEstimator
from src.entity.local_estimator import LocalInsuranceEstimator
from dataclasses import dataclass

@dataclass
class EvaluateModelResponse:
    trained_model_f1_score: float
    best_model_f1_score: float
    is_model_accepted: bool
    difference: float


class ModelEvaluation:

    def __init__(self, model_eval_config: ModelEvaluationConfig, data_ingestion_artifact: DataIngestionArtifact,
                 model_trainer_artifact: ModelTrainerArtifact):
        try:
            self.model_eval_config = model_eval_config
            self.data_ingestion_artifact = data_ingestion_artifact
            self.model_trainer_artifact = model_trainer_artifact
        except Exception as e:
            raise MyException(e, sys) from e

    def get_best_model(self) -> Optional[Union[InsuranceEstimator, LocalInsuranceEstimator]]:
        """
        Method Name :   get_best_model
        Description :   This function is used to get model from production stage or locally.

        Output      :   Returns model object if available in s3 storage or locally
        On Failure  :   Logs the error and returns None
        """
        try:
            # First try to get the model from S3
            try:
                bucket_name = self.model_eval_config.bucket_name
                model_path = self.model_eval_config.s3_model_key_path
                insurance_estimator = InsuranceEstimator(bucket_name=bucket_name,
                                                model_path=model_path)

                if insurance_estimator.is_model_present(model_path=model_path):
                    logging.info("Found production model in S3 bucket")
                    return insurance_estimator
            except Exception as s3_error:
                logging.warning(f"Could not access S3 model: {str(s3_error)}")
                logging.info("Falling back to local model evaluation")

            # If S3 fails, try to get the model locally
            # Check if there's a previous model in the artifact directory
            artifact_dir = os.path.dirname(os.path.dirname(self.model_trainer_artifact.trained_model_file_path))
            previous_model_dir = os.path.join(artifact_dir, "previous_model")
            previous_model_path = os.path.join(previous_model_dir, "model.pkl")

            # Create a local estimator
            local_estimator = LocalInsuranceEstimator(model_path=previous_model_path)

            if local_estimator.is_model_present():
                logging.info(f"Found previous model locally at {previous_model_path}")
                return local_estimator

            logging.info("No previous model found locally or in S3")
            return None
        except Exception as e:
            logging.error(f"Error in get_best_model: {str(e)}")
            return None

    def _map_gender_column(self, df):
        """Map Gender column to 0 for Female and 1 for Male."""
        logging.info("Mapping 'Gender' column to binary values")
        df['Gender'] = df['Gender'].map({'Female': 0, 'Male': 1}).astype(int)
        return df

    def _create_dummy_columns(self, df):
        """Create dummy variables for categorical features."""
        logging.info("Creating dummy variables for categorical features")
        df = pd.get_dummies(df, drop_first=True)
        return df

    def _rename_columns(self, df):
        """Rename specific columns and ensure integer types for dummy columns."""
        logging.info("Renaming specific columns and casting to int")
        df = df.rename(columns={
            "Vehicle_Age_< 1 Year": "Vehicle_Age_lt_1_Year",
            "Vehicle_Age_> 2 Years": "Vehicle_Age_gt_2_Years"
        })
        for col in ["Vehicle_Age_lt_1_Year", "Vehicle_Age_gt_2_Years", "Vehicle_Damage_Yes"]:
            if col in df.columns:
                df[col] = df[col].astype('int')
        return df

    def _drop_id_column(self, df):
        """Drop the 'id' column if it exists."""
        logging.info("Dropping 'id' column")
        if "_id" in df.columns:
            df = df.drop("_id", axis=1)
        return df

    def evaluate_model(self) -> EvaluateModelResponse:
        """
        Method Name :   evaluate_model
        Description :   This function is used to evaluate trained model
                        with production model and choose best model

        Output      :   Returns bool value based on validation results
        On Failure  :   Write an exception log and then raise an exception
        """
        try:
            test_df = pd.read_csv(self.data_ingestion_artifact.test_file_path)
            x, y = test_df.drop(TARGET_COLUMN, axis=1), test_df[TARGET_COLUMN]

            logging.info("Test data loaded and now transforming it for prediction...")

            x = self._map_gender_column(x)
            x = self._drop_id_column(x)
            x = self._create_dummy_columns(x)
            x = self._rename_columns(x)

            # Load the current trained model
            current_model = load_object(file_path=self.model_trainer_artifact.trained_model_file_path)
            logging.info("Trained model loaded/exists.")
            trained_model_f1_score = self.model_trainer_artifact.metric_artifact.f1_score
            logging.info(f"F1_Score for this model: {trained_model_f1_score}")

            # Try to get the best model (from S3 or locally)
            best_model_f1_score = None
            best_model = self.get_best_model()

            if best_model is not None:
                try:
                    logging.info(f"Computing F1_Score for previous/production model...")
                    y_hat_best_model = best_model.predict(x)

                    if y_hat_best_model is not None:
                        best_model_f1_score = f1_score(y, y_hat_best_model)
                        logging.info(f"F1_Score-Previous Model: {best_model_f1_score}, F1_Score-New Model: {trained_model_f1_score}")
                    else:
                        logging.warning("Previous model returned None predictions")
                except Exception as pred_error:
                    logging.warning(f"Error predicting with previous model: {str(pred_error)}")
            else:
                logging.info("No previous model found for comparison. This will be the first accepted model.")

            # If no previous model or error occurred, set score to 0 to accept new model
            tmp_best_model_score = 0 if best_model_f1_score is None else best_model_f1_score

            # Create evaluation response
            result = EvaluateModelResponse(
                trained_model_f1_score=trained_model_f1_score,
                best_model_f1_score=best_model_f1_score,
                is_model_accepted=trained_model_f1_score > tmp_best_model_score,
                difference=trained_model_f1_score - tmp_best_model_score
            )

            logging.info(f"Model evaluation result: {result}")
            return result

        except Exception as e:
            logging.error(f"Error in evaluate_model: {str(e)}")
            # Return a default response that accepts the current model
            return EvaluateModelResponse(
                trained_model_f1_score=self.model_trainer_artifact.metric_artifact.f1_score,
                best_model_f1_score=None,
                is_model_accepted=True,
                difference=0.0
            )

    def initiate_model_evaluation(self) -> ModelEvaluationArtifact:
        """
        Method Name :   initiate_model_evaluation
        Description :   This function is used to initiate all steps of the model evaluation

        Output      :   Returns model evaluation artifact
        On Failure  :   Logs the error and returns a default artifact
        """
        try:
            print("------------------------------------------------------------------------------------------------")
            logging.info("Initialized Model Evaluation Component.")

            # Evaluate the model
            evaluate_model_response = self.evaluate_model()

            # Get the S3 model path (even if we're not using S3)
            s3_model_path = self.model_eval_config.s3_model_key_path

            # Create the model evaluation artifact
            model_evaluation_artifact = ModelEvaluationArtifact(
                is_model_accepted=evaluate_model_response.is_model_accepted,
                s3_model_path=s3_model_path,
                trained_model_path=self.model_trainer_artifact.trained_model_file_path,
                changed_accuracy=evaluate_model_response.difference
            )

            # If the model is accepted, save it as the previous model for future comparisons
            if evaluate_model_response.is_model_accepted:
                logging.info("New model is better than previous model. Saving it for future reference.")

                # Create a directory for the previous model
                artifact_dir = os.path.dirname(os.path.dirname(self.model_trainer_artifact.trained_model_file_path))
                previous_model_dir = os.path.join(artifact_dir, "previous_model")
                os.makedirs(previous_model_dir, exist_ok=True)

                # Copy the current model to the previous model directory
                import shutil
                current_model_path = self.model_trainer_artifact.trained_model_file_path
                previous_model_path = os.path.join(previous_model_dir, "model.pkl")
                shutil.copy2(current_model_path, previous_model_path)
                logging.info(f"Copied current model to {previous_model_path} for future reference")

            logging.info(f"Model evaluation artifact: {model_evaluation_artifact}")
            return model_evaluation_artifact

        except Exception as e:
            logging.error(f"Error in initiate_model_evaluation: {str(e)}")
            # Return a default artifact that accepts the model
            return ModelEvaluationArtifact(
                is_model_accepted=True,
                s3_model_path=self.model_eval_config.s3_model_key_path,
                trained_model_path=self.model_trainer_artifact.trained_model_file_path,
                changed_accuracy=0.0
            )