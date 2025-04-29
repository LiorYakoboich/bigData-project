# -*- coding: utf-8 -*-
"""spark-airbnb-analysis.py

This script performs analysis on fake Airbnb data using PySpark.

written and submitted by [Your Name] [Your ID]
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, avg, year, desc, collect_list, struct, explode
from pyspark.sql import functions as F
from pyspark.sql.window import Window
import sqlite3
import os

print("Starting Spark session...")

# Create a Spark session
spark = SparkSession.builder \
    .appName("Airbnb Data Analysis") \
    .getOrCreate()

# File path
filename = 'airbnb_listings.json'

print(f"Checking for file: {filename}")

# Check if file exists
if not os.path.exists(filename):
    print(f"Error: {filename} not found. Please ensure the file is in the same directory as this script.")
    exit(1)

print("Reading JSON file...")

# Read the JSON file
df = spark.read.json(filename)

print("Preprocessing data...")

# Convert 'price' to numeric
df = df.withColumn("price", col("price").cast("double"))

print("Performing analysis...")

# Question: What are the top 5 cities with the highest average listing prices for each property type?

# Step 1: Calculate average price per city and property type
avg_prices = df.groupBy("city.name", "property_type") \
               .agg(F.avg("price").alias("avg_price"))

# Step 2: Rank cities within each property type based on average price
window_spec = Window.partitionBy("property_type").orderBy(F.desc("avg_price"))

# Step 3: Rank cities with dense_rank to handle ties
ranked_cities = avg_prices.withColumn("rank", F.dense_rank().over(window_spec))

# Step 4: Select top 5 cities for each property type
top_cities_by_property_type = ranked_cities.filter(F.col("rank") <= 5) \
                                           .groupBy("property_type") \
                                           .agg(F.collect_list(F.struct("name", "avg_price")).alias("top_cities"))

print("Analysis results:")
top_cities_by_property_type.show(truncate=False)

print("Preparing data for SQLite...")

# Convert the 'top_cities' column to a JSON string
top_cities_by_property_type = top_cities_by_property_type.withColumn('top_cities', F.to_json(col('top_cities')))

# Convert to Pandas
pandas_df = top_cities_by_property_type.toPandas()

print("Saving results to SQLite database...")

# Save to SQLite
conn = sqlite3.connect('airbnb_analysis_results.db')
pandas_df.to_sql('top_cities_by_property_type', conn, if_exists='replace', index=False)
conn.close()

print("Analysis complete. Results saved to airbnb_analysis_results.db")

# Stop the Spark session
spark.stop()

print("Spark session stopped. Script completed.")