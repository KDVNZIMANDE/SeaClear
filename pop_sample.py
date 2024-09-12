from pymongo import MongoClient
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
from bson.objectid import ObjectId
import random

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['seaclear_db']  # Replace with your actual database name

# Sample data
beaches = [
    {
        "name": "Clifton 4th Beach",
        "location": "Cape Town",
        "location_code": "42296bc2c1671fda7fbea0de323ce93b9555d49bf20580698170e21e53b006d3772f84ec8a83e6a364b501d665b18857",
        "longitude": "18.3738",
        "latitude": "-33.9415",
        "date": datetime.now().strftime("%Y-%m-%d"),
        "description": "A popular beach known for its pristine sands and clear waters. It’s perfect for sunbathing and social gatherings.",
        "entrocciticount": "0",
        "grade": "A",
        "temperature": "23°C",
        "wind_speed": "25 km/h",
        "wind_direction": "NW",
        "status": "SAFE",
        "map_image": "clifton_4th.jpg",
        "has_amenities": True,
        "amenities": ["Restrooms", "Parking", "Lifeguard", "Showers"] 
    },
    {
        "name": "Muizenberg Beach",
        "location": "Cape Town",
        "location_code": "b12720131d19c2b739cb580403d5572ecad354f5fde1569b17403c827d762571",
        "longitude": "18.4959",
        "latitude": "-34.0899",
        "date": datetime.now().strftime("%Y-%m-%d"),
        "description": "Ideal for surfing, Muizenberg Beach is known for its colorful beach huts and vibrant energy.",
        "entrocciticount": "5",
        "grade": "B",
        "temperature": "20°C",
        "wind_speed": "15 km/h",
        "wind_direction": "S",
        "status": "SAFE",
        "map_image": "muizenberg.jpg",
        "has_amenities": True,
        "amenities": ["Restrooms", "Parking", "Surfing Rentals", "Showers"] 
    },
    {
        "name": "Bloubergstrand",
        "location": "Cape Town",
        "location_code": "b12720131d19c2b739cb580403d5572ecad354f5fde1569b17403c827d762571",
        "longitude": "18.4866",
        "latitude": "-33.8194",
        "date": datetime.now().strftime("%Y-%m-%d"),
        "description": "Famous for its view of Table Mountain, Bloubergstrand is a favorite spot for kite-surfers and windsurfers.",
        "entrocciticount": "1",
        "grade": "A",
        "temperature": "21°C",
        "wind_speed": "28 km/h",
        "wind_direction": "W",
        "status": "SAFE",
        "map_image": "bloubergstrand.jpg",
        "has_amenities": True,
        "amenities": ["Restrooms", "Parking", "Lifeguard", "Restaurants"] 
    },
    {
        "name": "Camps Bay",
        "location": "Cape Town",
        "location_code": "c71de04f2ebf9c7b62263b2f59e6168bfc69b4f86ea7a98b485649b6d998d158",
        "longitude": "18.3762",
        "latitude": "-33.9519",
        "date": datetime.now().strftime("%Y-%m-%d"),
        "description": "Camps Bay is Cape Town's famous beach with palm-lined shores, perfect for swimming and sundowners.",
        "entrocciticount": "2",
        "grade": "A",
        "temperature": "22°C",
        "wind_speed": "18 km/h",
        "wind_direction": "SE",
        "status": "SAFE",
        "map_image": "camps_bay.jpg",
        "has_amenities": True,
        "amenities": ["Restrooms", "Parking", "Lifeguard", "Showers", "Restaurants"] 
    },
    {
        "name": "Boulders Beach",
        "location": "Simon's Town, Cape Town",
        "location_code": "de837fa65d0d36e1ea158b047b4fd401f6eeb4c88d46ff5fc249258498ab53f9",
        "longitude": "18.4512",
        "latitude": "-34.1974",
        "date": datetime.now().strftime("%Y-%m-%d"),
        "description": "Boulders Beach is home to a colony of African penguins, making it a top attraction for visitors.",
        "entrocciticount": "0",
        "grade": "A",
        "temperature": "21°C",
        "wind_speed": "10 km/h",
        "wind_direction": "E",
        "status": "SAFE",
        "map_image": "boulders_beach.jpg",
        "has_amenities": True,
        "amenities": ["Restrooms", "Parking", "Penguin Viewing"] 
    },
    {
        "name": "Hout Bay Beach",
        "location": "Cape Town",
        "location_code": "1ef2d3bd05c7e5fd3c41d8074d29a5e9d7287e39390fe030faacdbd6c9a9d42e",
        "longitude": "18.3418",
        "latitude": "-34.0455",
        "date": datetime.now().strftime("%Y-%m-%d"),
        "description": "Hout Bay Beach is a great spot for families, with gentle waves and a nearby fishing village for fresh seafood.",
        "entrocciticount": "3",
        "grade": "B",
        "temperature": "19°C",
        "wind_speed": "14 km/h",
        "wind_direction": "NW",
        "status": "SAFE",
        "map_image": "hout_bay.jpg",
        "has_amenities": True,
        "amenities": ["Restrooms", "Parking", "Fishing Village", "Restaurants"] 
    },
    {
        "name": "Fish Hoek Beach",
        "location": "Cape Town",
        "location_code": "b92f33d0a273bf4d51a0276a2b3c29b133f902e5167c9297d8e987e1e99c70de",
        "longitude": "18.4295",
        "latitude": "-34.1378",
        "date": datetime.now().strftime("%Y-%m-%d"),
        "description": "A calm and family-friendly beach, great for swimming and picnicking along the shore.",
        "entrocciticount": "1",
        "grade": "A",
        "temperature": "22°C",
        "wind_speed": "20 km/h",
        "wind_direction": "SW",
        "status": "SAFE",
        "map_image": "fish_hoek.jpg",
        "has_amenities": True,
        "amenities": ["Restrooms", "Parking", "Lifeguard", "Playground"] 
    },
    {
        "name": "Noordhoek Beach",
        "location": "Cape Town",
        "location_code": "1e6f27cccf781237fbcfd5c621c2b7d710d69c1e7d55507f0f4b2fb5a8e2b417",
        "longitude": "18.3674",
        "latitude": "-34.0877",
        "date": datetime.now().strftime("%Y-%m-%d"),
        "description": "A vast, tranquil beach ideal for horse riding and long walks. It offers a serene escape from the city.",
        "entrocciticount": "2",
        "grade": "A",
        "temperature": "18°C",
        "wind_speed": "12 km/h",
        "wind_direction": "SE",
        "status": "UNSAFE",
        "map_image": "noordhoek.jpg",
        "has_amenities": True,
        "amenities": ["Parking", "Horse Riding", "Scenic Views"] 
    },
    {
        "name": "Llandudno Beach",
        "location": "Cape Town",
        "location_code": "2fc6e18f389658129b9b92c97e5b6fdc490cf72f02c41649c96c32882d91cfd5",
        "longitude": "18.3320",
        "latitude": "-34.0017",
        "date": datetime.now().strftime("%Y-%m-%d"),
        "description": "A hidden gem, Llandudno Beach is surrounded by rocky outcrops, perfect for bodyboarding and sunsets.",
        "entrocciticount": "0",
        "grade": "A",
        "temperature": "20°C",
        "wind_speed": "25 km/h",
        "wind_direction": "NW",
        "status": "SAFE",
        "map_image": "llandudno.jpg",
        "has_amenities": True,
        "amenities": ["Restrooms", "Parking", "Lifeguard"] 
    },
    {
        "name": "Bakoven Beach",
        "location": "Cape Town",
        "location_code": "f4b70224e4e0abf5be3f1d3d4b3e8192fe93e896d04d06f62778e82ed7ed58f9",
        "longitude": "18.3756",
        "latitude": "-33.9572",
        "date": datetime.now().strftime("%Y-%m-%d"),
        "description": "A small, secluded beach with beautiful rock formations, perfect for a quiet retreat and snorkelling.",
        "entrocciticount": "0",
        "grade": "A",
        "temperature": "22°C",
        "wind_speed": "16 km/h",
        "wind_direction": "E",
        "status": "UNSAFE",
        "map_image": "bakoven.jpg",
        "has_amenities": True,
        "amenities": ["Parking", "Scenic Views", "Snorkelling"] 
    }
]


users = [
    {
        "email": "user1@example.com",
        "password": generate_password_hash("password123", method="pbkdf2:sha256", salt_length=8),
        "username": "User One",
        "role": "user"
    },
    {
        "email": "admin@example.com",
        "password": generate_password_hash("adminpass", method="pbkdf2:sha256", salt_length=8),
        "username": "Admin User",
        "role": "admin"
    }
]

# Insert data into collections
beach_collection = db.beaches
user_collection = db.users
# post_collection = db.posts

# Insert beaches
beach_result = beach_collection.insert_many(beaches)
print(f"Inserted {len(beach_result.inserted_ids)} beaches")

# Insert users
user_result = user_collection.insert_many(users)
print(f"Inserted {len(user_result.inserted_ids)} users")

print("Sample data insertion complete!")