import duckdb
import pandas as pd
import sqlite3

# Define the name of our CSV file
csv_file_name = 'airbnb-listings.csv'

# Connect to DuckDB
con = duckdb.connect()

# Create the table and load data from the CSV file
con.execute("""
    CREATE TABLE airbnb_listings AS 
    SELECT * FROM read_csv_auto(?, 
        types={
            'ID': 'VARCHAR',
            'Listing Url': 'VARCHAR',
            'Scrape ID': 'VARCHAR',
            'Last Scraped': 'DATE',
            'Name': 'VARCHAR',
            'Summary': 'VARCHAR',
            'Space': 'VARCHAR',
            'Description': 'VARCHAR',
            'Experiences Offered': 'VARCHAR',
            'Neighborhood Overview': 'VARCHAR',
            'Notes': 'VARCHAR',
            'Transit': 'VARCHAR',
            'Access': 'VARCHAR',
            'Interaction': 'VARCHAR',
            'House Rules': 'VARCHAR',
            'Thumbnail Url': 'VARCHAR',
            'Medium Url': 'VARCHAR',
            'Picture Url': 'VARCHAR',
            'XL Picture Url': 'VARCHAR',
            'Host ID': 'VARCHAR',
            'Host URL': 'VARCHAR',
            'Host Name': 'VARCHAR',
            'Host Since': 'DATE',
            'Host Location': 'VARCHAR',
            'Host About': 'VARCHAR',
            'Host Response Time': 'VARCHAR',
            'Host Response Rate': 'VARCHAR',
            'Host Acceptance Rate': 'VARCHAR',
            'Host Thumbnail Url': 'VARCHAR',
            'Host Picture Url': 'VARCHAR',
            'Host Neighbourhood': 'VARCHAR',
            'Host Listings Count': 'INTEGER',
            'Host Total Listings Count': 'INTEGER',
            'Host Verifications': 'VARCHAR',
            'Street': 'VARCHAR',
            'Neighbourhood': 'VARCHAR',
            'Neighbourhood Cleansed': 'VARCHAR',
            'Neighbourhood Group Cleansed': 'VARCHAR',
            'City': 'VARCHAR',
            'State': 'VARCHAR',
            'Zipcode': 'VARCHAR',
            'Market': 'VARCHAR',
            'Smart Location': 'VARCHAR',
            'Country Code': 'VARCHAR',
            'Country': 'VARCHAR',
            'Latitude': 'FLOAT',
            'Longitude': 'FLOAT',
            'Property Type': 'VARCHAR',
            'Room Type': 'VARCHAR',
            'Accommodates': 'INTEGER',
            'Bathrooms': 'FLOAT',
            'Bedrooms': 'INTEGER',
            'Beds': 'INTEGER',
            'Bed Type': 'VARCHAR',
            'Amenities': 'VARCHAR',
            'Square Feet': 'FLOAT',
            'Price': 'FLOAT',
            'Weekly Price': 'FLOAT',
            'Monthly Price': 'FLOAT',
            'Security Deposit': 'FLOAT',
            'Cleaning Fee': 'FLOAT',
            'Guests Included': 'INTEGER',
            'Extra People': 'FLOAT',
            'Minimum Nights': 'INTEGER',
            'Maximum Nights': 'INTEGER',
            'Calendar Updated': 'VARCHAR',
            'Has Availability': 'VARCHAR',
            'Availability 30': 'INTEGER',
            'Availability 60': 'INTEGER',
            'Availability 90': 'INTEGER',
            'Availability 365': 'INTEGER',
            'Calendar last Scraped': 'VARCHAR',
            'Number of Reviews': 'INTEGER',
            'First Review': 'DATE',
            'Last Review': 'DATE',
            'Review Scores Rating': 'FLOAT',
            'Review Scores Accuracy': 'FLOAT',
            'Review Scores Cleanliness': 'FLOAT',
            'Review Scores Checkin': 'FLOAT',
            'Review Scores Communication': 'FLOAT',
            'Review Scores Location': 'FLOAT',
            'Review Scores Value': 'FLOAT',
            'License': 'VARCHAR',
            'Jurisdiction Names': 'VARCHAR',
            'Cancellation Policy': 'VARCHAR',
            'Calculated host listings count': 'INTEGER',
            'Reviews per Month': 'FLOAT',
            'Geolocation': 'VARCHAR',
            'Features': 'VARCHAR'
        }
    )
""", [csv_file_name])


# Function to execute DuckDB query and return as pandas DataFrame
def duckdb_to_pandas(query):
    return con.execute(query).df()


# Define SQL queries
queries = [
    ("""
    -- Query 1: Average price and number of listings by city (with at least 100 listings, English names only)
    SELECT DISTINCT
        COALESCE(City, 'Unknown') AS City, 
        AVG(Price) OVER (PARTITION BY City) AS Average_Price, 
        COUNT(*) OVER (PARTITION BY City) AS Number_of_Listings
    FROM airbnb_listings
    WHERE Price IS NOT NULL
    AND "Number of Reviews" IS NOT NULL
    AND City IS NOT NULL
    AND City ~ '^[A-Za-z\s]+$'  -- This regex matches only strings with English letters and spaces
    QUALIFY COUNT(*) OVER (PARTITION BY City) >= 100
    ORDER BY Average_Price DESC
    LIMIT 20;
    """, "average_price_listings_by_city"),

    ("""
       -- Query 2: Number of listings and average price by amenities
       SELECT 
           Amenities, 
           COUNT(*) AS Number_of_Listings, 
           AVG(Price) AS Average_Price
       FROM airbnb_listings
       WHERE Amenities IS NOT NULL
       AND Price IS NOT NULL
       GROUP BY Amenities
       ORDER BY Number_of_Listings DESC;
       """, "listings_avg_price_by_amenities"),

    ("""
       -- Query 3: Average review scores by property type
       SELECT 
           "Property Type", 
           AVG("Review Scores Rating") AS Average_Review_Score,
           AVG("Review Scores Cleanliness") * 10 AS Average_Cleanliness_Score,
           AVG("Review Scores Location") * 10 AS Average_Location_Score
       FROM 
           airbnb_listings
       WHERE "Review Scores Rating" IS NOT NULL
       GROUP BY 
           "Property Type"
       ORDER BY 
           Average_Review_Score DESC;
       """, "avg_review_scores_by_property_type"),

    ("""
       -- Query 4: Total number of reviews and average review score by neighborhood
       SELECT 
           "Neighbourhood", 
           SUM("Number of Reviews") AS Total_Reviews, 
           AVG("Review Scores Rating") AS Average_Review_Score
       FROM 
           airbnb_listings
       WHERE "Number of Reviews" IS NOT NULL
       GROUP BY 
           "Neighbourhood"
       ORDER BY 
           Total_Reviews DESC;
       """, "total_reviews_avg_review_score_by_neighborhood"),

    ("""
       -- Query 5: Property types with highest average price and number of bedrooms
       SELECT
           "Property Type",
           AVG("Price") AS Average_Price,
           AVG("Bedrooms") AS Average_Bedrooms
       FROM
           airbnb_listings
       WHERE Price IS NOT NULL
       GROUP BY
           "Property Type"
       ORDER BY
           Average_Price DESC, Average_Bedrooms DESC;
       """, "property_types_highest_avg_price_bedrooms"),

    ("""
       -- Query 6: Relationship between price and number of reviews (excluding NULL values)
       SELECT 
           Price, 
           "Number of Reviews", 
           COUNT(*) AS Listings
       FROM 
           airbnb_listings
       WHERE 
           Price IS NOT NULL
           AND "Number of Reviews" IS NOT NULL
       GROUP BY 
           Price, "Number of Reviews"
       ORDER BY 
           Price DESC, "Number of Reviews" DESC;
       """, "relationship_price_reviews_excluding_null"),

]

pd.set_option('display.max_columns', None)

# Connect to SQLite
sqlite_conn = sqlite3.connect('airbnb_queries.db')

# Execute each query, store the result in a DataFrame, and save it to SQLite
for idx, (query, query_name) in enumerate(queries):
    df_result = duckdb_to_pandas(query)
    print(f"Query {idx + 1}: {query_name}")
    print(df_result)
    print("=" * 50)

    # Save the DataFrame to SQLite
    table_name = f"query_{idx + 1}"
    df_result.to_sql(table_name, sqlite_conn, if_exists='replace', index=False)

# Close the SQLite connection
sqlite_conn.close()