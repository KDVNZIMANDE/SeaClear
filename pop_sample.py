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
        "description": "temp",
        "entrocciticount": "0",
        "grade": "A",
        "temperature": "23°C",
        "wind_speed": "25 km/h",
        "wind_direction": "NW",
        "status": "SAFE",
        "map_image": "clifton_4th.jpg",
        "has_amenities": True,
        "amenities": ["Restrooms", "Parking", "Lifeguard"] 
    },
    {
        "name": "Muizenberg Beach",
        "location": "Cape Town",
        "location_code": "b12720131d19c2b739cb580403d5572ecad354f5fde1569b17403c827d762571",
        "longitude": "18.4959",
        "latitude": "-34.0899",
        "date": datetime.now().strftime("%Y-%m-%d"),
        "description": "temp",
        "entrocciticount": "5",
        "grade": "B",
        "temperature": "23°C",
        "wind_speed": "25 km/h",
        "wind_direction": "NW",
        "status": "SAFE",
        "map_image": "muizenberg.jpg",
        "has_amenities": True,
        "amenities": ["Restrooms", "Parking", "Lifeguard"] 
    },
    {
        "name": "Bloubergstrand",
        "location": "Cape Town",
        "location_code": "b12720131d19c2b739cb580403d5572ecad354f5fde1569b17403c827d762571",
        "longitude": "18.4866",
        "latitude": "-33.8194",
        "date": datetime.now().strftime("%Y-%m-%d"),
        "description": "temp",
        "entrocciticount": "1",
        "grade": "A",
        "temperature": "23°C",
        "wind_speed": "25 km/h",
        "wind_direction": "NW",
        "status": "SAFE",
        "map_image": "bloubergstrand.jpg",
        "has_amenities": True,
        "amenities": ["Restrooms", "Parking", "Lifeguard"] 
    },
    {
        "name": "Camps Bay",
        "location": "Cape Town",
        "location_code": "b12720131d19c2b739cb580403d5572ecad354f5fde1569b17403c827d762571",
        "longitude": "18.4866",
        "latitude": "-33.8194",
        "date": datetime.now().strftime("%Y-%m-%d"),
        "description": "temp",
        "entrocciticount": "1",
        "grade": "A",
        "temperature": "23°C",
        "wind_speed": "25 km/h",
        "wind_direction": "NW",
        "status": "SAFE",
        "map_image": "bloubergstrand.jpg",
        "has_amenities": True,
        "amenities": ["Restrooms", "Parking", "Lifeguards", "Showers"] 
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

# Function to generate random posts
# def generate_posts(beach_ids, user_ids):
#     posts = []
#     for _ in range(10):  # Generate 10 sample posts
#         posts.append({
#             "content": f"Sample post content {random.randint(1, 100)}",
#             "timestamp": (datetime.now() - timedelta(days=random.randint(0, 30))).strftime("%Y-%m-%d %H:%M:%S"),
#             "status": random.choice(["active", "approved"]),
#             "likes": random.randint(0, 100),
#             "beach_id": ObjectId(random.choice(beach_ids)),
#             "user_id": random.choice(user_ids)
#         })
#     return posts

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

# Generate and insert posts
# posts = generate_posts(beach_result.inserted_ids, user_result.inserted_ids)
# post_result = post_collection.insert_many(posts)
# print(f"Inserted {len(post_result.inserted_ids)} posts")

print("Sample data insertion complete!")