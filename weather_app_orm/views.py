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
    load_dotenv()
    api_key = os.getenv("OPENWEATHER_API_KEY")

    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"

    response = requests.get(url)
    data = response.json()
    if data.get('cod') != 200:
        return render(request, "error.html", {
            "error": f"No results found"
        })

    lon = data['coord']['lon']
    lat = data['coord']['lat']

    hourly_url = f"https://api.open-meteo.com/v1/forecast?&latitude={lat}&longitude={lon}&hourly=temperature_2m&timezone=Europe/Sofia"

    hourly_data = requests.get(hourly_url).json()
    hours = hourly_data["hourly"]["time"]
    temps = hourly_data["hourly"]['temperature_2m']

    hours_formatted = [datetime.fromisoformat(h).strftime("%I %p") for h in hours]

    hourly_forecast = [{"time": t, "temp": temp} for t, temp in zip(hours_formatted[:24], temps[:24])]

    sunset_utc = data["sys"]["sunset"]
    sunset_time = datetime.fromtimestamp(sunset_utc).strftime("%H:%M")

    sunrise_utc = data["sys"]["sunrise"]
    sunrise_time = datetime.fromtimestamp(sunrise_utc).strftime("%H:%M")



    context = {
        "city": city,
        "temperature": data["main"]["temp"],
        "description": data["weather"][0]["description"],
        "humidity": data["main"]["humidity"],
        "wind_speed": data["wind"]["speed"],
        "visibility": data["visibility"],
        "country": data["sys"]["country"],
        "sunset": sunset_time,
        "sunrise": sunrise_time,
        "hourly_forecast": hourly_forecast,
    }

    return render(request, "weather.html", context)

def autocomplete(request):
    load_dotenv()
    api_key = os.getenv("OPENWEATHER_API_KEY")
    query = request.GET.get('q', '')
    if len(query) < 2:
        return JsonResponse([], safe=False)

    url = f"http://api.openweathermap.org/geo/1.0/direct?q={query}&limit=5&appid={api_key}&units=metric"
    response = requests.get(url)
    cities = response.json()

    suggestions = [f"{city['name']} - {city['country']}"
                   for city in cities]

    return JsonResponse(suggestions, safe=False)


