# WeatherApp

Simple Django-based weather application that uses Open-Meteo APIs to show current weather, hourly forecast and air quality for a searched city.

## Features
- Search cities with autocomplete suggestions.
- City page with current conditions, hourly forecast (24h), sunrise/sunset and wind data.
- Air quality classification (European AQI).
- Minimal frontend using `HTML`, `CSS` and JavaScript.

## Tech stack
- Python \(Django\)
- JavaScript (vanilla)
- HTML
- CSS
- Pip for dependency management

## Quick setup (Windows)
1. Clone repository:
   - `git clone https://github.com/BobiBash/WeatherApp.git`
   - `git checkout master`
2. Create and activate a virtual environment:
   - `python -m venv .venv`
   - PowerShell: `.\.venv\Scripts\Activate`
   - CMD: `.\.venv\Scripts\activate`
3. Install dependencies:
   - `pip install -r requirements.txt`
4. (Optional) Create a `.env` file at project root for custom config. The project uses `python-dotenv` in `weather_app_orm/views.py`. No API key required for Open-Meteo.

## Project layout (important files)
- `manage.py` — Django entry point.
- `weatherapp/` — Django project settings and URLs.
- `weather_app_orm/` — main app:
  - `views.py` — search, city page, autocomplete (main logic).
  - `templates/` — `search.html`, `weather.html`, `error.html`.
  - `static/` — JS and CSS assets (`autocompletion.js`, styles).
- `db.sqlite3` — default local database file (if present).

## External APIs used
- Geocoding: `https://geocoding-api.open-meteo.com/v1/search`
- Forecast: `https://api.open-meteo.com/v1/forecast`
- Air quality: `https://air-quality-api.open-meteo.com/v1/air-quality`

## Screenshots
<img width="1864" height="909" alt="image" src="https://github.com/user-attachments/assets/548ff172-ea93-4ec2-b947-de6ca9095731" />
<img width="1867" height="910" alt="image" src="https://github.com/user-attachments/assets/7e15236f-8785-4528-a97f-64760d0a505e" />
<img width="1862" height="907" alt="image" src="https://github.com/user-attachments/assets/c967f72f-8b9d-41cb-803d-474b2eef1761" />
