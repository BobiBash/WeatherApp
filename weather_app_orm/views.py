from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, redirect
import requests
from datetime import datetime
from dotenv import load_dotenv
import os

from requests import ReadTimeout


# Create your views here.



def search_weather(request):
    city = request.GET.get("city", "").strip()

    if city:
        return redirect("city_weather", city=city)

    return render(request, "search.html")

def city_weather(request, city):


    url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=10&language=en&format=json"
    try:
        response = requests.get(url).json()
    except ReadTimeout:
        return "Something failed. Please try again later."

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
        0: {
            "description": "Clear sky",
            "icon_day": "clear-day",
            "icon_night": "clear-night",
        },
        1: {
            "description": "Mainly clear",
            "icon_day": "partly-cloudy-day",
            "icon_night": "partly-cloudy-night",
        },
        2: {
            "description": "Partly cloudy",
            "icon_day": "partly-cloudy-day",
            "icon_night": "partly-cloudy-night",
        },
        3: {
            "description": "Overcast",
            "icon": "overcast",
        },
        45: {
            "description": "Fog",
            "icon": "fog",
        },
        48: {
            "description": "Depositing rime fog",
            "icon": "fog",
        },
        51: {
            "description": "Light drizzle",
            "icon": "drizzle",
        },
        53: {
            "description": "Moderate drizzle",
            "icon": "drizzle",
        },
        55: {
            "description": "Dense drizzle",
            "icon": "drizzle",
        },
        56: {
            "description": "Light freezing drizzle",
            "icon": "sleet",
        },
        57: {
            "description": "Dense freezing drizzle",
            "icon": "sleet",
        },
        61: {
            "description": "Slight rain",
            "icon": "rain",
        },
        63: {
            "description": "Moderate rain",
            "icon": "rain",
        },
        65: {
            "description": "Heavy rain",
            "icon": "rain",
        },
        66: {
            "description": "Light freezing rain",
            "icon": "sleet",
        },
        67: {
            "description": "Heavy freezing rain",
            "icon": "sleet",
        },
        71: {
            "description": "Slight snowfall",
            "icon": "snow",
        },
        73: {
            "description": "Moderate snowfall",
            "icon": "snow",
        },
        75: {
            "description": "Heavy snowfall",
            "icon": "snow",
        },
        77: {
            "description": "Snow grains",
            "icon": "snow",
        },
        80: {
            "description": "Slight rain showers",
            "icon": "showers",
        },
        81: {
            "description": "Moderate rain showers",
            "icon": "showers",
        },
        82: {
            "description": "Violent rain showers",
            "icon": "thunderstorms",
        },
        85: {
            "description": "Slight snow showers",
            "icon": "snow",
        },
        86: {
            "description": "Heavy snow showers",
            "icon": "snow",
        },
        95: {
            "description": "Thunderstorm",
            "icon": "thunderstorms",
        },
        96: {
            "description": "Thunderstorm with slight hail",
            "icon": "hail",
        },
        99: {
            "description": "Thunderstorm with heavy hail",
            "icon": "hail",
        },
    }

    is_day = forecast_response["current"]["is_day"]

    entry = weather_mapping.get(current_weather_code)
    icon = ""

    if is_day and "icon_day" in entry:
        icon = entry["icon_day"]
    elif not is_day and "icon_night" in entry:
        icon = entry["icon_night"]
    elif "icon" in entry:
        icon = entry["icon"]

    description = weather_mapping[current_weather_code]

    context = {
        "city": city,
        "temperature": round(forecast_response['current']['temperature_2m']),
        "apparent_temperature": round(forecast_response['current']['apparent_temperature']),
        "icon": icon,
        "description": description["description"],
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


