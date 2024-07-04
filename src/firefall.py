import json
import os
import requests
import time

from datetime import datetime
from dotenv import load_dotenv

class FirefallService:
    BASE_URL = None
    ENVIRONMENT = None

    def __init__(self, ims_token, environment="prod") -> None:
        if environment not in ["stage", "prod"]:
            raise ValueError("environment must be one of: stage, prod")

        self.ENVIRONMENT = environment
        if environment == "stage":
            self.BASE_URL = "https://firefall-stage.adobe.io"
        elif environment == "prod":
            self.BASE_URL = "https://firefall.adobe.io"

        load_dotenv()
        self.oauth = ims_token
        self.api_key = os.getenv("FIREFALL_API_KEY")
        self.ims_org_id = os.getenv("FIREFALL_IMSS_ORG")

    def completions(
        self,
        session_id,
        prompt,
        max_tokens=4096,
        n=1,
        temperature=1,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        model_name="gpt-35-turbo",
        retry=3
    ) -> str:
        url = f"{self.BASE_URL}/v1/completions"
        headers = {
            "Authorization": self.oauth,
            "accept": "application/json",
            "x-api-key": self.api_key,
            "x-gw-ims-org-id": self.ims_org_id,
            "Content-Type": "application/json",
        }
        data = {
            "dialogue": {"question": prompt},
            "llm_metadata": {
                "llm_type": "azure_chat_openai",
                "model_name": model_name,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "top_p": top_p,
                "frequency_penalty": frequency_penalty,
                "presence_penalty": presence_penalty,
                "n": n,
            },
        }

        try:
            sleep_time = 20
            for i in range(retry):
                # Get the request start time
                request_start = datetime.now().strftime("%Y-%m-%d %H:%M")
                response = requests.post(url, headers=headers, json=data)
                print(response.status_code, response.text)

                # Capture response metrics
                token_usage = response.json()['llm_output']['token_usage']
                request_metrics = {
                    'request_api_key': self.api_key,
                    'request_id': response.json()['query_id'],
                    'request_status': response.status_code,
                    'request_start': request_start,
                    'request_end': datetime.now().strftime("%Y-%m-%d %H:%M"),
                    'request_duration': response.elapsed.total_seconds(),
                    'prompt_tokens': token_usage['prompt_tokens'], 
                    'completion_tokens': token_usage['completion_tokens'], 
                    'total_tokens': token_usage['total_tokens']
                    }
                
                # Log request metrics as an item in a csv
                # If the file is empty or doesn't exist, add the header
                file_name = f'{session_id}-metrics.csv'
                file_path = 'data/session-metrics'

                # If the directory doesn't exist, create it
                if not os.path.exists(file_path):
                    os.makedirs(file_path)

                if not os.path.isfile(f'{file_path}/{file_name}') or os.stat(f'{file_path}/{file_name}').st_size == 0:
                    with open(f'{file_path}/{file_name}', 'w') as f:
                        f.write('request_api_key,request_id,request_status,request_start,request_end,request_duration,prompt_tokens,completion_tokens,total_tokens\n')

                # Write the metrics to the csv
                with open(f'{file_path}/{file_name}', 'a') as f:
                    f.write(f"{request_metrics['request_api_key']},{request_metrics['request_id']},{request_metrics['request_status']},{request_metrics['request_start']},{request_metrics['request_end']},{request_metrics['request_duration']},{request_metrics['prompt_tokens']},{request_metrics['completion_tokens']},{request_metrics['total_tokens']}\n")

                if response.status_code < 200 or response.status_code > 299:
                    print(response.status_code, response.text)
                    print(f"Retrying {i+1}/{retry}...")
                    time.sleep(sleep_time)
                    # increase sleep time exponentially
                    sleep_time *= 2
                else:
                    break

        except Exception as e:
            print(e)
            return "Error: " + str(e)
        return response.json()

    def brand_score(self, brand, text):
        url = f"{self.BASE_URL}/v2/capability/completions"

        headers = {
            "Authorization": "Bearer " + self.oauth,
            "x-api-key": self.api_key,
            "x-gw-ims-org-id": self.ims_org_id,
            "Content-Type": "application/json",
        }

        data = {
            "capability_name": "ccai_brand_alignment_capability",
            "input_type": "json",
            "query": {"brand": brand, "text": text},
        }

        response = requests.post(url, headers=headers, json=data)
        return response.json()

    # 6.1.  Create a Brand
    def create_brand(self, brand_name, description):
        url = f"{self.BASE_URL}/brand"
        headers = {
            "Authorization": self.oauth,
            "x-api-key": self.api_key,
            "x-gw-ims-org-id": self.ims_org_id,
            "x-gw-ims-user-id": "ndere@adobe.com",
            "Content-Type": "application/json",
        }
        data = {"brand_name": brand_name, "description": description}
        response = requests.post(url, headers=headers, json=data)
        return response.json()

    # 6.2.1. Get all Brands
    def get_all_brands(self):
        url = f"{self.BASE_URL}/brand"
        headers = {
            "Authorization": self.oauth,
            "x-api-key": self.api_key,
            "x-gw-ims-org-id": self.ims_org_id,
            "x-gw-ims-user-id": "ndere@adobe.com",
        }
        response = requests.get(url, headers=headers)
        return response.json()

    # 6.2.2. Get Brand byID
    def get_brand_by_id(self, brand_id):
        url = f"{self.BASE_URL}/brand/{brand_id}"
        headers = {
            "Authorization": self.oauth,
            "x-api-key": self.api_key,
            "x-gw-ims-org-id": self.ims_org_id,
        }
        response = requests.get(url, headers=headers)
        return response.json()

    # 6.3.  Edit Brand
    def edit_brand(self, brand_id, description):
        url = f"{self.BASE_URL}/brand/{brand_id}"
        headers = {
            "Authorization": self.oauth,
            "x-api-key": self.api_key,
            "x-gw-ims-org-id": self.ims_org_id,
        }
        data = {"description": description}
        response = requests.patch(url, headers=headers, json=data)
        return response.json()

    # 6.4.  DELETE Brand
    def delete_brand(self, brand_id):
        url = f"{self.BASE_URL}/brand/{brand_id}"
        headers = {
            "Authorization": self.oauth,
            "x-api-key": self.api_key,
            "x-gw-ims-org-id": self.ims_org_id,
        }
        response = requests.delete(url, headers=headers)
        return response.json()

    # 7.1.1.  Create an Entry
    def create_asset(self, brand_id, asset_type, asset_label):
        url = f"{self.BASE_URL}/brand/{brand_id}/asset"
        headers = {
            "Authorization": self.oauth,
            "x-api-key": self.api_key,
            "x-gw-ims-org-id": self.ims_org_id,
            "Content-Type": "application/json",
        }
        data = {
            "asset_type": asset_type,
            "asset_label": asset_label,
        }
        response = requests.post(url, headers=headers, json=data)
        print(response.headers)
        return response.json()

    # 7.2.1.  Get All Assets
    def get_all_assets(self, brand_id):
        url = f"{self.BASE_URL}/brand/{brand_id}/asset"
        headers = {
            "Authorization": self.oauth,
            "x-api-key": self.api_key,
            "x-gw-ims-org-id": self.ims_org_id,
        }
        response = requests.get(url, headers=headers)
        return response.json()

    # 7.1.2. Upload Asset Directly to URI
    def upload_asset(self, uplaod_uri, path_to_asset):
        headers = {"Content-Type": "application/json"}
        with open(path_to_asset, "rb") as file:
            response = requests.put(uplaod_uri, headers=headers, data=file)
            print(response.status_code, response.text)
        return response

    # 7.2.1.  Get All Assets
    def get_asset_by_id(self, brand_id, asset_id):
        url = f"{self.BASE_URL}/brand/{brand_id}/asset/{asset_id}"
        headers = {
            "Authorization": self.oauth,
            "x-api-key": self.api_key,
            "x-gw-ims-org-id": self.ims_org_id,
        }
        response = requests.get(url, headers=headers)
        return response.json()

    # 7.3.  Delete Asset
    def delete_asset(self, brand_id, asset_id):
        url = f"{self.BASE_URL}/brand/{brand_id}/asset/{asset_id}"
        headers = {
            "Authorization": self.oauth,
            "x-api-key": self.api_key,
            "x-gw-ims-org-id": self.ims_org_id,
        }
        response = requests.delete(url, headers=headers)
        return response.json()

    # 8.1.  Create BrandDNA With Assets
    def create_brand_dna_with_assets(self, brand_id, brand_dna_label, list_asset_ids):
        url = f"{self.BASE_URL}/brand/{brand_id}/brand_dna/generate"
        headers = {
            "Authorization": self.oauth,
            "x-api-key": self.api_key,
            "x-gw-ims-org-id": self.ims_org_id,
            "Content-Type": "application/json",
        }
        data = {
            "brand_dna_label": brand_dna_label,
            "asset_ids": list_asset_ids,
        }
        response = requests.get(url, headers=headers, json=data)
        return response.json()

    # 8.2.  Create Brand DNA Without Assets
    def create_brand_dna(self, brand_id, brand_dna_label, brand_dna):
        url = f"{self.BASE_URL}/brand/{brand_id}/brand_dna"
        headers = {
            "Authorization": self.oauth,
            "x-api-key": self.api_key,
            "x-gw-ims-org-id": self.ims_org_id,
            "Content-Type": "application/json",
        }
        data = {
            "brand_dna_label": brand_dna_label,
            "brand_dna": brand_dna,
        }
        response = requests.post(url, headers=headers, json=data)
        print(data)
        return response.json()

    # 8.3.1.  GET ALL Brand DNAs
    def get_all_brand_dnas(self, brand_id):
        url = f"{self.BASE_URL}/brand/{brand_id}/brand_dna"
        headers = {
            "Authorization": self.oauth,
            "x-api-key": self.api_key,
            "x-gw-ims-org-id": self.ims_org_id,
            "Content-Type": "application/json",
        }
        response = requests.get(url, headers=headers)
        return response.json()

    # 10. Brand Aware Content
    # 10.1.  Create Content
    def create_content(
        self, brand_id, brand_dna_id, brand_content_label, brand_dna_keys, prompt
    ):
        url = f"{self.BASE_URL}/brand/{brand_id}/brand_content"
        headers = {
            "Authorization": self.oauth,
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
            "x-gw-ims-org-id": self.ims_org_id,
        }
        data = {
            "brand_content_label": brand_content_label,
            "brand_dna_id": brand_dna_id,
            "brand_dna_keys": brand_dna_keys,
            "user_prompt": prompt,
            "llm_metadata": {
                "llm_type": "azure_chat_openai",
                "model_name": "gpt-4",  # "gpt-35-turbo"
                "temperature": 0.5,
            },
        }
        response = requests.post(url, headers=headers, json=data)
        return response.json()

    # 10.2.2.  Get BrandContent ByID
    def get_brand_content_by_id(self, brand_id, brand_content_id):
        url = f"{self.BASE_URL}/brand/{brand_id}/brand_content/{brand_content_id}"
        headers = {
            "Authorization": self.oauth,
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
            "x-gw-ims-org-id": self.ims_org_id,
        }
        response = requests.get(url, headers=headers)
        return response.json()

    # 10.5. Get Brand Content Confidence
    def get_brand_content_confidence(self, brand_id, brand_content_id):
        url = f"{self.BASE_URL}/brand/{brand_id}/brand_content/{brand_content_id}/confidence"
        headers = {
            "Authorization": self.oauth,
            "x-api-key": self.api_key,
            "x-gw-ims-org-id": self.ims_org_id,
        }
        response = requests.post(url, headers=headers)
        return response.json()
    
    def test(self, prompt="Say Hello in a made-up language. Then briefly explain what you said."):
        print(f'Test prompt: {prompt}')
        session_id = 'test'
        response = self.completions(session_id, prompt, max_tokens=4000)
        print(f'Test response: {json.dumps(response["generations"][0][0]["text"], indent=2)}')
