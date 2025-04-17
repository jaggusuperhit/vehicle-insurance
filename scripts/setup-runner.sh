#!/bin/bash
# Script to set up a GitHub Actions self-hosted runner on an EC2 instance

# Exit immediately if a command exits with a non-zero status
set -e

# Check if script is run as root
if [ "$(id -u)" -ne 0 ]; then
    echo "This script must be run as root or with sudo privileges"
    exit 1
fi

# Variables - replace these with your actual values
GITHUB_REPO_OWNER="jaggusuperhit"
GITHUB_REPO_NAME="vehicle-insurance"
RUNNER_NAME="ec2-runner"
RUNNER_LABELS="self-hosted,linux,ec2"
RUNNER_WORK_DIR="_work"

# Update system packages
echo "Updating system packages..."
apt-get update
apt-get upgrade -y

# Install required dependencies
echo "Installing dependencies..."
apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release \
    jq \
    git

# Install Docker
echo "Installing Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    usermod -aG docker ubuntu
    systemctl enable docker
    systemctl start docker
else
    echo "Docker is already installed"
fi

# Install AWS CLI
echo "Installing AWS CLI..."
if ! command -v aws &> /dev/null; then
    curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
    apt-get install -y unzip
    unzip awscliv2.zip
    ./aws/install
    rm -rf aws awscliv2.zip
else
    echo "AWS CLI is already installed"
fi

# Create a user for the runner
echo "Creating runner user..."
if ! id -u github-runner &>/dev/null; then
    useradd -m -s /bin/bash github-runner
    usermod -aG docker github-runner
fi

# Switch to the github-runner user
cd /home/github-runner

# Get the latest runner version
echo "Getting latest runner version..."
GITHUB_TOKEN=$1
if [ -z "$GITHUB_TOKEN" ]; then
    echo "GitHub token not provided. Please provide a token with repo scope."
    echo "Usage: $0 <github_token>"
    exit 1
fi

LATEST_VERSION_LABEL=$(curl -s -X GET \
    -H "Authorization: token ${GITHUB_TOKEN}" \
    -H "Accept: application/vnd.github.v3+json" \
    "https://api.github.com/repos/actions/runner/releases/latest" \
    | jq -r '.tag_name')
LATEST_VERSION=${LATEST_VERSION_LABEL:1}  # Remove the 'v' prefix

echo "Latest runner version: ${LATEST_VERSION}"

# Download and extract the runner
echo "Downloading and extracting the runner..."
if [ ! -d "actions-runner" ]; then
    mkdir -p actions-runner
    cd actions-runner
    curl -o actions-runner-linux-x64-${LATEST_VERSION}.tar.gz -L \
        https://github.com/actions/runner/releases/download/${LATEST_VERSION_LABEL}/actions-runner-linux-x64-${LATEST_VERSION}.tar.gz
    tar xzf actions-runner-linux-x64-${LATEST_VERSION}.tar.gz
    rm actions-runner-linux-x64-${LATEST_VERSION}.tar.gz
else
    echo "Runner directory already exists"
    cd actions-runner
fi

# Get a registration token
echo "Getting registration token..."
RUNNER_TOKEN=$(curl -s -X POST \
    -H "Authorization: token ${GITHUB_TOKEN}" \
    -H "Accept: application/vnd.github.v3+json" \
    "https://api.github.com/repos/${GITHUB_REPO_OWNER}/${GITHUB_REPO_NAME}/actions/runners/registration-token" \
    | jq -r '.token')

# Configure the runner
echo "Configuring the runner..."
chown -R github-runner:github-runner /home/github-runner/actions-runner
sudo -u github-runner ./config.sh \
    --url "https://github.com/${GITHUB_REPO_OWNER}/${GITHUB_REPO_NAME}" \
    --token "${RUNNER_TOKEN}" \
    --name "${RUNNER_NAME}" \
    --labels "${RUNNER_LABELS}" \
    --work "${RUNNER_WORK_DIR}" \
    --unattended

# Install the runner as a service
echo "Installing the runner as a service..."
./svc.sh install github-runner
./svc.sh start

# Create a service file for auto-start
cat > /etc/systemd/system/github-runner.service << EOF
[Unit]
Description=GitHub Actions Runner
After=network.target

[Service]
ExecStart=/home/github-runner/actions-runner/run.sh
User=github-runner
WorkingDirectory=/home/github-runner/actions-runner
KillMode=process
KillSignal=SIGTERM
TimeoutStopSec=5min
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start the service
systemctl daemon-reload
systemctl enable github-runner
systemctl start github-runner

echo "GitHub Actions runner setup complete!"
echo "Runner name: ${RUNNER_NAME}"
echo "Runner labels: ${RUNNER_LABELS}"
echo "Runner working directory: ${RUNNER_WORK_DIR}"

# Setup monitoring ports
echo "Setting up monitoring ports..."
ufw allow 5050/tcp
ufw allow 5051/tcp
ufw allow 9090/tcp
ufw allow 3000/tcp
ufw allow 8000/tcp

echo "Setup complete! The runner should now be visible in your GitHub repository's Actions settings."
