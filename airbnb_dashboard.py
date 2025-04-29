import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import sqlite3
import seaborn as sns
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.express as px
import json

def main():
    """
    Main function to run the Streamlit dashboard.
    """
    st.set_page_config(page_title="Airbnb Listings Dashboard")

    # Load data from SQLite database
    conn = sqlite3.connect('airbnb_queries.db')
    conn_analysis = sqlite3.connect('airbnb_analysis_results.db')

    # Create sidebar for navigation
    pages = {
        "Questions": questions_page,
        "Story and Insights": story_page,
        "Sample Rows": lambda: sample_rows_page(conn),
        "Average Price by City": lambda: avg_price_by_city_page(conn),
        "Review Scores by Property Type": lambda: review_scores_by_property_type_page(conn),
        "Reviews by Neighborhood": lambda: reviews_by_neighborhood_page(conn),
        "Price and Bedrooms by Property Type": lambda: price_bedrooms_by_property_type_page(conn),
        "Interactive City Comparison": lambda: interactive_city_comparison_page(conn),
        "Interactive Property Type Reviews": lambda: interactive_property_type_reviews_page(conn),
        "Top Cities by Property Type (Spark Analysis)": lambda: top_cities_by_property_type_page(conn_analysis),
    }

    selection = st.sidebar.radio("Go to", list(pages.keys()))

    # Call the selected page function
    pages[selection]()
    conn.close()


def questions_page():
    """
    Renders the Questions page with a list of questions related to the dataset.
    """
    st.header("Questions")
    st.write("""
    1. How do average prices and number of listings vary across different cities?
    2. What is the relationship between amenities, number of listings, and average price?
    3. How do review scores vary across different property types?
    4. Which neighborhoods have the most reviews and highest average review scores?
    5. What are the average prices and number of bedrooms for different property types?
    6. Is there a relationship between a listing's price and its number of reviews?
    """)


def story_page():
    """
    Renders the Story and Insights page with an overview of the analysis and its findings.
    """
    st.header("Story and Insights")
    st.write("""
    This dashboard provides a comprehensive analysis of Airbnb listings across various cities and property types. It examines pricing trends, listing volumes, guest satisfaction, and property characteristics to offer insights into the short-term rental market.

    ### Key Insights:

    #### 1. **Pricing and Listing Volume**
    - **Copenhagen** has the highest average price of $633.90 among the cities shown but has relatively fewer listings. This suggests that Copenhagen's market may cater to more premium or luxury rentals, with fewer but more expensive options available.
    - **Hong Kong City** stands out with the most listings at 3,124, though it has a mid-range average price. This indicates a high supply in the market, possibly driven by a large demand and diverse range of available properties.
    - There is an inverse relationship between price and listing volume in some cities. For instance, Copenhagen has high prices but fewer listings, while Hong Kong has many listings but mid-range prices. This relationship can indicate different market dynamics where cities with high demand and low supply see higher prices, whereas cities with high supply can offer more competitive pricing.

    #### 2. **Property Type Performance**
    - **Heritage hotels (India)**, **entire floors**, and **casa particulars** receive the highest overall review scores, indicating that guests have a high level of satisfaction with these property types.
    - **Luxury and unique accommodations**, such as **treehouses** and **yurts**, tend to score well across all review categories (average review score, cleanliness, and location). This suggests that guests value unique experiences and are likely willing to pay a premium for these stays.
    - **Budget options** like **hostels** and **dorms** receive lower scores, especially for cleanliness. This highlights a potential area for improvement for these types of accommodations, possibly by increasing maintenance and cleaning standards.

    #### 3. **Neighborhood Popularity**
    - **Venice** has the highest number of total reviews, indicating high popularity and potentially a well-established market with many visitors. This makes Venice a competitive area for hosts aiming to attract a large volume of guests.
    - Some neighborhoods with fewer reviews, such as **Norrbro**, have very high average review scores. This suggests that while these areas may not have as many guests, the quality of the experience is high, which could attract a niche market looking for high-quality stays.

    #### 4. **Property Characteristics and Pricing**
    - There is a general trend of higher prices for properties with more bedrooms, but there is significant variation by property type. For example, unique property types such as **islands**, **castles**, and **boats** command higher prices regardless of the number of bedrooms. This highlights the premium guests are willing to pay for unique and exclusive experiences.
    - **Standard apartments** and **houses** show a more linear relationship between the number of bedrooms and price. This can be attributed to the straightforward value addition of extra space and accommodation capacity in more conventional property types.

    #### 5. **Guest Satisfaction Factors**
    - **Cleanliness scores** are generally high across most property types, suggesting that cleanliness is a key focus for hosts and a major factor in guest satisfaction. Maintaining high standards of cleanliness can significantly impact the overall review scores.
    - **Location scores** vary more widely, indicating the importance of choosing the right area. Properties in desirable or convenient locations tend to receive higher scores, reflecting guests' preferences for accessibility and proximity to attractions or amenities.

    ### Summary
    These insights provide valuable information for various stakeholders in the short-term rental market:
    - **Hosts** can optimize their listings by focusing on cleanliness, choosing the right locations, and understanding the pricing dynamics in their city.
    - **Travelers** can make informed decisions when choosing accommodations based on property types and neighborhoods that align with their preferences for quality and location.
    - **Airbnb and real estate investors** can gain market intelligence to identify trends, opportunities for investment, and areas for improvement.

    The data underscores the diversity of the short-term rental market and the different factors that contribute to success across various segments.
    """)


def sample_rows_page(conn):
    """
    Renders the Sample Rows page with sample rows from all the tables.
    """
    st.header("Sample Rows")
    st.write("This page displays sample rows from all the tables in the database.")

    queries = [
        ("Average Price and Listings by City", "SELECT * FROM query_1 LIMIT 50"),
        ("Listings and Average Price by Amenities", "SELECT * FROM query_2 LIMIT 50"),
        ("Review Scores by Property Type", "SELECT * FROM query_3 LIMIT 50"),
        ("Reviews by Neighborhood", "SELECT * FROM query_4 LIMIT 50"),
        ("Price and Bedrooms by Property Type", "SELECT * FROM query_5 LIMIT 50"),
        ("Price vs Reviews", "SELECT * FROM query_6 LIMIT 50")
    ]

    for title, query in queries:
        st.subheader(title)
        df = pd.read_sql(query, conn)
        st.dataframe(df.style.highlight_max(axis=0))
        st.write(
            f"This table shows a sample of {title.lower()}. It provides insight into the data used to create the visualizations.")


def avg_price_by_city_page(conn):
    """
    Renders the Average Price by City page with a bar chart showing the average price and number of listings for each city.
    """
    st.header("Average Price and Number of Listings by City")
    st.write("""
    This chart displays the average price and number of listings for each city with at least 100 listings. 
    It helps us understand how prices and listing volumes vary across different locations.
    """)
    df = pd.read_sql("SELECT * FROM query_1 ORDER BY Average_Price DESC LIMIT 7", conn)

    # Check if dataframe is empty
    if df.empty:
        st.write("No data available for cities with at least 100 listings.")
        return

    # Remove any rows with NaN values
    df = df.dropna()

    if df.empty:
        st.write("No valid data available after removing NULL values.")
        return

    fig, ax1 = plt.subplots(figsize=(12, 6))
    ax2 = ax1.twinx()

    ax1.bar(df["City"], df["Average_Price"], color='b', alpha=0.7, label='Average Price')
    ax2.plot(df["City"], df["Number_of_Listings"], color='r', label='Number of Listings')

    ax1.set_xlabel("City")
    ax1.set_ylabel("Average Price ($)")
    ax2.set_ylabel("Number of Listings")

    plt.title("Average Price and Number of Listings by City (100+ listings)")
    plt.xticks(rotation=45, ha='right')

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')

    plt.tight_layout()
    st.pyplot(fig)

    # Display some statistics
    st.write(f"Total cities shown: {len(df)}")
    st.write(f"City with highest average price: {df['City'].iloc[0]} (${df['Average_Price'].iloc[0]:.2f})")
    st.write(
        f"City with most listings: {df.loc[df['Number_of_Listings'].idxmax(), 'City']} ({df['Number_of_Listings'].max()} listings)")




def review_scores_by_property_type_page(conn):
    """
    Renders the Review Scores by Property Type page with a heatmap showing different review score types for each property type.
    """
    st.header("Review Scores by Property Type")
    st.write("""
    This heatmap shows different types of review scores for each property type. It helps us understand how different property types perform in terms of guest satisfaction.
    """)

    df = pd.read_sql("SELECT * FROM query_3 LIMIT 41", conn)
    pd.set_option('display.float_format', lambda x: '%.2f' % x)

    fig, ax = plt.subplots(figsize=(12, 8))
    sns.heatmap(df.set_index("Property Type"), annot=True, cmap="YlGnBu", ax=ax, fmt=".2f")

    plt.title("Review Scores by Property Type")
    plt.ylabel("Property Type")

    st.pyplot(fig)


def reviews_by_neighborhood_page(conn):
    """
    Renders the Reviews by Neighborhood page with a bar chart showing total reviews and average review score for top neighborhoods.
    """
    st.header("Total Reviews and Average Review Score by Neighborhood")
    st.write("""
    This chart displays the total number of reviews and average review score for top neighborhoods. It helps identify which neighborhoods are most popular and highly rated.
    """)
    df = pd.read_sql("SELECT * FROM query_4 WHERE Neighbourhood IS NOT NULL ORDER BY Total_Reviews DESC LIMIT 20", conn)

    if df.empty:
        st.write("No data available for this visualization.")
        return

    fig, ax1 = plt.subplots(figsize=(12, 6))
    ax2 = ax1.twinx()

    x = range(len(df["Neighbourhood"]))
    ax1.bar(x, df["Total_Reviews"], color='b', alpha=0.7, label='Total Reviews')
    ax2.plot(x, df["Average_Review_Score"], color='r', label='Average Review Score')

    ax1.set_xlabel("Neighborhood")
    ax1.set_ylabel("Total Reviews")
    ax2.set_ylabel("Average Review Score")

    plt.title("Total Reviews and Average Review Score by Neighborhood")
    ax1.set_xticks(x)
    ax1.set_xticklabels(df["Neighbourhood"], rotation=45, ha='right')

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')

    st.pyplot(fig)


import plotly.express as px
import pandas as pd
import streamlit as st

def price_bedrooms_by_property_type_page(conn):
    """
    Renders the Price and Bedrooms by Property Type page with a scatter plot showing the relationship
    between average price and average number of bedrooms for different property types.
    """
    st.header("Average Price and Bedrooms by Property Type")
    st.write("""
    This scatter plot visualizes the relationship between average price and average number of bedrooms 
    for different property types. It helps understand how property characteristics relate to pricing.
    """)
    df = pd.read_sql("SELECT * FROM query_5", conn)

    # Filter data to include only properties with up to 10 bedrooms
    df_filtered = df[df["Average_Bedrooms"] <= 10]

    # Plot using Seaborn with an enhanced color palette
    fig, ax = plt.subplots(figsize=(12, 8))
    scatter = sns.scatterplot(data=df_filtered, x="Average_Bedrooms", y="Average_Price", hue="Property Type", palette="husl", s=100, ax=ax)

    plt.title("Average Price vs Average Number of Bedrooms by Property Type")
    plt.xlabel("Average Number of Bedrooms")
    plt.ylabel("Average Price ($)")
    plt.legend(title="Property Type", bbox_to_anchor=(1.05, 1), loc='upper left')

    st.pyplot(fig)

    # Display summary statistics
    st.subheader("Summary Statistics")
    st.write(f"Total property types shown: {len(df_filtered)}")
    st.write(f"Property type with highest average price: {df_filtered['Property Type'].iloc[df_filtered['Average_Price'].idxmax()]} (${df_filtered['Average_Price'].max():.2f})")
    st.write(f"Property type with most bedrooms on average: {df_filtered['Property Type'].iloc[df_filtered['Average_Bedrooms'].idxmax()]} ({df_filtered['Average_Bedrooms'].max():.2f} bedrooms)")


def interactive_city_comparison_page(conn):
    st.header("Interactive City Comparison")
    st.write("""
    This interactive chart allows you to compare average prices and number of listings across different cities.
    Use the dropdown to select cities for comparison.
    """)

    # Fetch data
    df = pd.read_sql("SELECT * FROM query_1", conn)

    # Allow user to select cities for comparison
    selected_cities = st.multiselect(
        "Select cities to compare",
        options=df['City'].tolist(),
        default=df['City'].tolist()[:5]  # Default to first 5 cities
    )

    # Filter data based on selection
    df_selected = df[df['City'].isin(selected_cities)]

    # Create subplot figure
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Add traces
    fig.add_trace(
        go.Bar(x=df_selected['City'], y=df_selected['Average_Price'], name="Average Price"),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(x=df_selected['City'], y=df_selected['Number_of_Listings'], name="Number of Listings", mode='lines+markers'),
        secondary_y=True,
    )

    # Set x-axis title
    fig.update_xaxes(title_text="City")

    # Set y-axes titles
    fig.update_yaxes(title_text="Average Price ($)", secondary_y=False)
    fig.update_yaxes(title_text="Number of Listings", secondary_y=True)

    # Add title
    fig.update_layout(title_text="Average Price and Number of Listings by City")

    # Show plot
    st.plotly_chart(fig)

    # Display statistics
    st.subheader("Statistics")
    st.write(f"Total cities shown: {len(df_selected)}")
    st.write(f"City with highest average price: {df_selected.loc[df_selected['Average_Price'].idxmax(), 'City']} (${df_selected['Average_Price'].max():.2f})")
    st.write(f"City with most listings: {df_selected.loc[df_selected['Number_of_Listings'].idxmax(), 'City']} ({df_selected['Number_of_Listings'].max()} listings)")

def interactive_property_type_reviews_page(conn):
    st.header("Interactive Property Type Review Scores")
    st.write("""
    This interactive chart allows you to explore review scores across different property types.
    Use the slider to filter property types based on their average review score.
    """)

    # Fetch data
    df = pd.read_sql("SELECT * FROM query_3", conn)

    # Add a slider for filtering based on average review score
    min_score = float(df['Average_Review_Score'].min())
    max_score = float(df['Average_Review_Score'].max())
    score_threshold = st.slider(
        "Filter property types with average review score above:",
        min_value=min_score,
        max_value=max_score,
        value=min_score
    )

    # Filter data based on the slider
    df_filtered = df[df['Average_Review_Score'] >= score_threshold]

    # Create the interactive plot
    fig = px.scatter(
        df_filtered,
        x='Average_Cleanliness_Score',
        y='Average_Location_Score',
        size='Average_Review_Score',
        color='Property Type',
        hover_name='Property Type',
        labels={
            'Average_Cleanliness_Score': 'Cleanliness Score',
            'Average_Location_Score': 'Location Score',
            'Average_Review_Score': 'Overall Review Score'
        }
    )

    fig.update_layout(title="Property Type Review Scores")
    st.plotly_chart(fig)

    # Display statistics
    st.subheader("Statistics")
    st.write(f"Number of property types shown: {len(df_filtered)}")
    st.write(f"Property type with highest overall score: {df_filtered.loc[df_filtered['Average_Review_Score'].idxmax(), 'Property Type']} ({df_filtered['Average_Review_Score'].max():.2f})")
    st.write(f"Property type with highest cleanliness score: {df_filtered.loc[df_filtered['Average_Cleanliness_Score'].idxmax(), 'Property Type']} ({df_filtered['Average_Cleanliness_Score'].max():.2f})")
    st.write(f"Property type with highest location score: {df_filtered.loc[df_filtered['Average_Location_Score'].idxmax(), 'Property Type']} ({df_filtered['Average_Location_Score'].max():.2f})")
def top_cities_by_property_type_page(conn):
    st.header("Top 5 Cities with Highest Average Listing Prices by Property Type (Spark Analysis)")
    st.write("""
    This visualization shows the top 5 cities with the highest average listing prices for each property type,
    based on the Spark analysis of the Airbnb dataset.
    """)

    # Load data
    df = pd.read_sql_query("SELECT * FROM top_cities_by_property_type", conn)

    # Convert the 'top_cities' column from JSON string to list of dicts
    df['top_cities'] = df['top_cities'].apply(json.loads)

    # Select a property type
    property_type = st.selectbox("Select a Property Type", df['property_type'].unique())

    # Filter data for the selected property type
    selected_data = df[df['property_type'] == property_type]['top_cities'].iloc[0]

    # Create lists for city names and average prices
    cities = [city['name'] for city in selected_data]
    prices = [city['avg_price'] for city in selected_data]

    # Create bar chart
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(cities, prices)
    ax.set_xlabel('City')
    ax.set_ylabel('Average Price')
    ax.set_title(f'Top 5 Cities with Highest Average Listing Prices\nfor {property_type}')
    plt.xticks(rotation=45, ha='right')

    # Display the chart
    st.pyplot(fig)

    # Display data in table format
    st.subheader("Data Table")
    table_data = pd.DataFrame(selected_data)
    st.table(table_data)
if __name__ == "__main__":
    main()