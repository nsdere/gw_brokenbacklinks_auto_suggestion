import json
import requests
from dotenv import load_dotenv

EMERALD_SERVICE_URL = 'https://emerald-stage.adobe.io'
FIREFALL_URL = "https://firefall-stage.adobe.io"

class EmeraldService:
    def __init__(self, token):
        
        load_dotenv()
        self.token = token
        self.ims_client_id =  'aem-generate-variations'
        self.ims_org_id =  'ndere@adobe.com'


        self.default_headers = {'Authorization': f'Bearer {self.token}',
                                'x-api-key': self.ims_client_id,
                                'x-gw-ims-org-id': self.ims_org_id,
                                'Content-Type': 'application/json'}
        
    def split_to_chunks(self, ls, n=10):
        """
        Return a list of chunks, where each chunk is a list of at most n elements.
        The output list contains the exact same elements in the exact same order, but instead expressed as a list of lists.
        E.g. ls = [1,2,3,4,5,6,7], max_size = 2 -> [[1,2], [3,4], [5,6], [7]]
        """
        return [ls[i:i+n] for i in range(0, len(ls), n)]
    
    def get_all_embedders(self):
        """
        Return a list of available embedders
        """
        url = f'{EMERALD_SERVICE_URL}/embedder'
        response = requests.request("GET", url, headers=self.default_headers)
        response.raise_for_status()
        return response.json()
    
    def get_adhoc_text_embedding(self, text, input_format="text", embedder="openai-embedder"):
        """
        Return an embedding vector for a given input string.
        This method is used to acquire text embedding vectors 'adhoc' without the need
        to create collections or assets.
        """
        url = f"{EMERALD_SERVICE_URL}/embedding"
        payload = {
            "embedder_id": embedder,
            "asset_type": "text",
            "input_format": input_format,
            "data": text
        }
        response = requests.request("POST", url, headers=self.default_headers, data=json.dumps(payload))
        response.raise_for_status()
        return response.json()

    def get_all_collections(self):
        """
        Return a list of available collections
        """  
        url = f'{EMERALD_SERVICE_URL}/collection'
        response = requests.request("GET", url, headers=self.default_headers)
        response.raise_for_status()
        return response.json()

    def create_collection(self, collection_name, embedder="openai-embedder"):
        url = f"{EMERALD_SERVICE_URL}/collection"
        payload = {
            "collection_name": collection_name,
            "asset_type": "text",
            "embedder_id": embedder
        }
        response = requests.request("POST", url, headers=self.default_headers, data=json.dumps(payload))
        response.raise_for_status()
        return response.json(), response.headers
    
    def create_collection_from_url(self, collection_name, embedder="openai-embedder"):
        url = f"{EMERALD_SERVICE_URL}/collection"
        payload = {
            "collection_name": collection_name,
            "asset_type": "text",
            "input_format" : "url",
            "embedder_id": embedder
        }
        response = requests.request("POST", url, headers=self.default_headers, data=json.dumps(payload))
        response.raise_for_status()
        return response.json(), response.headers
    
    def create_collection_if_not_exists(self, collection_name, *args, **kwargs):
        """
        Check if collection exists, if not, create it.
        Return the creation response if collection was created, otherwise returns None.
        """
        if not self.collection_exists(collection_name):
            return self.create_collection(collection_name, *args, **kwargs)
        else:
            return None

    def get_collection_info(self, collection_name):
        """
        Return info about a given collection
        """
        url = f'{EMERALD_SERVICE_URL}/collection/{collection_name}'
        response = requests.request("GET", url, headers=self.default_headers)
        response.raise_for_status()
        return response.json()
    
    def collection_exists(self, collection_name) -> bool:
        """
        Return True if a collection of a given name exists, otherwise return False
        """
        try:
            self.get_collection_info(collection_name) # API returns a 404 error if a given collection doesn't exist
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                return False
            else:
                raise Exception('An unhandled error has occurred')
        else:
            return True

    def delete_collection(self, collection_name):
        """
        Deletes a given collection
        """
        url = f'{EMERALD_SERVICE_URL}/collection/{collection_name}'
        response = requests.delete(url, headers=self.default_headers)
        response.raise_for_status()

    def split_to_chunks(self, ls, n):
        """
        Return a list of chunks, where each chunk is a list of at most n elements.
        The output list contains the exact same elements in the exact same order, but instead expressed as a list of lists.
        E.g. ls = [1,2,3,4,5,6,7], max_size = 2 -> [[1,2], [3,4], [5,6], [7]]
        """
        return [ls[i:i+n] for i in range(0, len(ls), n)]

    """ def add_assets(self, collection_name, assets, max_chunk_size):
        assert type(assets) == list
        responses = []
        asset_chunks = self.split_to_chunks(assets, n=max_chunk_size)
        with Bar('Uploading', max=len(asset_chunks)) as bar:
            for assets_chunk in asset_chunks:
                print(assets_chunk)
                url = f"{EMERALD_SERVICE_URL}/collection/{collection_name}/asset"
                payload = assets_chunk
                response = requests.request("POST", url, headers=self.default_headers, data=json.dumps(payload))
                response.raise_for_status()
                responses.append((response.json(), response.headers))
                bar.next()
        return responses """

    def get_asset(self, collection_name, asset_id):
        """
        Return info about a given asset
        """
        url = f'{EMERALD_SERVICE_URL}/collection/{collection_name}/asset/{asset_id}'
        response = requests.request("GET", url, headers=self.default_headers)
        response.raise_for_status()
        return response.json()
        
    def get_all_assets_in_collection(self, collection_name):
        """
        Return a list of all current assets in a collection
        """
        url = f'{EMERALD_SERVICE_URL}/collection/{collection_name}/asset'
        response = requests.request("GET", url, headers=self.default_headers)
        response.raise_for_status()
        return response.json()
        
    def delete_asset(self, collection_name, asset_id):
        """
        Delete an asset with a given id
        """
        url = f'{EMERALD_SERVICE_URL}/collection/{collection_name}/asset/{asset_id}'
        response = requests.delete(url, headers=self.default_headers)
        response.raise_for_status()

    def add_assets_to_collection(self, collection_name, assets):
        try:
            url = f"{EMERALD_SERVICE_URL}/collection/{collection_name}/asset"

            payload = assets

            response = requests.request("POST", url, headers=self.default_headers, data=json.dumps(payload))

            resp_json = response.json()
            print(resp_json)
            return resp_json, response.headers
        except Exception as e:
            print(e)
            return "Error"
        

    def add_assets_to_collection_async(self, collection_name, assets):
        try:
            url = f"{EMERALD_SERVICE_URL}/collection/{collection_name}/asset/job?override=True"

            payload = assets

            response = requests.request("POST", url, headers=self.default_headers, data=json.dumps(payload))

            resp_json = response.json()
            print(resp_json)
            return resp_json, response.headers
        except Exception as e:
            print(e)
            return "Error"
        
    def get_job_status(self, job_id):
        try:
            url = f"{EMERALD_SERVICE_URL}/async/job/{job_id}"

            response = requests.request("GET", url, headers=self.default_headers)

            resp_json = response.json()
            return resp_json
        except Exception as e:
            print(e)
            return "Error"
        
        
    def similarity_search(self, collection_name, query):
        try:
            url = f"{EMERALD_SERVICE_URL}/collection/{collection_name}/search?include_asset=true"

            search_payload = {
                            "data": query,
                            "input_format": "text",
                            "top_n": 3
                        }
            
            response = requests.request("POST", url, headers=self.default_headers, data=json.dumps(search_payload))

            resp_json = response.json()
            return resp_json
        except Exception as e:
            print(e)
            return "Error"
