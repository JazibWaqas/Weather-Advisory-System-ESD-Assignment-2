import grpc
import os
import time
from concurrent import futures
import spec_pb2
import spec_pb2_grpc
from openweather.api.default_api import DefaultApi
from openweather.api_client import ApiClient

def get_air_quality(request, context):
    city = request.city or ""
    print(f"getting air quality for {city}")
    
    api_key = os.environ.get("OPENWEATHER_API_KEY")
    if not api_key:
        context.abort(grpc.StatusCode.INTERNAL, "OPENWEATHER_API_KEY is not set")
    
    with ApiClient() as client:
        api = DefaultApi(client)
        results = api.geo10_direct_get(q=city, appid=api_key, limit=1)
        if not results:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, f"City not found: {city}")
        
        first = results[0]
        lat = float(first.lat)
        lon = float(first.lon)
        
        air = api.data25_air_pollution_get(lat=lat, lon=lon, appid=api_key)
        aqi = int(air.list[0].main.aqi) if air.list and air.list[0].main and air.list[0].main.aqi is not None else 0
        
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
        
        message = f"AQI {aqi} - {quality}"
        return spec_pb2.AirQualityResponse(city=city, air_quality=quality, message=message)

def kelvin_to_celsius(temp_k):
    return float(temp_k) - 273.15

def get_weather(request, context):
    city = request.city or ""
    print(f"getting weather for {city}")
    
    api_key = os.environ.get("OPENWEATHER_API_KEY")
    if not api_key:
        context.abort(grpc.StatusCode.INTERNAL, "OPENWEATHER_API_KEY is not set")
    
    with ApiClient() as client:
        api = DefaultApi(client)
        data = api.data25_weather_get(q=city, appid=api_key)
        temp_k = float(data.main.temp) if data.main and data.main.temp is not None else 273.15
        temp_c = kelvin_to_celsius(temp_k)
        description = data.weather[0].description if data.weather else ""
        return spec_pb2.WeatherResponse(city=city, temperature=temp_c, description=description)

def get_travel_recommendation(request, context):
    city = request.city or ""
    print(f"getting travel for {city}")
    
    api_key = os.environ.get("OPENWEATHER_API_KEY")
    if not api_key:
        context.abort(grpc.StatusCode.INTERNAL, "OPENWEATHER_API_KEY is not set")
    
    with ApiClient() as client:
        api = DefaultApi(client)
        fc = api.data25_forecast_get(q=city, appid=api_key)
        if not fc.list:
            context.abort(grpc.StatusCode.INTERNAL, "No forecast data")
        
        feels_like_k = float(fc.list[0].main.feels_like) if fc.list[0].main and fc.list[0].main.feels_like is not None else 273.15
        feels_like_c = kelvin_to_celsius(feels_like_k)
        
        if feels_like_c < 15:
            rec = "It's chilly, consider wearing a jacket"
        elif feels_like_c > 30:
            rec = "It's hot, consider wearing sunscreen"
        else:
            rec = "It's perfect, no need to bring an umbrella"
        
        return spec_pb2.TravelRecommendationResponse(city=city, recommendation=rec)

class WeatherServicer(spec_pb2_grpc.WeatherAdvisoryServicer):
    def GetAirQuality(self, request, context):
        return get_air_quality(request, context)
    
    def GetWeather(self, request, context):
        return get_weather(request, context)
    
    def GetTravelRecommendation(self, request, context):
        return get_travel_recommendation(request, context)

def main():
    port = os.getenv('SERVER_PORT', '9999')
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    
    spec_pb2_grpc.add_WeatherAdvisoryServicer_to_server(WeatherServicer(), server)
    
    addr = f'127.0.0.1:{port}'
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