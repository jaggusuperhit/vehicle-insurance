# MongoDB Atlas Connection String
# Replace with your actual MongoDB Atlas connection string
$env:MONGODB_URL = "mongodb+srv://username:password@cluster0.pxxqyie.mongodb.net/?retryWrites=true&w=majority"

# AWS Credentials
# Replace with your actual AWS credentials
$env:AWS_ACCESS_KEY_ID = "YOUR_AWS_ACCESS_KEY_ID"
$env:AWS_SECRET_ACCESS_KEY = "YOUR_AWS_SECRET_ACCESS_KEY"
$env:AWS_REGION = "us-east-1"  # or your preferred region

# Print the environment variables to verify
Write-Host "Environment variables set:"
Write-Host "MONGODB_URL: $env:MONGODB_URL"
Write-Host "AWS_ACCESS_KEY_ID: $env:AWS_ACCESS_KEY_ID"
Write-Host "AWS_SECRET_ACCESS_KEY: $($env:AWS_SECRET_ACCESS_KEY.Substring(0, 5))..."
Write-Host "AWS_REGION: $env:AWS_REGION"

Write-Host "`nTo use these variables in your current session, run:"
Write-Host ".\setup_env.ps1"

Write-Host "`nTo make these variables persistent, add them to your system environment variables."
