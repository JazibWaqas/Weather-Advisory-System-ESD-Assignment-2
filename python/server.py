import grpc
import requests
import os
from concurrent import futures
import time
import spec_pb2
import spec_pb2_grpc

api_key = '8e7b073df463f91111e4bd3d6901dc0b'

def get_air_quality(request, context):
    city = request.city
    print(f"getting air quality for {city}")
    
    geo_url = "https://api.openweathermap.org/geo/1.0/direct"
    geo_resp = requests.get(geo_url, params={'q': city, 'limit': 1, 'appid': api_key})
    
    if geo_resp.status_code != 200:
        air_quality = "Unknown"
        message = "city not found"
        return spec_pb2.AirQualityResponse(city=city, air_quality=air_quality, message=message)
    
    geo_data = geo_resp.json()
    if not geo_data:
        air_quality = "Unknown"
        message = "city not found"
        return spec_pb2.AirQualityResponse(city=city, air_quality=air_quality, message=message)
    
    lat = geo_data[0]['lat']
    lon = geo_data[0]['lon']
    
    air_url = "https://api.openweathermap.org/data/2.5/air_pollution"
    air_resp = requests.get(air_url, params={'lat': lat, 'lon': lon, 'appid': api_key})
    
    if air_resp.status_code != 200:
        air_quality = "Unknown"
        message = "cant get air data"
        return spec_pb2.AirQualityResponse(city=city, air_quality=air_quality, message=message)
    
    air_data = air_resp.json()
    aqi = air_data['list'][0]['main']['aqi']
    
    if aqi == 1:
        quality = "Good"
    elif aqi == 2:
        quality = "Fair"
    elif aqi == 3:
        quality = "Moderate"
    elif aqi == 4:
        quality = "Poor"
    else:
        quality = "Very Poor"
    
    message = f"air quality is {quality.lower()}"
    return spec_pb2.AirQualityResponse(city=city, air_quality=quality, message=message)

def get_weather(request, context):
    city = request.city
    print(f"getting weather for {city}")
    
    weather_url = "https://api.openweathermap.org/data/2.5/weather"
    resp = requests.get(weather_url, params={'q': city, 'appid': api_key, 'units': 'metric'})
    
    if resp.status_code != 200:
        temperature = 0.0
        description = "unknown"
        return spec_pb2.WeatherResponse(city=city, temperature=temperature, description=description)
    
    data = resp.json()
    temp = data['main']['temp']
    desc = data['weather'][0]['description']
    
    return spec_pb2.WeatherResponse(city=city, temperature=temp, description=desc)

def get_travel_recommendation(request, context):
    city = request.city
    print(f"getting travel for {city}")
    
    forecast_url = "https://api.openweathermap.org/data/2.5/forecast"
    resp = requests.get(forecast_url, params={'q': city, 'appid': api_key, 'units': 'metric'})
    
    if resp.status_code != 200:
        recommendation = "cant get forecast"
        return spec_pb2.TravelRecommendationResponse(city=city, recommendation=recommendation)
    
    data = resp.json()
    temp = data['list'][0]['main']['feels_like']
    
    if temp < 15:
        rec = "It's chilly, consider wearing a jacket"
    elif temp > 30:
        rec = "It's hot, consider wearing sunscreen"
    else:
        rec = "It's perfect, no need to bring an umbrella"
    
    return spec_pb2.TravelRecommendationResponse(city=city, recommendation=rec)

def main():
    port = os.getenv('SERVER_PORT', '8888')
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    
    class SimpleServicer(spec_pb2_grpc.WeatherAdvisoryServicer):
        def GetAirQuality(self, request, context):
            return get_air_quality(request, context)
        def GetWeather(self, request, context):
            return get_weather(request, context)
        def GetTravelRecommendation(self, request, context):
            return get_travel_recommendation(request, context)
    
    spec_pb2_grpc.add_WeatherAdvisoryServicer_to_server(SimpleServicer(), server)
    
    addr = f'0.0.0.0:{port}'
    server.add_insecure_port(addr)
    print(f"server starting on {addr}")
    
    server.start()
    
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    main()