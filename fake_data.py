from faker import Faker
import json
import random

print("Starting script...")

fake = Faker()


def generate_airbnb_listing():
    property_type = random.choice(["Apartment", "House", "Loft", "Villa", "Condo"])

    # Define base price ranges for each property type
    base_price_ranges = {
        "Apartment": (50, 300),
        "House": (100, 500),
        "Loft": (80, 400),
        "Villa": (300, 1500),
        "Condo": (70, 350)
    }

    # Generate a city-specific multiplier
    city_multiplier = random.uniform(0.8, 1.2)

    min_price, max_price = base_price_ranges[property_type]

    # Apply the city multiplier to the price range
    adjusted_min_price = min_price * city_multiplier
    adjusted_max_price = max_price * city_multiplier

    # Generate the price with added randomness
    price = round(random.uniform(adjusted_min_price, adjusted_max_price) * random.uniform(0.9, 1.1), 2)

    return {
        "id": fake.uuid4(),
        "name": fake.city(),  # Use city name instead of catch phrase for more realistic names
        "host": {
            "id": fake.uuid4(),
            "name": fake.name(),
            "location": fake.city(),
            "response_rate": round(random.uniform(0.5, 1.0), 2)
        },
        "city": {
            "name": fake.city(),
            "country": fake.country()
        },
        "price": price,
        "bedrooms": random.randint(1, 5),
        "property_type": property_type,
        "room_type": random.choice(["Entire home/apt", "Private room", "Shared room"]),
        "amenities": random.sample(["Wifi", "Kitchen", "Washer", "Dryer", "Air conditioning", "Heating", "TV", "Pool"],
                                   k=random.randint(3, 8))
    }

print("Generating listings...")

listings = []
target_size = 70 * 1024 * 1024  # 70MB in bytes
current_size = 0
batch_size = 1000

while current_size < target_size:
    new_listings = [generate_airbnb_listing() for _ in range(batch_size)]
    listings.extend(new_listings)
    current_size = len(json.dumps(listings).encode('utf-8'))
    print(f"Generated {len(listings)} listings. Current size: {current_size / (1024 * 1024):.2f} MB")

print("Saving full dataset...")

# Save full dataset
with open('airbnb_listings.json', 'w') as f:
    json.dump(listings, f)

print("Saving sample of 50 records...")

# Save sample of 50 records
with open('airbnb_listings_sample.json', 'w') as f:
    json.dump(listings[:50], f, indent=2)

print(f"Generated {len(listings)} listings")

print("\nDisplaying sample data:")

# Display the first 5 records from the sample
for i, listing in enumerate(listings[:5], 1):
    print(f"\nListing {i}:")
    print(f"Name: {listing['name']}")
    print(f"City: {listing['city']['name']}, {listing['city']['country']}")
    print(f"Price: ${listing['price']}")
    print(f"Property Type: {listing['property_type']}")
    print(f"Bedrooms: {listing['bedrooms']}")
    print(f"Host: {listing['host']['name']}")
    print(f"Amenities: {', '.join(listing['amenities'][:3])}...")  # Show first 3 amenities

print("\n... (remaining listings truncated)")

print("Script completed.")