import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from datetime import datetime
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, FloatType, TimestampType
from dotenv import load_dotenv

load_dotenv()

sfOptions = {
  "sfURL": os.environ.get("SNOWFLAKE_URL"),
  "sfUser": os.environ.get("SNOWFLAKE_USER"),
  "sfPassword": os.environ.get("SNOWFLAKE_PASSWORD"),
  "sfDatabase": os.environ.get("SNOWFLAKE_DATABASE"),
  "sfSchema": os.environ.get("SNOWFLAKE_SCHEMA"),
  "sfWarehouse": os.environ.get("SNOWFLAKE_WAREHOUSE")
}

KAFKA_TOPIC = os.environ.get("KAFKA_TOPIC", "topic2")
KAFKA_BROKER = os.environ.get("KAFKA_BROKER", "localhost:9092")

spark = SparkSession.builder     .appName("KafkaDataToSnowflake")     .config("spark.jars.packages", 
            "org.apache.spark:spark-sql-kafka-0-10_2.13:3.5.0,"
            "net.snowflake:snowflake-jdbc:3.13.22,"
            "net.snowflake:spark-snowflake_2.13:2.11.1-spark_3.3")     .getOrCreate()

spark.sparkContext.setLogLevel('INFO')

json_schema = StructType([
    StructField("City", StringType()),
    StructField("Date", TimestampType()),
    StructField("Temperature (Celsius)", FloatType()),
    StructField("Weather", StringType()),
    StructField("Humidity (%)", IntegerType()),
    StructField("Wind Speed (m/s)", FloatType())
])

stream_df = spark.readStream     .format("kafka")     .option("kafka.bootstrap.servers", KAFKA_BROKER)     .option("subscribe", KAFKA_TOPIC)     .option("startingOffsets", "earliest")     .load()

parsed_df = stream_df.select(from_json(col("value").cast("string"), json_schema).alias("data")).select("data.*")

batch_counter = 0

def process_batch(df, epoch_id):
    global batch_counter
    record_count = df.count()

    if record_count > 0:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        table_name = f"WEATHER_DATA_BATCH_{batch_counter}_{timestamp}"

        df.write             .format("snowflake")             .options(**sfOptions)             .option("dbtable", table_name)             .mode("overwrite")             .save()

        print(f"✅ Batch {batch_counter} ({record_count} records) written to Snowflake table {table_name}")
        batch_counter += 1
    else:
        print("⚠️ No records in this batch")

query = parsed_df.writeStream     .foreachBatch(process_batch)     .outputMode("append")     .trigger(processingTime='1 minute')     .start()

query.awaitTermination()
