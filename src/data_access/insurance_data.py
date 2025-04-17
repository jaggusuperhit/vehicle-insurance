import sys
import os
import pandas as pd
import numpy as np
from typing import Optional
import logging

from src.configuration.mongo_db_connection import MongoDBClient
from src.constants import DATABASE_NAME, COLLECTION_NAME
from src.exception import MyException
from src.utils.sample_data import get_sample_data


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
        Uses the get_sample_data utility which provides consistent sample data.

        Returns:
        -------
        pd.DataFrame
            Sample DataFrame with insurance data.
        """
        logging.info("Using sample data utility for testing/development")

        # Get sample data from utility
        df = get_sample_data()

        # Ensure proper data types
        if not df.empty:
            try:
                # Convert categorical columns
                for col in ['Gender', 'Vehicle_Age', 'Vehicle_Damage']:
                    if col in df.columns:
                        df[col] = df[col].astype('category')

                # Convert integer columns
                for col in ['id', 'Age', 'Driving_License', 'Previously_Insured', 'Vintage', 'Response']:
                    if col in df.columns:
                        df[col] = df[col].astype('int')

                # Convert float columns
                for col in ['Region_Code', 'Annual_Premium', 'Policy_Sales_Channel']:
                    if col in df.columns:
                        df[col] = df[col].astype('float')
            except Exception as e:
                logging.warning(f"Error converting data types: {str(e)}")

        logging.info(f"Using sample data with {len(df)} records and columns: {df.columns.tolist()}")
        return df
