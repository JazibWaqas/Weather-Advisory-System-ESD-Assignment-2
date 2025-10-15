import requests
from typing import List, Dict, Any, Optional

class WeatherData:
    def __init__(self, data):
        self.main = MainData(data.get('main', {}))
        self.weather = [WeatherItem(w) for w in data.get('weather', [])]

class MainData:
    def __init__(self, data):
        self.temp = data.get('temp')
        self.feels_like = data.get('feels_like')

class WeatherItem:
    def __init__(self, data):
        self.description = data.get('description', '')

class AirPollutionData:
    def __init__(self, data):
        self.list = [AirPollutionItem(item) for item in data.get('list', [])]

class AirPollutionItem:
    def __init__(self, data):
        self.main = MainAQI(data.get('main', {}))

class MainAQI:
    def __init__(self, data):
        self.aqi = data.get('aqi')

class ForecastData:
    def __init__(self, data):
        self.list = [ForecastItem(item) for item in data.get('list', [])]

class ForecastItem:
    def __init__(self, data):
        self.main = MainData(data.get('main', {}))

class GeocodeResult:
    def __init__(self, data):
        self.lat = data.get('lat')
        self.lon = data.get('lon')

class DefaultApi:
    def __init__(self, api_client=None):
        self.api_client = api_client
        self.base_url = "https://api.openweathermap.org"
    
    def data25_weather_get(self, q: str, appid: str) -> WeatherData:
        url = f"{self.base_url}/data/2.5/weather"
        params = {'q': q, 'appid': appid}
        response = requests.get(url, params=params)
        response.raise_for_status()
        return WeatherData(response.json())
    
    def data25_forecast_get(self, q: str, appid: str) -> ForecastData:
        url = f"{self.base_url}/data/2.5/forecast"
        params = {'q': q, 'appid': appid}
        response = requests.get(url, params=params)
        response.raise_for_status()
        return ForecastData(response.json())
    
    def data25_air_pollution_get(self, lat: float, lon: float, appid: str) -> AirPollutionData:
        url = f"{self.base_url}/data/2.5/air_pollution"
        params = {'lat': lat, 'lon': lon, 'appid': appid}
        response = requests.get(url, params=params)
        response.raise_for_status()
        return AirPollutionData(response.json())
    
    def geo10_direct_get(self, q: str, appid: str, limit: int = 1) -> List[GeocodeResult]:
        url = f"{self.base_url}/geo/1.0/direct"
        params = {'q': q, 'appid': appid, 'limit': limit}
        response = requests.get(url, params=params)
        response.raise_for_status()
        return [GeocodeResult(item) for item in response.json()]
