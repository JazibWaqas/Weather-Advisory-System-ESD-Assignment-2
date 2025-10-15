import grpc
import spec_pb2
import spec_pb2_grpc


def test_weather_service():
    channel = grpc.insecure_channel('localhost:9999')
    stub = spec_pb2_grpc.WeatherAdvisoryStub(channel)
    
    print("Testing air quality...")
    air_req = spec_pb2.AirQualityRequest(city="New York")
    air_resp = stub.GetAirQuality(air_req)
    print(f"Air Quality: {air_resp.air_quality} - {air_resp.message}")
    
    print("\nTesting weather...")
    weather_req = spec_pb2.WeatherRequest(city="New York")
    weather_resp = stub.GetWeather(weather_req)
    print(f"Weather: {weather_resp.temperature}°C, {weather_resp.description}")
    
    print("\nTesting travel recommendation...")
    travel_req = spec_pb2.TravelRequest(city="New York")
    travel_resp = stub.GetTravelRecommendation(travel_req)
    print(f"Travel: {travel_resp.recommendation}")


if __name__ == '__main__':
    test_weather_service()