import asyncio
import aiohttp
import yaml
import requests
import time
from collections import defaultdict
from urllib.parse import urlparse
import sys

# Convert the yaml file to a python object
def load_config(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

def check_health(endpoint):

    # Default GET method
    method = endpoint.get("method", "GET").upper()
    url = endpoint["url"]
    headers = endpoint.get("headers", {})
    body = endpoint.get("body", None)
    try:
        start_time = time.time()
        response = requests.request(method, url, headers=headers, data=body, timeout=5)
        latency = (time.time() - start_time) * 1000 
        # We want response of 2XX and latency <500
        is_up = 200 <= response.status_code < 300 and latency < 500
        return is_up
    except requests.RequestException:
        return False

def log_availability_stats(stats):
    for domain, data in stats.items():
        total_checks = data["total"]
        up_checks = data["up"]
        # Round to nearest percentage
        availability = round((up_checks / total_checks) * 100) if total_checks else 0
        print(f"{domain} has {availability}% availability percentage")

def main(file_path):
    # get list of individual endpoints
    endpoints = load_config(file_path)
    # local storage, to maintain stats
    domain_stats = defaultdict(lambda: {"up": 0, "total": 0})

    print("Starting health check monitoring. Press CTRL+C to stop.")
    try:
        while True:
            for endpoint in endpoints:

                # Use urlparse and remove the port number
                domain = urlparse(endpoint["url"]).netloc.split(':')[0]
                is_up = check_health(endpoint)
                domain_stats[domain]["total"] += 1
                if is_up:
                    domain_stats[domain]["up"] += 1
            print("----------------------")
            log_availability_stats(domain_stats)
            print("----------------------")
            time.sleep(15)
    except KeyboardInterrupt:
        print("\nMonitoring stopped. Exiting program.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python fetchURL.py <path_to_yaml_file>")
        sys.exit(1)

    # Accept the file path from user
    config_file_path = sys.argv[1]
    main(config_file_path)
