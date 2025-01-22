# Check out the complete solution at : https://github.com/yashk1900/HttpEndpointChecker/tree/main
# To run this stand alone file you will need to install the following dependencies
# 1. pyyaml
# 2. requests
# 3. aiohttp
# Instead, if you choose to clone the above repo, you will just need to run `pip install .` once

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

    # Run requests asynchronously
    try:
        start_time = time.time()
        async with session.request(method, url, headers=headers, data=body, timeout=5) as response:
            # calculate latency
            latency = (time.time() - start_time) * 1000 
            is_up = 200 <= response.status < 300 and latency < 500
            return urlparse(url).netloc, is_up, latency
        
    except Exception as e:
            return urlparse(url).netloc, False, 0

async def monitor_health(endpoints):
    stats = defaultdict(lambda: {"up": 0, "total": 0})
    async with aiohttp.ClientSession() as session:
        while True:
            # each endpoint is associated with a particular task
            tasks = [check_health(endpoint, session) for endpoint in endpoints]
            results = await asyncio.gather(*tasks)

            # update ther stats
            for domain, is_up,_ in results:
                stats[domain]["total"] += 1
                if is_up:
                    stats[domain]["up"] += 1

            # Log the availability for each domain
            print("-----------")
            for domain, data in stats.items():
                availability = round((data["up"] / data["total"]) * 100) if data["total"] > 0 else 0
                print(f"{domain} has {availability}% availability percentage")
            print("-----------")
            await asyncio.sleep(15)

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
