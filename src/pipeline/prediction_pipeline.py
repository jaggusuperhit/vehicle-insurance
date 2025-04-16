import sys
import os
from src.entity.config_entity import VehiclePredictorConfig
from src.entity.s3_estimator import InsuranceEstimator
from src.exception import MyException
from src.logger import logging
from pandas import DataFrame


class VehicleData:
    def __init__(self,
                Gender,
                Age,
                Driving_License,
                Region_Code,
                Previously_Insured,
                Annual_Premium,
                Policy_Sales_Channel,
                Vintage,
                Vehicle_Age_lt_1_Year,
                Vehicle_Age_gt_2_Years,
                Vehicle_Damage_Yes
                ):
        """
        Vehicle Data constructor
        Input: all features of the trained model for prediction
        """
        try:
            # Validate and convert inputs
            self.Gender = int(Gender)
            self.Age = int(Age)
            self.Driving_License = int(Driving_License)
            self.Region_Code = float(Region_Code)
            self.Previously_Insured = int(Previously_Insured)
            self.Annual_Premium = float(Annual_Premium)
            self.Policy_Sales_Channel = float(Policy_Sales_Channel)

            # Ensure Vintage is not negative
            vintage_value = int(Vintage)
            if vintage_value < 0:
                logging.warning(f"Negative Vintage value ({vintage_value}) received. Setting to 0.")
                vintage_value = 0
            self.Vintage = vintage_value

            self.Vehicle_Age_lt_1_Year = int(Vehicle_Age_lt_1_Year)
            self.Vehicle_Age_gt_2_Years = int(Vehicle_Age_gt_2_Years)
            self.Vehicle_Damage_Yes = int(Vehicle_Damage_Yes)

            logging.info("Successfully validated and processed all input values")

        except ValueError as ve:
            logging.error(f"Invalid input value: {str(ve)}")
            raise MyException(f"Invalid input value: {str(ve)}", sys) from ve
        except Exception as e:
            logging.error(f"Error in VehicleData initialization: {str(e)}")
            raise MyException(e, sys) from e

    def get_vehicle_input_data_frame(self)-> DataFrame:
        """
        This function returns a DataFrame from USvisaData class input
        """
        try:

            vehicle_input_dict = self.get_vehicle_data_as_dict()
            return DataFrame(vehicle_input_dict)

        except Exception as e:
            raise MyException(e, sys) from e


    def get_vehicle_data_as_dict(self):
        """
        This function returns a dictionary from VehicleData class input
        """
        logging.info("Entered get_vehicle_data_as_dict method as VehicleData class")

        try:
            input_data = {
                "id": [0],  # Add a dummy id column to satisfy the model requirements
                "Gender": [self.Gender],
                "Age": [self.Age],
                "Driving_License": [self.Driving_License],
                "Region_Code": [self.Region_Code],
                "Previously_Insured": [self.Previously_Insured],
                "Annual_Premium": [self.Annual_Premium],
                "Policy_Sales_Channel": [self.Policy_Sales_Channel],
                "Vintage": [self.Vintage],
                "Vehicle_Age_lt_1_Year": [self.Vehicle_Age_lt_1_Year],
                "Vehicle_Age_gt_2_Years": [self.Vehicle_Age_gt_2_Years],
                "Vehicle_Damage_Yes": [self.Vehicle_Damage_Yes]
            }

            logging.info("Created vehicle data dict")
            logging.info("Exited get_vehicle_data_as_dict method as VehicleData class")
            return input_data

        except Exception as e:
            raise MyException(e, sys) from e

class VehicleDataClassifier:
    def __init__(self, prediction_pipeline_config: VehiclePredictorConfig = VehiclePredictorConfig(),) -> None:
        """
        :param prediction_pipeline_config: Configuration for prediction the value
        """
        try:
            self.prediction_pipeline_config = prediction_pipeline_config

            # Set up paths for local model fallback
            import os
            from src.constants import ARTIFACT_DIR
            self.local_model_path = os.path.join(ARTIFACT_DIR, "production_model", "model.pkl")

        except Exception as e:
            raise MyException(e, sys)

    def predict(self, dataframe) -> str:
        """
        This is the method of VehicleDataClassifier
        Returns: Prediction in string format
        """
        try:
            logging.info("Entered predict method of VehicleDataClassifier class")

            # Try to use S3 model first
            try:
                logging.info("Attempting to use S3 model for prediction")
                model = InsuranceEstimator(
                    bucket_name=self.prediction_pipeline_config.model_bucket_name,
                    model_path=self.prediction_pipeline_config.model_file_path,
                )
                result = model.predict(dataframe)
                logging.info("Successfully used S3 model for prediction")
                return result

            except Exception as s3_error:
                # If S3 model fails, try local model
                logging.warning(f"S3 model prediction failed: {str(s3_error)}. Trying local model.")
                from src.entity.local_estimator import LocalInsuranceEstimator

                if os.path.exists(self.local_model_path):
                    logging.info(f"Using local model at {self.local_model_path}")
                    local_model = LocalInsuranceEstimator(model_path=self.local_model_path)
                    result = local_model.predict(dataframe)
                    logging.info("Successfully used local model for prediction")
                    return result
                else:
                    logging.error(f"Local model not found at {self.local_model_path}")
                    raise MyException(f"Neither S3 nor local model is available for prediction", sys)

        except Exception as e:
            logging.error(f"Error in prediction: {str(e)}")
            raise MyException(e, sys)