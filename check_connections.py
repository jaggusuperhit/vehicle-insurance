import os
import sys
import boto3
import pymongo
from pymongo import MongoClient
from botocore.exceptions import ClientError

def check_mongodb_connection():
    """Check if MongoDB connection is working"""
    print("\n--- MongoDB Connection Check ---")
    
    # Get MongoDB URL from environment variable or use default
    mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017/")
    print(f"Using MongoDB URL: {mongodb_url}")
    
    try:
        # Connect to MongoDB
        client = MongoClient(mongodb_url, serverSelectionTimeoutMS=5000)
        
        # Force a connection to verify it works
        server_info = client.server_info()
        
        print(f"✅ Successfully connected to MongoDB!")
        print(f"MongoDB version: {server_info.get('version', 'unknown')}")
        
        # List databases
        databases = client.list_database_names()
        print(f"Available databases: {', '.join(databases)}")
        
        # Check if we can access the insurance database
        if "insurance" in databases:
            db = client["insurance"]
            collections = db.list_collection_names()
            print(f"Collections in 'insurance' database: {', '.join(collections)}")
            
            # Check if vehicle_insurance collection exists and count documents
            if "vehicle_insurance" in collections:
                count = db["vehicle_insurance"].count_documents({})
                print(f"Found {count} documents in vehicle_insurance collection")
                
                # Show a sample document
                if count > 0:
                    sample = db["vehicle_insurance"].find_one()
                    print(f"Sample document: {sample}")
        
        return True
    except pymongo.errors.ServerSelectionTimeoutError as e:
        print(f"❌ Failed to connect to MongoDB: {e}")
        return False
    except Exception as e:
        print(f"❌ Error connecting to MongoDB: {e}")
        return False
    finally:
        if 'client' in locals():
            client.close()

def check_aws_connection():
    """Check if AWS connection is working"""
    print("\n--- AWS S3 Connection Check ---")
    
    # Get AWS credentials from environment variables
    aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    aws_region = os.getenv("AWS_REGION", "us-east-1")
    
    if not aws_access_key_id or not aws_secret_access_key:
        print("❌ AWS credentials not found in environment variables")
        return False
    
    print(f"AWS Access Key ID: {aws_access_key_id[:4]}...{aws_access_key_id[-4:] if len(aws_access_key_id) > 8 else ''}")
    print(f"AWS Region: {aws_region}")
    
    try:
        # Create an S3 client
        s3 = boto3.client(
            's3',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=aws_region
        )
        
        # List S3 buckets to verify connection
        response = s3.list_buckets()
        
        print(f"✅ Successfully connected to AWS S3!")
        print(f"Available buckets: {', '.join([bucket['Name'] for bucket in response['Buckets']])}")
        
        return True
    except ClientError as e:
        print(f"❌ Failed to connect to AWS S3: {e}")
        return False
    except Exception as e:
        print(f"❌ Error connecting to AWS S3: {e}")
        return False

if __name__ == "__main__":
    print("Checking connections to MongoDB and AWS S3...")
    
    mongodb_ok = check_mongodb_connection()
    aws_ok = check_aws_connection()
    
    print("\n--- Summary ---")
    print(f"MongoDB Connection: {'✅ OK' if mongodb_ok else '❌ Failed'}")
    print(f"AWS S3 Connection: {'✅ OK' if aws_ok else '❌ Failed'}")
    
    if not mongodb_ok or not aws_ok:
        print("\nSome connections failed. Please check your configuration.")
        sys.exit(1)
    else:
        print("\nAll connections are working properly!")
        sys.exit(0)
