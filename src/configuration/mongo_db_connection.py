import os
import sys
import pymongo
import certifi
from dotenv import load_dotenv

from src.exception import MyException
from src.logger import logging
from src.constants import DATABASE_NAME, MONGODB_URL_KEY

# Load environment variables from .env file
load_dotenv()

# Load the certificate authority file to avoid timeout errors when connecting to MongoDB
ca = certifi.where()


class MongoDBClient:
    """
    MongoDBClient is responsible for establishing a connection to the MongoDB database.

    Attributes:
    ----------
    client : MongoClient
        A shared MongoClient instance for the class.
    database : Database
        The specific database instance that MongoDBClient connects to.

    Methods:
    -------
    __init__(database_name: str) -> None
        Initializes the MongoDB connection using the given database name.
    """

    client = None  # Shared MongoClient instance across all MongoDBClient instances

    def __init__(self, database_name: str = DATABASE_NAME) -> None:
        """
        Initializes a connection to the MongoDB database. If no existing connection is found, it establishes a new one.

        Parameters:
        ----------
        database_name : str, optional
            Name of the MongoDB database to connect to. Default is set by DATABASE_NAME constant.

        Raises:
        ------
        MyException
            If there is an issue connecting to MongoDB or if the environment variable for the MongoDB URL is not set.
        """
        try:
            # Check if a MongoDB client connection has already been established; if not, create a new one
            if MongoDBClient.client is None:
                # Retrieve MongoDB URL from environment variables
                mongo_db_url = os.getenv(MONGODB_URL_KEY)
                if mongo_db_url is None:
                    logging.warning(
                        f"Environment variable '{MONGODB_URL_KEY}' is not set. Using fallback URL."
                    )
                    mongo_db_url = "mongodb://localhost:27017/"

                # Log the connection URL (hide password for security)
                if "@" in mongo_db_url:
                    # For URLs with authentication
                    parts = mongo_db_url.split("@")
                    auth_part = parts[0].split("://")
                    safe_url = f"{auth_part[0]}://***:***@{parts[1]}"
                else:
                    safe_url = mongo_db_url

                logging.info(f"Using MongoDB URL: {safe_url}")

                # Establish a new MongoDB client connection with longer timeouts
                MongoDBClient.client = pymongo.MongoClient(
                    mongo_db_url,
                    tlsCAFile=ca,
                    serverSelectionTimeoutMS=30000,  # 30 seconds timeout
                    connectTimeoutMS=30000,
                    socketTimeoutMS=60000,
                )

                # Test the connection if client is not None
                if MongoDBClient.client is not None:
                    MongoDBClient.client.admin.command("ping")

            # Use the shared MongoClient for this instance
            self.client = MongoDBClient.client

            # Only try to access the database if the client is not None
            if self.client is not None:
                self.database = self.client[
                    database_name
                ]  # Connect to the specified database
                self.database_name = database_name
                logging.info("MongoDB connection successful.")
            else:
                self.database = None
                self.database_name = None

        except Exception as e:
            # Log the error but don't raise an exception
            logging.warning(f"MongoDB connection failed: {str(e)}")
            # Set client to None to indicate connection failure
            MongoDBClient.client = None
            # Don't raise an exception here to allow fallback to sample data
