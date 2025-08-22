# 🌦️ Real-Time Weather Data Pipeline

This project is an **end-to-end streaming pipeline** that fetches
weather forecast data from the **OpenWeather API**, streams it through
**Apache Kafka**, processes it with **Apache Spark Structured
Streaming**, and stores it into **AWS S3** and **Snowflake** for
analytics.

------------------------------------------------------------------------

## 📂 Project Structure

-   **producer.py** → Fetches weather data from OpenWeather API and
    pushes it into Kafka (`topic2`).
-   **kafka_spark_test.py** → Spark consumer to test and validate
    incoming Kafka messages.
-   **weather.py** → Standalone script to fetch and display weather
    forecast (without Kafka).
-   **aws_s3.py** → Spark streaming consumer that writes weather data
    into **AWS S3 (CSV format)**.
-   **snowflake.py** → Spark streaming consumer that writes weather data
    into **Snowflake tables**.

------------------------------------------------------------------------

## ⚙️ Technologies Used

-   **Apache Kafka** → Message broker for streaming weather data.
-   **Apache Spark (Structured Streaming)** → Stream processing engine.
-   **AWS S3** → Data lake storage (CSV).
-   **Snowflake** → Cloud data warehouse for analytics.
-   **OpenWeather API** → Weather forecast provider.
-   **Python (3.8+)** → Programming language for producer and consumers.
-   **python-dotenv** → For managing credentials securely.

------------------------------------------------------------------------

## 📦 Installation & Setup

### 1️⃣ Clone the Repository

``` bash
git clone https://github.com/your-username/weather-streaming-pipeline.git
cd weather-streaming-pipeline
```

### 2️⃣ Install Dependencies

``` bash
pip install -r requirements.txt
```

**requirements.txt**

    pyspark
    kafka-python
    requests
    tabulate
    boto3
    python-dotenv
    snowflake-connector-python

------------------------------------------------------------------------

## 🔐 Configuration

### `.env` file

Create a `.env` file in your project root (not committed to GitHub):

    # OpenWeather API
    OPENWEATHER_API_KEY=your_openweather_api_key

    # AWS Config
    AWS_ACCESS_KEY_ID=your_aws_access_key
    AWS_SECRET_ACCESS_KEY=your_aws_secret_key
    S3_BUCKET_NAME=weatherapi-nivedya

    # Snowflake Config
    SNOWFLAKE_URL=https://your_account.snowflakecomputing.com
    SNOWFLAKE_USER=your_username
    SNOWFLAKE_PASSWORD=your_password
    SNOWFLAKE_DATABASE=my_database
    SNOWFLAKE_SCHEMA=my_schema
    SNOWFLAKE_WAREHOUSE=my_warehouse

    # Kafka Config
    KAFKA_BROKER=localhost:9092
    KAFKA_TOPIC=topic2

### `.gitignore`

    .env
    __pycache__/
    *.log
    *.csv

------------------------------------------------------------------------

## ▶️ Running the Pipeline

### Step 1: Start Kafka & Zookeeper

``` bash
zookeeper-server-start.sh config/zookeeper.properties
kafka-server-start.sh config/server.properties
```

Create the topic:

``` bash
kafka-topics.sh --create --topic topic2 --bootstrap-server localhost:9092
```

### Step 2: Run the Producer

``` bash
python producer.py
```

This fetches weather data for **Kochi, Bangalore, and Mumbai** and
publishes to Kafka.

### Step 3: Test Consumer (Optional)

``` bash
python kafka_spark_test.py
```

This verifies data ingestion and schema parsing.

### Step 4: Stream to AWS S3

``` bash
python aws_s3.py
```

Stores Kafka data batches as CSV in your **S3 bucket**.

### Step 5: Stream to Snowflake

``` bash
python snowflake.py
```

Writes Kafka data into **Snowflake tables**.

------------------------------------------------------------------------

## 📊 Example Output

### Producer JSON Message

``` json
{
  "City": "Kochi",
  "Date": "2025-08-22 12:00:00",
  "Temperature (Celsius)": 28.34,
  "Weather": "Cloudy",
  "Humidity (%)": 84,
  "Wind Speed (m/s)": 4.6
}
```

### AWS S3 CSV Output

    city,date,temperature,weather,humidity,windspeed
    Kochi,2025-08-22 12:00:00,28.34,Cloudy,84,4.6

------------------------------------------------------------------------

## 🚀 Future Improvements

-   Dockerize the pipeline (Kafka + Spark + S3 + Snowflake)
-   Add monitoring & logging
-   Use Airflow for orchestration
-   Integrate dashboards (Power BI / Tableau / Superset)

------------------------------------------------------------------------

## 👩‍💻 Author

**Nivedya K**\
Data Enthusiast \| Cloud & Big Data \| Analytics

------------------------------------------------------------------------
