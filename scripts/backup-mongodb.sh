#!/bin/bash
# Script to backup MongoDB data to AWS S3

# Exit immediately if a command exits with a non-zero status
set -e

# Configuration
MONGODB_URI="${MONGODB_URL:-mongodb://localhost:27017}"
DATABASE_NAME="vehicle"
BACKUP_DIR="/tmp/mongodb_backups"
S3_BUCKET="vehicle-insurance-backups"
DATE=$(date +%Y-%m-%d-%H-%M-%S)
BACKUP_NAME="mongodb-backup-${DATE}"

# Create backup directory if it doesn't exist
mkdir -p ${BACKUP_DIR}

echo "Starting MongoDB backup..."

# Perform the backup
mongodump --uri="${MONGODB_URI}" --db=${DATABASE_NAME} --out=${BACKUP_DIR}/${BACKUP_NAME}

# Compress the backup
echo "Compressing backup..."
tar -czf ${BACKUP_DIR}/${BACKUP_NAME}.tar.gz -C ${BACKUP_DIR} ${BACKUP_NAME}

# Upload to S3
echo "Uploading to S3..."
aws s3 cp ${BACKUP_DIR}/${BACKUP_NAME}.tar.gz s3://${S3_BUCKET}/${BACKUP_NAME}.tar.gz

# Clean up
echo "Cleaning up temporary files..."
rm -rf ${BACKUP_DIR}/${BACKUP_NAME}
rm -f ${BACKUP_DIR}/${BACKUP_NAME}.tar.gz

echo "Backup completed successfully!"
echo "Backup stored in S3: s3://${S3_BUCKET}/${BACKUP_NAME}.tar.gz"
