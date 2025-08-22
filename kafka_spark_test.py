from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, FloatType, TimestampType
from dotenv import load_dotenv
import os

load_dotenv()

KAFKA_TOPIC = os.environ.get("KAFKA_TOPIC", "topic2")
KAFKA_BROKER = os.environ.get("KAFKA_BROKER", "localhost:9092")

spark = SparkSession.builder     .appName("KafkaDataToTable")     .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.13:3.5.0")     .getOrCreate()

spark.sparkContext.setLogLevel('INFO')

stream_df = spark.readStream     .format("kafka")     .option("kafka.bootstrap.servers", KAFKA_BROKER)     .option("subscribe", KAFKA_TOPIC)     .option("startingOffsets", "earliest")     .load()

df = stream_df.selectExpr("CAST(value AS STRING)")

json_schema = StructType([
    StructField("City", StringType()),
    StructField("Date", TimestampType()),
    StructField("Temperature (Celsius)", FloatType()),
    StructField("Weather", StringType()),
    StructField("Humidity (%)", IntegerType()),
    StructField("Wind Speed (m/s)", FloatType())
])

parsed_df = df.select(from_json(col("value"), json_schema).alias("parsed_value"), col("value").alias("raw_data"))

def process_batch(df, epoch_id):
    expanded_df = df.select(
        col("parsed_value.City").alias("city"),
        col("parsed_value.Date").alias("date"),
        col("parsed_value.Temperature (Celsius)").alias("temperature"),
        col("parsed_value.Weather").alias("weather"),
        col("parsed_value.Humidity (%)").alias("humidity"),
        col("parsed_value.Wind Speed (m/s)").alias("windspeed"),
        col("raw_data")
    )
    print("Data overview:")
    expanded_df.show(n=10, truncate=False)

query = parsed_df.writeStream     .foreachBatch(process_batch)     .outputMode("update")     .trigger(processingTime='5 seconds')     .start()

query.awaitTermination()
