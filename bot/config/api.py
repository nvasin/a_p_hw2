import os
from dotenv import load_dotenv


WEATHER_API_URL = "http://api.weatherstack.com/current"
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "")