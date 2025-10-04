# Building a Weather Advisory Service with gRPC and OpenAPI

## Why Are You Doing This Project?

This project is designed to give you hands-on experience with gRPC and OpenAPI, two powerful tools for modern API development and communication. You will learn how to:

- Generate and work with gRPC server stubs and OpenAPI SDKs.
- Implement a gRPC server that proxies requests to an OpenAPI-based service.
- Integrate third-party APIs into your applications.

By the end, you'll have practical knowledge of using gRPC for efficient communication and OpenAPI for leveraging third-party APIs.

## Motivation

Imagine you're building a service to help people make informed travel and outdoor activity decisions. Your service will answer two critical questions:

- Is the air quality safe to breathe?
- Is the temperature within a comfortable range for travel?

You'll achieve this by creating a proxy service that integrates with the OpenWeatherMap API to fetch real-time weather and air quality data. Your gRPC server will process this data and provide meaningful recommendations to clients.

## Instructions to Get Your OpenWeatherMap API Key

- Visit the OpenWeatherMap [Sign-Up Page](https://home.openweathermap.org/users/sign_up).
- Create a free account by entering your details and verifying your email address.
- Once logged in, go to the [API Keys](https://home.openweathermap.org/api_keys) section.
- Generate a new API key and note it down. You'll use this key to authenticate your requests.

💡 Tip: The free plan provides enough access for this project but has a rate limit of 60 API calls per minute.

Note: It takes couple of hours for your API key to be active. Once it is active, you can start working on `Talking with OpenWeatherMap API` part of the assignment.

## Generating gRPC Server Stubs (2 points)

- Go to https://grpc.io/docs/languages/ and pick the link for your preferred programming language.
- Install [protoc](https://grpc.io/docs/protoc-installation/) and any language specific tools.
- Ask ChatGPT to generate the command to compile [spec.proto](./spec.proto) file.
- For Go, the command is:

```bash
cd go/pb
protoc --go_out=. --go_opt=paths=source_relative --go-grpc_out=. --go-grpc_opt=paths=source_relative ../../spec.proto --proto_path=../../
```

There may be slight variations depending on the language you choose. Figuring it out is part of the assignment.

Putting code in `pb` directory is not a strict requirement. You can put it elsewhere if the language you pick requires it.

## Creating First gRPC Server (2 points)

Based on what got generated above, you are to implement a server. GRPC server is usually made by extending a generated interface and overriding the methods. You can find the generated interface in the code generated above. Follow the language specific instructions to implement the server.

For the first version, just return some dummy data to the client. For example, in Go, you could have returned these:

```go
func (s *server) GetAirQuality(context.Context, *pb.AirQualityRequest) (*pb.AirQualityResponse, error) {
	return &pb.AirQualityResponse{
		City:       "New York",
		AirQuality: "Good",
		Message:    "Air quality is good",
	}, nil
}

func (s *server) GetTravelRecommendation(context.Context, *pb.TravelRequest) (*pb.TravelRecommendationResponse, error) {
	return &pb.TravelRecommendationResponse{
		City:           "New York",
		Recommendation: "Visit",
	}, nil
}

func (s *server) GetWeather(context.Context, *pb.WeatherRequest) (*pb.WeatherResponse, error) {
	return &pb.WeatherResponse{
		City:        "New York",
		Temperature: 25.0,
		Description: "Sunny",
	}, nil
}
```

Once you are done, run the server on port `9999` and make sure it works by using the provided client binary in `tools/client` directory.:

```bash
./client-windows-amd64.exe air-quality -city "New York"
./client-windows-amd64.exe travel -city "New York"
./client-windows-amd64.exe weather -city "New York"
```

You may override the server port by setting the `SERVER_PORT` environment variable.

Example:

```bash
SERVER_PORT=8888 ./client-windows-amd64.exe air-quality -city "New York"
```

## Creating OpenAPI SDK (2 points)

We will use OpenAPI SDK to call the OpenWeatherMap API. We will use [OpenAPI Generator ](https://github.com/OpenAPITools/openapi-generator) to generate the SDK. There are multiple ways to use openapi generator. Easiest is to ensure you have Docker Desktop installed and run a command similar to the following command:

```bash
docker run --rm -v $(pwd):/local openapitools/openapi-generator-cli generate -g go -i /local/openapi.yaml -o /local/go/openweather --additional-properties=packageName=openweather,withGoMod=false
```

You can see docs for generator specific options here: https://github.com/OpenAPITools/openapi-generator/tree/master/docs/generators

Language specific options can be passed to the generator in additional-properties as shown above.

## Talking with OpenWeatherMap API

1. Change the dummy server implementation to use the real OpenWeatherMap API via SDK that we generated above.
2. The server must respect `SERVER_PORT` environment variable with default value of `9999` and listen on localhost.
3. The server must respect `OPENWEATHER_API_KEY` environment variable and use this key to make requests to OpenWeatherMap API.

### GetAirQuality (1 point)

As can be seen in the [openapi spec](./openapi.yaml), the air quality can be fetched by calling `/data/2.5/air_pollution` endpoint with the following parameters:

- `lat`: latitude of the location
- `lon`: longitude of the location
- `appid`: API key

But the client sends city in the `AirQualityRequest` message. So you will need to convert the city name to latitude and longitude.

To convert the city name to latitude and longitude, you can use the OpenWeatherMap Geocoding API. The endpoint is `/geo/1.0/direct` and the parameters are:

- `q`: city name
- `appid`: API key
- `limit`: maximum number of results (default 5)

You can set limit to 1, as we only need the first result. Response will give you lat and lon. Pass those to `data/2.5/air_pollution` endpoint.

Finally, from air_pollution response, use `list[0].main.aqi` to get the air quality index and map it to a description.

Here is AQI table for mapping AQI to description:

|Description | AQI Score|
-----|------
| Good | 1 |
| Fair | 2 |
| Moderate | 3 |
| Poor | 4 |
| Very Poor | >=5 |

Finally return `AirQualityResponse` to the client.

You can play with this endpoint by checking AQI at https://www.iqair.com/world-air-quality-ranking and passing related names to the client.

Here are some examples (run server in a separate terminal, on port 9999):

```bash
./tools/client/client-windows-amd64.exe air-quality -city "Blacksburg"

./tools/client/client-windows-amd64.exe air-quality -city "Wuhan"
```

### GetWeather (1 point)

As can be seen in the [spec](./openapi.yaml), The weather can be fetched by calling `/data/2.5/weather` endpoint with the following parameters:

- `q`: city name
- `appid`: API key

There are two keys in the response that will give us the data we need.

- `main.temp`: temperature in Kelvin
- `weather[0].description`: description of the weather

You will need to convert the temperature from Kelvin to Celcius before returning it to the client.

Try it:

```bash
./tools/client/client-windows-amd64.exe weather -city "Blacksburg"
```

### GetTravelRecommendation (1 point)

As can be seen in the (spec)[./openapi.yaml], The travel recommendation can be fetched by calling /data/2.5/forecast endpoint with the following parameters:

- `q`: city name
- `appid`: API key


From response's list of forecasts, you will need to get the first forecast (`list[0].main`) and get the temperature from the `feels_like` field. You will need to convert the temperature from Kelvin to Celcius.

From celsius to recommendation, you can use the following table:

| Description | Temperature Range |
--------------|-------------------
| It's chilly, consider wearing a jacket | < 15 |
| It's hot, consider wearing sunscreen | > 30 |
| It's perfect, no need to bring an umbrella | 15 <= temp <= 30 |

Finally return the recommendation to the client.

Try it:

```bash
./tools/client/client-windows-amd64.exe travel -city "Blacksburg"
./tools/client/client-windows-amd64.exe travel -city "Karachi"
```

## Documentation

Since the you pick the programming language of server, you have to document how to run the solution. Add that documentation to the below section.

# Running the Solution (1 point)

**How to run the Python server:**

1. Start the server:
   ```bash
   cd python
   python server.py
   ```

2. Test quickly (in new terminal):
   ```bash
   cd python
   python testing.py
   ```

# Testing the Solution

In terminal A:

- `export OPENWEATHER_API_KEY=your_api_key`
- `export SERVER_PORT=9999`
- Start the provided server. Example: `./tools/server/server-windows-amd64.exe`

In terminal B:
- Use the provided client to interact with the server you just started.

In terminal A:
- Stop the provided server (Press Ctrl+C)
- Start the server you implemented

In terminal B:
- Use the provided client to interact with the server you just started.

If the output matches the output of the provided server, you are done. Commit and push all of your code.

# FAQs

1. Can I use AI?

    Yes and No. You may use AI to ask it general questions like "How do I generate grpc server stub for Rust?" and "How do I generate openapi sdk for Rust?". Or you may ask AI to show you a hello world gRPC server for Rust.

    You may not use AI to generate the code for the project. You must write the code by yourself.

2. How would you know I used AI to generate the solution?

    I will put this project's instructions on AI prompt and ask it to generate the code for the project in various different ways. If any of that matches what you did, then you are using AI.

3. Can I ask friends if I run into problems?

    No, you will use Canvas Discussions to ask questions and your friends may answer there. If two code bases are too similar, you will get a penalty.

4. Can I use Go?

    No but you may use Go as a reference. You can pick any other supported language from [grpc website.](https://grpc.io/docs/languages/)

5. Can I use another SDK?

    No, only use openapi generator to generate the code. You can install it any way you want, docker is not required.