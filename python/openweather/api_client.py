import requests
from typing import Optional

class ApiClient:
    def __init__(self, configuration=None):
        self.configuration = configuration or {}
        self.session = requests.Session()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()
    
    def request(self, method, url, **kwargs):
        return self.session.request(method, url, **kwargs)
