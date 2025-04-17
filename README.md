# Vehicle Insurance Prediction

## Overview

This project predicts whether a customer will be interested in vehicle insurance based on various features like demographics, vehicle information, and policy details.

## Features

- Machine learning model to predict customer interest in vehicle insurance
- Modern UI with Indian-themed design
- Support for Rupee currency
- Production-grade CI/CD pipeline for automated testing, building, and deployment
- MongoDB integration for data storage
- AWS S3 integration for model storage
- Automated model monitoring and retraining
- Scheduled database backups
- Prometheus and Grafana monitoring

## Technologies Used

- Python
- FastAPI
- MongoDB
- AWS (S3, ECR, EC2)
- Docker
- GitHub Actions
- Prometheus & Grafana

## CI/CD Pipeline

The project includes a comprehensive CI/CD pipeline that automates:

1. **Testing**: Unit tests, linting, and Docker build tests
2. **Building**: Building and pushing Docker images to Amazon ECR
3. **Deployment**: Deploying to staging and production environments
4. **Monitoring**: Setting up Prometheus and Grafana for application monitoring
5. **Backup**: Scheduled MongoDB backups to S3

For detailed instructions on using the CI/CD pipeline, see [CI-CD-GUIDE.md](CI-CD-GUIDE.md).

## Getting Started

### Prerequisites

- Python 3.10+
- Docker
- AWS Account
- MongoDB Atlas Account

### Installation

1. Clone the repository

   ```bash
   git clone https://github.com/jaggusuperhit/vehicle-insurance.git
   cd vehicle-insurance
   ```

2. Install dependencies

   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables

   ```bash
   # For MongoDB connection
   export MONGODB_URL="your_mongodb_connection_string"

   # For AWS services
   export AWS_ACCESS_KEY_ID="your_aws_access_key"
   export AWS_SECRET_ACCESS_KEY="your_aws_secret_key"
   export AWS_DEFAULT_REGION="your_aws_region"
   ```

4. Run the application
   ```bash
   python app.py
   ```

### Docker Deployment

```bash
docker build -t vehicle-insurance .
docker run -d -p 5050:5050 -e MONGODB_URL="your_mongodb_connection_string" vehicle-insurance
```

## API Endpoints

- `/`: Main application UI
- `/train`: Trigger model training
- `/health`: Health check endpoint

## Monitoring

The application includes built-in monitoring with Prometheus and Grafana:

- Prometheus: http://your-server-ip:9090
- Grafana: http://your-server-ip:3000

## Automated Backups

MongoDB data is automatically backed up daily to an S3 bucket with a 30-day retention policy.

## Model Monitoring

The model performance is monitored every 6 hours to detect drift and trigger retraining if necessary.
