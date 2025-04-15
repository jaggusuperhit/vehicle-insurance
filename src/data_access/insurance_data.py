import sys
import os
import pandas as pd
import numpy as np
from typing import Optional
import logging

from src.configuration.mongo_db_connection import MongoDBClient
from src.constants import DATABASE_NAME, COLLECTION_NAME
from src.exception import MyException


class InsuranceData:
    """
    A class to export MongoDB records as a pandas DataFrame.
    """

    def __init__(self) -> None:
        """
        Initializes the MongoDB client connection.
        """
        # Try to connect to MongoDB
        self.mongo_client = MongoDBClient(database_name=DATABASE_NAME)
        # Check if MongoDB connection was successful
        self.use_mongodb = self.mongo_client.client is not None

        if self.use_mongodb:
            logging.info("MongoDB connection established successfully.")
        else:
            logging.warning("MongoDB connection failed. Will use sample data instead.")

    def export_collection_as_dataframe(
        self, collection_name: str, database_name: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Exports an entire MongoDB collection as a pandas DataFrame.
        If MongoDB is not available, uses a sample CSV file instead.

        Parameters:
        ----------
        collection_name : str
            The name of the MongoDB collection to export.
        database_name : Optional[str]
            Name of the database (optional). Defaults to DATABASE_NAME.

        Returns:
        -------
        pd.DataFrame
            DataFrame containing the collection data, with '_id' column removed and 'na' values replaced with NaN.
        """
        try:
            if self.use_mongodb:
                # Access specified collection from the default or specified database
                if database_name is None:
                    collection = self.mongo_client.database[collection_name]
                else:
                    collection = self.mongo_client.client[database_name][
                        collection_name
                    ]

                # Convert collection data to DataFrame and preprocess
                logging.info(
                    f"Fetching data from MongoDB collection: {collection_name}"
                )

                # Set a timeout for the find operation
                try:
                    # Try to fetch just one document first to test the connection
                    test_doc = collection.find_one()
                    if test_doc:
                        logging.info("Successfully connected to MongoDB and found data")
                        # Now fetch a limited number of documents with a timeout
                        # Limit to 1000 documents to avoid timeout issues
                        cursor = collection.find().limit(1000)
                        cursor.max_time_ms(10000)  # 10 second timeout
                        logging.info(
                            "Fetching documents from MongoDB (limited to 1000)..."
                        )
                        data = list(cursor)
                        df = pd.DataFrame(data)

                        if len(df) > 0:
                            logging.info(
                                f"Successfully fetched {len(df)} records from MongoDB"
                            )
                            if "_id" in df.columns.to_list():
                                df = df.drop(columns=["_id"], axis=1)
                        else:
                            logging.warning(
                                f"No data found in MongoDB collection: {collection_name}. Using sample data instead."
                            )
                            # Fall back to sample data if collection is empty
                            df = self._create_sample_data()
                    else:
                        logging.warning(
                            f"No documents found in collection: {collection_name}"
                        )
                        df = self._create_sample_data()
                except Exception as e:
                    logging.error(f"Error fetching data from MongoDB: {str(e)}")
                    df = self._create_sample_data()
            else:
                # Use sample data instead
                df = self._create_sample_data()

            # Common preprocessing
            df.replace({"na": np.nan}, inplace=True)
            return df

        except Exception as e:
            logging.error(f"Error in export_collection_as_dataframe: {str(e)}")
            logging.info("Falling back to sample data due to error")
            # Fall back to sample data in case of any error
            df = self._create_sample_data()
            df.replace({"na": np.nan}, inplace=True)
            return df

    def _create_sample_data(self) -> pd.DataFrame:
        """
        Creates a sample DataFrame with insurance data for development and testing.
        Includes all columns required by the schema.

        Returns:
        -------
        pd.DataFrame
            Sample DataFrame with insurance data.
        """
        logging.info("Creating sample insurance data with all required columns")

        # Create sample data with 100 records to have enough for train/test split
        num_samples = 100

        # Generate sample data with all required columns from schema.yaml
        sample_data = {
            "id": list(range(1, num_samples + 1)),
            "Gender": np.random.choice(["Male", "Female"], size=num_samples),
            "Age": np.random.randint(18, 70, size=num_samples),
            "Driving_License": np.random.choice([0, 1], size=num_samples, p=[0.05, 0.95]),
            "Region_Code": np.random.uniform(1.0, 50.0, size=num_samples),
            "Previously_Insured": np.random.choice([0, 1], size=num_samples),
            "Vehicle_Age": np.random.choice(["< 1 Year", "1-2 Year", "> 2 Years"], size=num_samples),
            "Vehicle_Damage": np.random.choice(["Yes", "No"], size=num_samples),
            "Annual_Premium": np.random.uniform(20000.0, 60000.0, size=num_samples),
            "Policy_Sales_Channel": np.random.uniform(100.0, 200.0, size=num_samples),
            "Vintage": np.random.randint(1, 100, size=num_samples),
            "Response": np.random.choice([0, 1], size=num_samples, p=[0.7, 0.3]),  # Imbalanced target
        }

        df = pd.DataFrame(sample_data)

        # Convert columns to appropriate types as per schema
        df['Gender'] = df['Gender'].astype('category')
        df['Vehicle_Age'] = df['Vehicle_Age'].astype('category')
        df['Vehicle_Damage'] = df['Vehicle_Damage'].astype('category')
        df['id'] = df['id'].astype('int')
        df['Age'] = df['Age'].astype('int')
        df['Driving_License'] = df['Driving_License'].astype('int')
        df['Previously_Insured'] = df['Previously_Insured'].astype('int')
        df['Vintage'] = df['Vintage'].astype('int')
        df['Response'] = df['Response'].astype('int')
        df['Region_Code'] = df['Region_Code'].astype('float')
        df['Annual_Premium'] = df['Annual_Premium'].astype('float')
        df['Policy_Sales_Channel'] = df['Policy_Sales_Channel'].astype('float')

        logging.info(f"Created sample data with {len(df)} records and columns: {df.columns.tolist()}")
        return df
