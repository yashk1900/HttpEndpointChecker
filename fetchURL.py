import yaml
import requests
import time
from collections import defaultdict
from urllib.parse import urlparse
import sys


def load_config(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

def check_health(endpoint):
    method = endpoint.get("method", "GET").upper()
    url = endpoint["url"]
    headers = endpoint.get("headers", {})
    body = endpoint.get("body", None)
    
    try:
        start_time = time.time()
        response = requests.request(method, url, headers=headers, data=body, timeout=5)
        latency = (time.time() - start_time) * 1000  # Convert to ms
        is_up = 200 <= response.status_code < 300 and latency < 500
        return is_up
    except requests.RequestException:
        return False

def log_availability_stats(stats):
    for domain, data in stats.items():
        total_checks = data["total"]
        up_checks = data["up"]
        availability = round((up_checks / total_checks) * 100) if total_checks else 0
        print(f"{domain} has {availability}% availability percentage")

def main(file_path):
    endpoints = load_config(file_path)
    domain_stats = defaultdict(lambda: {"up": 0, "total": 0})

    print("Starting health check monitoring. Press CTRL+C to stop.")
    try:
        while True:
            for endpoint in endpoints:
                domain = urlparse(endpoint["url"]).netloc
                is_up = check_health(endpoint)
                domain_stats[domain]["total"] += 1
                if is_up:
                    domain_stats[domain]["up"] += 1

            log_availability_stats(domain_stats)
            time.sleep(15)
    except KeyboardInterrupt:
        print("\nMonitoring stopped. Exiting program.")

if __name__ == "__main__":
    # if len(sys.argv) != 2:
    #     print("Usage: python monitor.py <path_to_yaml_file>")
    #     sys.exit(1)

    # config_file_path = sys.argv[1]
    main('/Users/yashkothekar/Desktop/589/sample.yaml')
