import requests
from datetime import datetime, timedelta
from tabulate import tabulate
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.environ.get("OPENWEATHER_API_KEY")
city_names = ['Kochi', 'Bangalore', 'Mumbai']

weather_data = []

for city in city_names:
    url = f'https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}'
    response = requests.get(url)
    data = response.json()

    city_weather_data = []
    for forecast in data['list']:
        timestamp = forecast['dt']
        date = datetime.utcfromtimestamp(timestamp)
        if date > datetime.utcnow() + timedelta(days=7):
            break

        weather = {
            'City': city,
            'Date': date.strftime('%Y-%m-%d %H:%M:%S'),
            'Temperature (Celsius)': round(forecast['main']['temp'] - 273.15, 2),
            'Weather': forecast['weather'][0]['description'].capitalize(),
            'Humidity (%)': forecast['main']['humidity'],
            'Wind Speed (m/s)': forecast['wind']['speed']
        }
        city_weather_data.append(weather)

    weather_data.extend(city_weather_data)

print(tabulate(weather_data, headers='keys', tablefmt='pretty'))
