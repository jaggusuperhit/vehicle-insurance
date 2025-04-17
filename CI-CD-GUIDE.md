# CI/CD Pipeline Guide for Vehicle Insurance Prediction

This guide explains how to use and manage the CI/CD pipeline for the Vehicle Insurance Prediction application.

## Overview

The CI/CD pipeline automates the following processes:

1. **Testing**: Runs unit tests, linting, and Docker build tests
2. **Building**: Builds and pushes Docker images to Amazon ECR
3. **Deployment**: Deploys the application to staging and production environments
4. **Monitoring**: Sets up monitoring for the application and model performance
5. **Backup**: Performs scheduled backups of the MongoDB database

## Workflow Files

The following workflow files are available:

- `production-pipeline.yml`: Main CI/CD pipeline for testing, building, and deploying
- `scheduled-backup.yml`: Scheduled workflow for backing up MongoDB data
- `model-monitoring.yml`: Scheduled workflow for monitoring model performance

## Setting Up the CI/CD Pipeline

### Prerequisites

1. AWS Account with appropriate permissions
2. GitHub repository
3. EC2 instance for self-hosted runner
4. MongoDB Atlas account (or other MongoDB provider)

### Required Secrets

Set up the following secrets in your GitHub repository (Settings > Secrets and variables > Actions):

- `AWS_ACCESS_KEY_ID`: AWS access key with permissions for ECR, S3, etc.
- `AWS_SECRET_ACCESS_KEY`: AWS secret key
- `AWS_DEFAULT_REGION`: AWS region (e.g., us-east-1)
- `ECR_REPO`: Name of your ECR repository
- `MONGODB_URL`: MongoDB connection string

### Setting Up a Self-Hosted Runner

1. Launch an EC2 instance (recommended: t2.medium or larger with Ubuntu)
2. SSH into the instance
3. Run the setup script:

```bash
sudo bash scripts/setup-runner.sh YOUR_GITHUB_TOKEN
```

Replace `YOUR_GITHUB_TOKEN` with a GitHub personal access token with `repo` scope.

## Using the CI/CD Pipeline

### Triggering the Pipeline

The main pipeline can be triggered in several ways:

1. **Automatically on push to main branch**:
   - Any push to the `main` branch will trigger the pipeline

2. **Manually via GitHub Actions UI**:
   - Go to Actions > Production CI/CD Pipeline > Run workflow

3. **On schedule**:
   - The pipeline runs weekly on Sunday at midnight

### Pipeline Stages

#### 1. Test

- Runs unit tests with code coverage
- Performs linting with flake8
- Tests Docker build
- Verifies container health

#### 2. Build

- Builds Docker image
- Tags with commit SHA and latest
- Pushes to Amazon ECR
- Scans for vulnerabilities

#### 3. Deploy to Staging

- Deploys to staging environment
- Runs on port 5051
- Verifies deployment health

#### 4. Deploy to Production

- Deploys to production environment
- Runs on port 5050
- Verifies deployment health
- Sends deployment notification

#### 5. Setup Monitoring

- Sets up Prometheus for metrics collection
- Sets up Grafana for visualization

## Monitoring

### Application Monitoring

- Prometheus: http://your-ec2-ip:9090
- Grafana: http://your-ec2-ip:3000 (default login: admin/admin)

### Model Monitoring

The model monitoring workflow runs every 6 hours to:

1. Evaluate model performance
2. Detect model drift
3. Trigger retraining if necessary

## Database Backups

The database backup workflow runs daily to:

1. Backup MongoDB data
2. Upload to S3
3. Apply lifecycle policies (30-day retention)

## Troubleshooting

### Common Issues

1. **Pipeline fails at test stage**:
   - Check test logs for details
   - Fix failing tests and push changes

2. **Docker build fails**:
   - Check Docker build logs
   - Verify Dockerfile and dependencies

3. **Deployment fails**:
   - Check if EC2 instance is running
   - Verify self-hosted runner is active
   - Check if ports are open in security group

4. **Monitoring not working**:
   - Verify Prometheus and Grafana containers are running
   - Check if ports 9090 and 3000 are accessible

### Viewing Logs

- GitHub Actions logs: Available in the Actions tab
- Application logs: Available in the Docker container
  ```bash
  docker logs vehicle-insurance
  ```
- Monitoring logs: Available in the logs directory
  ```bash
  cat logs/model_monitoring.log
  ```

## Manual Operations

### Manually Triggering Backups

```bash
# SSH into the EC2 instance
ssh ubuntu@your-ec2-ip

# Run the backup script
MONGODB_URL="your-mongodb-url" bash scripts/backup-mongodb.sh
```

### Manually Restarting the Application

```bash
# SSH into the EC2 instance
ssh ubuntu@your-ec2-ip

# Restart the container
docker restart vehicle-insurance
```

### Manually Checking Application Health

```bash
# SSH into the EC2 instance
ssh ubuntu@your-ec2-ip

# Check health endpoint
curl http://localhost:5050/health
```

## Best Practices

1. **Always create pull requests** instead of pushing directly to main
2. **Review test results** before merging
3. **Monitor deployment** after changes
4. **Check logs regularly** for any issues
5. **Keep secrets secure** and rotate them periodically
