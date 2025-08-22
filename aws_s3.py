import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from datetime import datetime
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, FloatType, TimestampType
from dotenv import load_dotenv

load_dotenv()

AWS_ACCESS_KEY = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
S3_BUCKET = os.environ.get("S3_BUCKET_NAME", "weatherapi-nivedya")

KAFKA_TOPIC = os.environ.get("KAFKA_TOPIC", "topic2")
KAFKA_BROKER = os.environ.get("KAFKA_BROKER", "localhost:9092")

spark = SparkSession.builder     .appName("KafkaDataToS3")     .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.13:3.5.0,org.apache.hadoop:hadoop-aws:3.3.4")     .config("spark.hadoop.fs.s3a.access.key", AWS_ACCESS_KEY)     .config("spark.hadoop.fs.s3a.secret.key", AWS_SECRET_KEY)     .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")     .config("spark.hadoop.fs.s3a.aws.credentials.provider", "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider")     .getOrCreate()

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

parsed_df = df.select(from_json(col("value"), json_schema).alias("parsed_value"))

def process_batch(df, epoch_id):
    expanded_df = df.select(
        col("parsed_value.City").alias("city"),
        col("parsed_value.Date").alias("date"),
        col("parsed_value.Temperature (Celsius)").alias("temperature"),
        col("parsed_value.Weather").alias("weather"),
        col("parsed_value.Humidity (%)").alias("humidity"),
        col("parsed_value.Wind Speed (m/s)").alias("windspeed")
    )

    print(f"Data overview for batch {epoch_id}:")
    expanded_df.show(n=5, truncate=False)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"weather_data_batch_{epoch_id}_{timestamp}.csv"
    output_path = f"s3a://{S3_BUCKET}/{filename}"

    expanded_df.coalesce(1).write         .format('csv')         .option('header', True)         .mode('overwrite')         .save(output_path)

    print(f"✅ Batch {epoch_id} written to {output_path}")

query = parsed_df.writeStream     .foreachBatch(process_batch)     .outputMode("append")     .trigger(processingTime='1 minute')     .start()

query.awaitTermination()
