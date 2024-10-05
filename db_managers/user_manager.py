from motor.motor_asyncio import AsyncIOMotorClient

client = AsyncIOMotorClient(
    "mongodb+srv://sugoto:1111@rpg.bhwib.mongodb.net/?retryWrites=true&w=majority&appName=rpg"
)
db = client["fractal_rpg"]
collection = db["users"]

class_attributes = {
    "Warrior": {
        "abilities": {"STR": 3, "DEX": 2, "CON": 1, "INT": 0, "WIS": 1, "CHA": -1},
        "equipment": ["Sword", "Shield", "Steel Armor"],
        "hp": 25,
        "ac": 16,
        "gold": 50,
    },
    "Rogue": {
        "abilities": {"STR": 0, "DEX": 3, "CON": 1, "INT": 1, "WIS": -1, "CHA": 2},
        "equipment": ["Daggers", "Thieves' Tools", "Leather Armor"],
        "hp": 20,
        "ac": 14,
        "gold": 100,
    },
    "Artificer": {
        "abilities": {"STR": -1, "DEX": 0, "CON": 1, "INT": 3, "WIS": 2, "CHA": 1},
        "equipment": ["Crossbow", "Tinker's Tools", "Mage's Robes"],
        "hp": 15,
        "ac": 12,
        "gold": 50,
    },
    "Skyseer": {
        "abilities": {"STR": 1, "DEX": 0, "CON": 2, "INT": 0, "WIS": 3, "CHA": 2},
        "equipment": ["Staff", "Star Dust", "Mystical Robes"],
        "hp": 15,
        "ac": 12,
        "gold": 25,
    },
}


async def save_user(char_name, username, class_name):
    attributes = class_attributes[class_name]
    await collection.update_one(
        {"_id": username},
        {"$set": {"char_name": char_name, "username": username, **attributes}},
        upsert=True,
    )


async def get_user(username):
    user = await collection.find_one({"_id": username})
    return user
