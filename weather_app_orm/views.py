import json

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

def  city_weather(request, city):
    view_type = request.GET.get("view", "current")

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
    print(lat, lon)
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": ["temperature_2m","weather_code", "apparent_temperature", "is_day", "relative_humidity_2m", "precipitation_probability",
                    "wind_speed_10m", "wind_gusts_10m", "wind_direction_10m"],
        "daily": ["sunrise", "sunset", 'precipitation_probability_max'],
        "current": ["temperature_2m","weather_code", "apparent_temperature", "is_day", "relative_humidity_2m", "precipitation", "rain",
                    "wind_speed_10m", "wind_gusts_10m", "wind_direction_10m"],
        "timezone": "Europe/Sofia"
    }

    forecast_url = "https://api.open-meteo.com/v1/forecast"
    air_quality_url = f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={lat}&longitude={lon}&current=european_aqi&hourly=european_aqi"
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

    def get_weather_icon_and_description(weather_code_func, is_day_func):

        entry = weather_mapping.get(weather_code_func)

        if not entry:
            return "not-available", "Unknown"


        if is_day_func and "icon_day" in entry:
            icon = entry["icon_day"]
        elif not is_day_func and "icon_night" in entry:
            icon = entry["icon_night"]
        elif "icon" in entry:
            icon = entry["icon"]
        else:
            icon = "not-available"

        return icon, entry["description"]

    # hourly stuff
    now = datetime.now()
    future_data = [
        (datetime.fromisoformat(h), w_code, appa_temp, day, hum, wind_spd, wind_gst, wind_dir, temp, rain_prob, air_q)
        for h, w_code, appa_temp, day, hum, wind_spd, wind_gst, wind_dir, temp, rain_prob, air_q
        in zip(
            forecast_response["hourly"]["time"],
            forecast_response["hourly"]["weather_code"],
            forecast_response["hourly"]["apparent_temperature"],
            forecast_response["hourly"]["is_day"],
            forecast_response["hourly"]["relative_humidity_2m"],
            forecast_response["hourly"]["wind_speed_10m"],
            forecast_response["hourly"]["wind_gusts_10m"],
            forecast_response["hourly"]["wind_direction_10m"],
            forecast_response["hourly"]["temperature_2m"],
            forecast_response["hourly"]["precipitation_probability"],
            air_quality_json["hourly"]["european_aqi"]
        )
        if datetime.fromisoformat(h) >= now
    ]
    hourly_forecast = []
    for t, w_code, appa_temp, day, hum, wind_spd, wind_gst, wind_dir, temp, rain_prob, air_q in future_data[:24]:
        hourly_icon, hourly_description = get_weather_icon_and_description(w_code, day)

        hourly_forecast.append({
            "time": t.strftime("%I %p"),
            "temperature": round(temp),
            "apparent_temperature": round(appa_temp),
            "weather_code": w_code,
            "is_day": day,
            "humidity": hum,
            "wind_speed": wind_spd,
            "wind_gusts": wind_gst,
            "wind_direction": wind_dir,
            "rain_chance": rain_prob,
            "icon": hourly_icon,
            "description": hourly_description,
            "air_quality": air_q
        })

    is_day = forecast_response["current"]["is_day"]
    daily_icon,daily_description = get_weather_icon_and_description(current_weather_code, is_day)


    context = {
        "city": city,
        "temperature": round(forecast_response['current']['temperature_2m']),
        "apparent_temperature": round(forecast_response['current']['apparent_temperature']),
        "icon": daily_icon,
        "description": daily_description,
        "air_quality": air_quality,
        "relative_humidity": forecast_response["current"]["relative_humidity_2m"],
        "precipitation_chance": forecast_response["daily"]["precipitation_probability_max"][0],
        "rain": round(forecast_response["current"]["rain"]),
        "wind_speed": forecast_response["current"]["wind_speed_10m"],
        "wind_gusts": forecast_response["current"]["wind_gusts_10m"],
        "wind_direction": forecast_response['current']['wind_direction_10m'],
        "sunset": sunset_time,
        "sunrise": sunrise_time,
        "hourly_forecast": hourly_forecast,
    }

    if view_type == "hourly":
        context["hourly_forecast"] = json.dumps(hourly_forecast)
        return render(request, "hourly_weather.html", context)
    else:
        return render(request, "weather.html", context)

def autocomplete(request):
    query = request.GET.get('q', '')

    MIN_THRESHOLD = 5000

    if len(query) < 2:
        return JsonResponse([], safe=False)

    url = f"https://geocoding-api.open-meteo.com/v1/search?name={query}&count=20&language=en&format=json"

    response = requests.get(url).json()
    cities = response.get("results", [])

    population_mapping = {f"{city["name"]}, {city["country"]}": city.get('population') for city in cities if 'population' in city and city.get('population') > MIN_THRESHOLD}
    print(population_mapping)

    sorted_by_population = sorted(population_mapping.items(), key=lambda item: item[1], reverse=True)
    print(sorted_by_population)
    city_names = [item[0] for item in sorted_by_population]

    suggestions = [city for city in city_names][:5]

    print(suggestions)

    return JsonResponse(suggestions, safe=False)


