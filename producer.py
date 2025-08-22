from kafka import KafkaProducer
from kafka.errors import KafkaError
import json
import requests
from datetime import datetime, timedelta
from tabulate import tabulate
import os
from dotenv import load_dotenv

load_dotenv()

KAFKA_BROKER = os.environ.get("KAFKA_BROKER", "localhost:9092")
KAFKA_TOPIC = os.environ.get("KAFKA_TOPIC", "topic2")
api_key = os.environ.get("OPENWEATHER_API_KEY")

producer = KafkaProducer(
    bootstrap_servers=[KAFKA_BROKER],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

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
        future = producer.send(KAFKA_TOPIC, value=weather)

try:
    record_metadata = future.get(timeout=10)
    print("✅ Messages successfully sent to Kafka")
except KafkaError as e:
    print(f"❌ Error sending message: {e}")
