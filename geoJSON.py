import requests
import os
from pathlib import Path
from dotenv import load_dotenv

class QvantumAPI:
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = "https://dev.api-v2.qvantum.scio.services"
        self.token_url = "https://gardian-ecosystem.eu.auth0.com/oauth/token"
        self.access_token = self.get_access_token()

    def get_access_token(self):
        payload = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "audience": "https://qvantum.scio.services",
            "grant_type": "client_credentials"
        }
        headers = {"content-type": "application/json"}
        response = requests.post(self.token_url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()["access_token"]

    def post_layers_metadata(self, latitude, longitude, from_idx=0, size=10):
        url = f"{self.base_url}/api/geosearch/layers/metadata/{from_idx}/{size}"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        body = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [longitude, latitude]
            }
        }
        response = requests.post(url, json=body, headers=headers)
        response.raise_for_status()
        return response.json()

    def post_layer_data(self, latitude, longitude, from_idx=0, size=10):
        url = f"{self.base_url}/api/geosearch/layers/data/{from_idx}/{size}"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        body = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [longitude, latitude]
            }
        }
        response = requests.post(url, json=body, headers=headers)
        response.raise_for_status()
        return response.json()  # Contains jobId

    def get_layer_data_status(self, job_id):
        # Correct endpoint for job status
        url = f"{self.base_url}/api/geosearch/layers/job/{job_id}"
        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        if response.text:
            try:
                return response.json()
            except Exception as e:
                print("JSON decode error:", e)
                print("Response text:", response.text)
                return None
        else:
            print("Empty response from API")
            return None

    def get_layer_data_result(self, job_id):
        # Fetch actual data after status is COMPLETED
        url = f"{self.base_url}/api/geosearch/layers/data/{job_id}"
        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        if response.text:
            try:
                return response.json()
            except Exception as e:
                print("JSON decode error:", e)
                print("Response text:", response.text)
                return None
        else:
            print("Empty response from API")
            return None

# --------- How to use the class ---------
if __name__ == "__main__":
    # Load environment variables from the single project-root .env file
    load_dotenv(Path(__file__).resolve().parent / ".env")
    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")

    api = QvantumAPI(client_id, client_secret)

    # # Example: Ethiopia coordinates
    # lat, lon = 6.479447, 40.267359

    lat, lon = 125.6, 10.1

    # 1. Fetch available layers metadata for a point
    layers = api.post_layers_metadata(lat, lon, from_idx=0, size=5)
    print("Available Layers Metadata:", layers)

    # 2. Request actual data for a point (returns jobId)
    layer_data_job = api.post_layer_data(lat, lon, from_idx=0, size=1)
    print("Layer Data Job:", layer_data_job)
    job_id = layer_data_job.get("jobId")

    # 3. Poll job status and get results
    import time
    if job_id:
        while True:
            status_response = api.get_layer_data_status(job_id)
            if status_response is None:
                print("No status response, try again...")
                time.sleep(2)
                continue
            print("Job Status:", status_response.get("status"))
            if status_response.get("status") == "COMPLETED":
                # Now fetch the result data
                result = api.get_layer_data_result(job_id)
                print("Result:", result)
                break
            elif status_response.get("status") in ("FAILED", "CANCELLED"):
                print("Job Failed or Cancelled")
                break
            time.sleep(2)  # wait before polling again
