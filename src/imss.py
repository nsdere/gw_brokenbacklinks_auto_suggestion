import os
import requests

from dotenv import load_dotenv

class IMSService:
    
    ENVIRONMENT = None
    ACCESS_TOKEN = None
    ENDPOINT = None
    
    def __init__(self, environment='stage') -> None:
        load_dotenv()
        if environment not in ['stage', 'prod']:
            raise ValueError('environment must be one of: stage, prod')
    
        self.ENVIRONMENT = environment
        if environment == 'stage':
            self.ENDPOINT = 'https://ims-na1-stg1.adobelogin.com'
            imss_client_id = 'aem-generate-variations'
            imss_client_secret = os.getenv('IMSS_CLIENT_SECRET_STAGE')
            imss_service_permanent_authorization_code = os.getenv('IMSS_SERVICE_PERMANENT_AUTHORIZATION_CODE_STAGE')
        elif environment == 'prod':
            self.ENDPOINT = 'https://ims-na1.adobelogin.com'
            imss_client_id = 'aem-sidekick-genai-assistant'
            imss_client_secret = os.getenv('IMSS_CLIENT_SECRET_PROD')
            imss_service_permanent_authorization_code = os.getenv('IMSS_SERVICE_PERMANENT_AUTHORIZATION_CODE_PROD')

        url = f"{self.ENDPOINT}/ims/token/v1"
        # Request an access token from IMSS
        imss_access_token_response = requests.post(
            url,
            data = {
                'client_id': imss_client_id,
                'client_secret': imss_client_secret,
                'grant_type': 'authorization_code',
                'code': imss_service_permanent_authorization_code
            }
        )
        print(imss_access_token_response)
        self.ACCESS_TOKEN = imss_access_token_response.json()['access_token']
