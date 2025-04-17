"""
Monitoring script for the Vehicle Insurance Prediction application.
This script collects metrics and sends them to Prometheus.
"""

import time
import os
import requests
import psutil
import logging
from prometheus_client import start_http_server, Gauge, Counter, Summary

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Define metrics
API_REQUESTS = Counter('api_requests_total', 'Total count of API requests', ['endpoint', 'method', 'status'])
API_LATENCY = Summary('api_request_latency_seconds', 'API request latency in seconds', ['endpoint'])
PREDICTION_COUNTER = Counter('predictions_total', 'Total number of predictions made', ['result'])
CPU_USAGE = Gauge('cpu_usage_percent', 'CPU usage percentage')
MEMORY_USAGE = Gauge('memory_usage_percent', 'Memory usage percentage')
DISK_USAGE = Gauge('disk_usage_percent', 'Disk usage percentage')

# Application settings
APP_HOST = os.getenv('APP_HOST', 'localhost')
APP_PORT = int(os.getenv('APP_PORT', 5050))
METRICS_PORT = int(os.getenv('METRICS_PORT', 8000))
CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL', 15))  # seconds

def collect_system_metrics():
    """Collect system metrics like CPU, memory, and disk usage."""
    try:
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        CPU_USAGE.set(cpu_percent)
        
        # Memory usage
        memory = psutil.virtual_memory()
        MEMORY_USAGE.set(memory.percent)
        
        # Disk usage
        disk = psutil.disk_usage('/')
        DISK_USAGE.set(disk.percent)
        
        logger.debug(f"System metrics collected: CPU={cpu_percent}%, Memory={memory.percent}%, Disk={disk.percent}%")
    except Exception as e:
        logger.error(f"Error collecting system metrics: {e}")

def check_application_health():
    """Check if the application is healthy and collect metrics."""
    try:
        # Health check
        start_time = time.time()
        response = requests.get(f"http://{APP_HOST}:{APP_PORT}/health")
        latency = time.time() - start_time
        
        API_REQUESTS.labels(endpoint='/health', method='GET', status=response.status_code).inc()
        API_LATENCY.labels(endpoint='/health').observe(latency)
        
        if response.status_code == 200:
            health_data = response.json()
            logger.info(f"Application health: {health_data['status']}")
            
            # Log additional health information if available
            if 'services' in health_data:
                for service, status in health_data['services'].items():
                    logger.info(f"Service {service}: {status}")
        else:
            logger.warning(f"Health check failed with status code: {response.status_code}")
            
    except requests.RequestException as e:
        logger.error(f"Error checking application health: {e}")

def main():
    """Main function to start the monitoring server and collect metrics."""
    logger.info(f"Starting monitoring server on port {METRICS_PORT}")
    start_http_server(METRICS_PORT)
    
    logger.info(f"Monitoring application at http://{APP_HOST}:{APP_PORT}")
    logger.info(f"Collecting metrics every {CHECK_INTERVAL} seconds")
    
    while True:
        collect_system_metrics()
        check_application_health()
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
