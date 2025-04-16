import os
from dotenv import load_dotenv
import sys

def load_environment_variables():
    """Load environment variables from .env file"""
    # Load environment variables from .env file
    load_dotenv()
    
    # Check if required environment variables are set
    mongodb_url = os.getenv("MONGODB_URL")
    aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    aws_region = os.getenv("AWS_REGION")
    
    # Print status
    print("Environment variables status:")
    print(f"MONGODB_URL: {'✅ Set' if mongodb_url else '❌ Not set'}")
    print(f"AWS_ACCESS_KEY_ID: {'✅ Set' if aws_access_key_id else '❌ Not set'}")
    print(f"AWS_SECRET_ACCESS_KEY: {'✅ Set' if aws_secret_access_key else '❌ Not set'}")
    print(f"AWS_REGION: {'✅ Set' if aws_region else '❌ Not set'}")
    
    # Return True if all required variables are set
    return all([mongodb_url, aws_access_key_id, aws_secret_access_key, aws_region])

if __name__ == "__main__":
    print("Loading environment variables from .env file...")
    
    try:
        # Install python-dotenv if not already installed
        try:
            import dotenv
        except ImportError:
            print("Installing python-dotenv package...")
            import subprocess
            subprocess.check_call([sys.executable, "-m", "pip", "install", "python-dotenv"])
            from dotenv import load_dotenv
        
        # Load environment variables
        if load_environment_variables():
            print("\n✅ All required environment variables are set.")
            print("You can now run your application with:")
            print("python demo.py")
        else:
            print("\n❌ Some environment variables are not set.")
            print("Please update the .env file with your credentials.")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
