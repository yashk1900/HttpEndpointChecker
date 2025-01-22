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

async def check_health(endpoint,session):

    # Default GET method
    method = endpoint.get("method", "GET").upper()
    url = endpoint["url"]
    headers = endpoint.get("headers", {})
    body = endpoint.get("body", None)
    try:
        start_time = time.time()
        async with session.request(method, url, headers=headers, data=body, timeout=5) as response:
            
            # latency = response.elapsed.total_seconds() * 1000  # in milliseconds
            
            latency = (time.time() - start_time) * 1000 
            print("Latencky:",latency)
            print(response)
            is_up = 200 <= response.status < 300 and latency < 500
            return urlparse(url).netloc, is_up, latency
    except Exception as e:
            print("Error:", e)
            return urlparse(url).netloc, False, 0

def log_availability_stats(stats):
    for domain, data in stats.items():
        total_checks = data["total"]
        up_checks = data["up"]
        # Round to nearest percentage
        availability = round((up_checks / total_checks) * 100) if total_checks else 0
        print(f"{domain} has {availability}% availability percentage")

async def monitor_health(endpoints):
    domain_stats = defaultdict(lambda: {"up": 0, "total": 0})
    async with aiohttp.ClientSession() as session:
        while True:
            tasks = [check_health(endpoint, session) for endpoint in endpoints]
            results = await asyncio.gather(*tasks)

            for domain, is_up,_ in results:
                domain_stats[domain]["total"] += 1
                if is_up:
                    domain_stats[domain]["up"] += 1

            # Log the availability for each domain
            for domain, data in domain_stats.items():
                availability = round((data["up"] / data["total"]) * 100) if data["total"] > 0 else 0
                print(f"{domain} has {availability}% availability percentage")

            await asyncio.sleep(15)  # Wait for 15 seconds before the next check

def main(file_path):
    endpoints = load_config(file_path)
    asyncio.run(monitor_health(endpoints))
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python fetchURL.py <path_to_yaml_file>")
        sys.exit(1)

    # Accept the file path from user
    config_file_path = sys.argv[1]
    main(config_file_path)
