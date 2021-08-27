import os
import json
import requests


class HuggingfaceApp():
    def __init__(self, api_url, model_name, huggingface_token):
        """Class for utilizing hunggingface api
        """
        self.api_endpoint = api_url + model_name
        self.request_headers = {
            'Authorization': 'Bearer {}'.format(huggingface_token)
        }

    def query(self, payload):
        """
        make request to the Hugging Face model API
        """
        data = json.dumps(payload)
        response = requests.request('POST',
                                    self.api_endpoint,
                                    headers=self.request_headers,
                                    data=data)
        ret = json.loads(response.content.decode('utf-8'))
        return ret  # return a string i think
