from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, redirect
import requests
from datetime import datetime
from dotenv import load_dotenv
import os
# Create your views here.



def search_weather(request):
    city = request.GET.get("city", "").strip()

    if city:
        return redirect("city_weather", city=city)

    return render(request, "search.html")

def city_weather(request, city):


    url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=10&language=en&format=json"
    response = requests.get(url).json()

    if not response.get('results'):
        return render(request, "error.html", {
            "error": f"No results found"
        })

    lat = response["results"][0]["latitude"]
    lon = response["results"][0]["longitude"]
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": ["temperature_2m", 'precipitation_probability'],
        "daily": ["sunrise", "sunset", 'precipitation_probability_max'],
        "current": ["temperature_2m","weather_code", "apparent_temperature", "is_day", "relative_humidity_2m", "precipitation", "rain",
                    "wind_speed_10m", "wind_direction_10m"],
        "timezone": "Europe/Sofia"
    }

    forecast_url = "https://api.open-meteo.com/v1/forecast"
    air_quality_url = f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={lat}&longitude={lon}&current=european_aqi"
    air_quality_json = requests.get(air_quality_url).json()

    air_quality_index = air_quality_json["current"]['european_aqi']

    if 0 <= air_quality_index <= 20:
        air_quality = "Good"
    elif 20 < air_quality_index <= 40:
        air_quality = "Fair"
    elif 40 < air_quality_index <= 60:
        air_quality = "Moderate"
    elif 60 < air_quality_index <= 80:
        air_quality = "Poor"
    elif 80 < air_quality_index <= 100:
        air_quality = "Very Poor"
    else:
        air_quality = "Extremely Poor"


    forecast_response = requests.get(forecast_url, params=params).json()

    print(forecast_response["current"])


    #hourly stuff
    hours = forecast_response["hourly"]["time"]
    temps = forecast_response["hourly"]['temperature_2m']
    rain_probability = forecast_response['hourly']['precipitation_probability']

    future_hours = []
    future_temps = []
    future_rain_probability = []


    for h, temp, rain_prob in zip(hours, temps, rain_probability):
        dt = datetime.fromisoformat(h)
        if dt >= datetime.now():
            future_hours.append(dt.strftime("%I %p"))
            future_temps.append(temp)
            future_rain_probability.append(rain_prob)

    hourly_forecast = [{"time": t, "temp": temp, "rain_chance": rain_prob} for t, temp, rain_prob in zip(future_hours[:24], future_temps[:24], future_rain_probability[:24])]

    sunset_iso = forecast_response['daily']['sunset'][0]
    sunset_time = datetime.fromisoformat(sunset_iso).strftime("%H:%M")

    sunrise_iso = forecast_response['daily']['sunrise'][0]
    sunrise_time = datetime.fromisoformat(sunrise_iso).strftime("%H:%M")

    current_weather_code = forecast_response['current']['weather_code']


    weather_mapping = {
        0: "Clear sky",
        1: "Mainly clear",
        2: "Partly cloudy",
        3: "Overcast",
        45: "Fog",
        48: "Depositing rime fog",
        51: "Light drizzle",
        53: "Moderate drizzle",
        55: "Dense drizzle",
        56: "Light freezing drizzle",
        57: "Dense freezing drizzle",
        61: "Slight rain",
        63: "Moderate rain",
        65: "Heavy rain",
        66: "Light freezing rain",
        67: "Heavy freezing rain",
        71: "Slight snowfall",
        73: "Moderate snowfall",
        75: "Heavy snowfall",
        77: "Snow grains",
        80: "Slight rain showers",
        81: "Moderate rain showers",
        82: "Violent rain showers",
        85: "Slight snow showers",
        86: "Heavy snow showers",
        95: "Thunderstorm",
        96: "Thunderstorm with slight hail",
        99: "Thunderstorm with heavy hail",
    }

    description = weather_mapping[current_weather_code]

    context = {
        "city": city,
        "temperature": round(forecast_response['current']['temperature_2m']),
        "apparent_temperature": round(forecast_response['current']['apparent_temperature']),
        "description": description,
        "air_quality": air_quality,
        "relative_humidity": forecast_response["current"]["relative_humidity_2m"],
        "precipitation_chance": forecast_response["daily"]["precipitation_probability_max"][0],
        "rain": round(forecast_response["current"]["rain"]),
        "wind_speed": forecast_response["current"]["wind_speed_10m"],
        "wind_direction": forecast_response['current']['wind_direction_10m'],
        "sunset": sunset_time,
        "sunrise": sunrise_time,
        "hourly_forecast": hourly_forecast,
    }

    return render(request, "weather.html", context)

def autocomplete(request):
    query = request.GET.get('q', '')

    if len(query) < 2:
        return JsonResponse([], safe=False)

    url = f"https://geocoding-api.open-meteo.com/v1/search?name={query}&count=5&language=en&format=json"

    response = requests.get(url).json()
    cities = response.get("results", [])

    suggestions = [f"{city['name']}, {city['country']}"
                   for city in cities]

    return JsonResponse(suggestions, safe=False)


