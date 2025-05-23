import os
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.responses import HTMLResponse, RedirectResponse
from uvicorn import run as app_run

# Importing constants and pipeline modules from the project
from src.constants import APP_HOST, APP_PORT
from src.pipeline.prediction_pipeline import VehicleData, VehicleDataClassifier
from src.pipeline.training_pipeline import TrainPipeline

# Initialize FastAPI application
app = FastAPI(
    title="Vehicle Insurance Prediction",
    description="API for predicting customer interest in vehicle insurance",
    version="1.0.0"
)

# Mount the 'static' directory for serving static files (like CSS)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up Jinja2 template engine for rendering HTML templates
templates = Jinja2Templates(directory='templates')

# Allow all origins for Cross-Origin Resource Sharing (CORS)
origins = ["*"]

# Configure middleware to handle CORS, allowing requests from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class DataForm:
    """
    DataForm class to handle and process incoming form data.
    This class defines the vehicle-related attributes expected from the form.
    """
    def __init__(self, request: Request):
        self.request: Request = request
        self.Gender: Optional[int] = None
        self.Age: Optional[int] = None
        self.Driving_License: Optional[int] = None
        self.Region_Code: Optional[float] = None
        self.Previously_Insured: Optional[int] = None
        self.Annual_Premium: Optional[float] = None
        self.Policy_Sales_Channel: Optional[float] = None
        self.Vintage: Optional[int] = None
        self.Vehicle_Age_lt_1_Year: Optional[int] = None
        self.Vehicle_Age_gt_2_Years: Optional[int] = None
        self.Vehicle_Damage_Yes: Optional[int] = None


    async def get_vehicle_data(self):
        """
        Method to retrieve and assign form data to class attributes.
        This method is asynchronous to handle form data fetching without blocking.
        """
        form = await self.request.form()
        self.Gender = form.get("Gender")
        self.Age = form.get("Age")
        self.Driving_License = form.get("Driving_License")
        self.Region_Code = form.get("Region_Code")
        self.Previously_Insured = form.get("Previously_Insured")
        self.Annual_Premium = form.get("Annual_Premium")
        self.Policy_Sales_Channel = form.get("Policy_Sales_Channel")
        self.Vintage = form.get("Vintage")
        self.Vehicle_Age_lt_1_Year = form.get("Vehicle_Age_lt_1_Year")
        self.Vehicle_Age_gt_2_Years = form.get("Vehicle_Age_gt_2_Years")
        self.Vehicle_Damage_Yes = form.get("Vehicle_Damage_Yes")

# Route to render the main page with the form
@app.get("/", tags=["authentication"])
async def index(request: Request):
    """
    Renders the main HTML form page for vehicle data input.
    """
    return templates.TemplateResponse(
            "vehicledata.html",{"request": request, "context": "Rendering"})

# Route to trigger the model training process
@app.get("/train")
async def trainRouteClient(request: Request):
    """
    Endpoint to initiate the model training pipeline.
    """
    try:
        train_pipeline = TrainPipeline()
        train_pipeline.run_pipeline()
        return templates.TemplateResponse(
            "training.html",
            {"request": request, "context": "Training Completed Successfully!"}
        )

    except Exception as e:
        return templates.TemplateResponse(
            "training.html",
            {"request": request, "context": f"Error Occurred! {e}"}
        )

# Route to handle form submission and make predictions
@app.post("/")
async def predictRouteClient(request: Request):
    """
    Endpoint to receive form data, process it, and make a prediction.
    """
    try:
        form = DataForm(request)
        await form.get_vehicle_data()

        vehicle_data = VehicleData(
                                Gender= form.Gender,
                                Age = form.Age,
                                Driving_License = form.Driving_License,
                                Region_Code = form.Region_Code,
                                Previously_Insured = form.Previously_Insured,
                                Annual_Premium = form.Annual_Premium,
                                Policy_Sales_Channel = form.Policy_Sales_Channel,
                                Vintage = form.Vintage,
                                Vehicle_Age_lt_1_Year = form.Vehicle_Age_lt_1_Year,
                                Vehicle_Age_gt_2_Years = form.Vehicle_Age_gt_2_Years,
                                Vehicle_Damage_Yes = form.Vehicle_Damage_Yes
                                )

        # Convert form data into a DataFrame for the model
        vehicle_df = vehicle_data.get_vehicle_input_data_frame()

        # Initialize the prediction pipeline
        model_predictor = VehicleDataClassifier()

        # Make a prediction and retrieve the result
        value = model_predictor.predict(dataframe=vehicle_df)[0]

        # Interpret the prediction result as 'Response-Yes' or 'Response-No'
        status = "Response-Yes" if value == 1 else "Response-No"

        # Render the same HTML page with the prediction result
        return templates.TemplateResponse(
            "vehicledata.html",
            {"request": request, "context": status},
        )

    except Exception as e:
        return {"status": False, "error": f"{e}"}

# Health check endpoint for monitoring
@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring the application status
    """
    try:
        # Check if we can connect to MongoDB
        mongo_status = "OK"
        try:
            from pymongo import MongoClient
            mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017/")
            client = MongoClient(mongodb_url, serverSelectionTimeoutMS=1000)
            client.server_info()  # Will raise an exception if cannot connect
        except Exception as e:
            mongo_status = f"Error: {str(e)}"

        # Check if model files exist
        from src.constants import ARTIFACT_DIR
        local_model_path = os.path.join(ARTIFACT_DIR, "production_model", "model.pkl")
        model_status = "OK" if os.path.exists(local_model_path) else "Not found"

        return {
            "status": "healthy",
            "timestamp": str(datetime.now()),
            "environment": os.getenv("ENVIRONMENT", "development"),
            "services": {
                "mongodb": mongo_status,
                "model": model_status
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": str(datetime.now())
        }

# Main entry point to start the FastAPI server
if __name__ == "__main__":
    import webbrowser
    import threading
    import time

    # Function to open browser after a short delay
    def open_browser():
        time.sleep(1.5)  # Wait for the server to start
        webbrowser.open(f"http://{APP_HOST}:{APP_PORT}")

    # Start browser in a separate thread (only in development mode)
    if os.getenv("ENVIRONMENT", "development") == "development":
        threading.Thread(target=open_browser).start()

    # Start the FastAPI server
    print(f"\n🚀 Starting server at http://{APP_HOST}:{APP_PORT}")
    print(f"✨ Environment: {os.getenv('ENVIRONMENT', 'development')}")
    app_run(app, host=APP_HOST, port=APP_PORT)