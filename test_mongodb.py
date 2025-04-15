import os
import pymongo
import certifi
import logging
import dns.resolver  # For DNS debugging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Use the correct MongoDB URL
mongo_url = "mongodb+srv://jagtapsuraj636:hTIFywlGMNeKU7Xz@cluster0.pxxqyie.mongodb.net/vehicle?retryWrites=true&w=majority&appName=Cluster0"
logging.info("Using the provided MongoDB URL")

# Try to resolve the DNS for the MongoDB host
if "mongodb+srv://" in mongo_url:
    host = mongo_url.split("@")[1].split("/")[0]
    logging.info(f"Trying to resolve DNS for: {host}")
    try:
        # Try to resolve the SRV record
        srv_host = f"_mongodb._tcp.{host}"
        logging.info(f"Looking up SRV record: {srv_host}")
        answers = dns.resolver.resolve(srv_host, "SRV")
        for answer in answers:
            logging.info(f"SRV record found: {answer}")
    except Exception as e:
        logging.error(f"DNS resolution failed: {str(e)}")

# Hide password in logs
safe_url = mongo_url
if "@" in mongo_url:
    parts = mongo_url.split("@")
    auth_part = parts[0].split("://")
    safe_url = f"{auth_part[0]}://***:***@{parts[1]}"

logging.info(f"Connecting to MongoDB: {safe_url}")

try:
    # Connect to MongoDB
    client = pymongo.MongoClient(
        mongo_url,
        tlsCAFile=certifi.where(),
        serverSelectionTimeoutMS=10000,
        connectTimeoutMS=10000,
        socketTimeoutMS=20000,
    )

    # Test the connection
    client.admin.command("ping")
    logging.info("MongoDB connection successful!")

    # List databases
    databases = client.list_database_names()
    logging.info(f"Available databases: {databases}")

    # Check if 'vehicle' database exists
    if "vehicle" in databases:
        db = client["vehicle"]
        collections = db.list_collection_names()
        logging.info(f"Collections in 'vehicle' database: {collections}")

        # If there are collections, show a sample document from the first collection
        if collections:
            collection = db[collections[0]]
            sample = collection.find_one()
            logging.info(f"Sample document from {collections[0]}: {sample}")
    else:
        logging.warning("'vehicle' database not found")

except Exception as e:
    logging.error(f"MongoDB connection failed: {str(e)}")
