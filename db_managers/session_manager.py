from motor.motor_asyncio import AsyncIOMotorClient
from bson.objectid import ObjectId

client = AsyncIOMotorClient(
    "mongodb+srv://sugoto:1111@rpg.bhwib.mongodb.net/?retryWrites=true&w=majority&appName=rpg"
)
db = client["fractal_rpg"]
collection = db["sessions"]


async def save_message(user_id, message):
    user_id = ObjectId(user_id)
    user = await collection.find_one({"_id": user_id})
    new_message = {"id": 0, "message": message}
    if user:
        message_id = len(user.get("messages", []))
        new_message["id"] = message_id
        await collection.update_one(
            {"_id": user_id}, {"$push": {"messages": new_message}}
        )
    else:
        await collection.insert_one({"_id": user_id, "messages": [new_message]})


async def get_messages(user_id):
    user_id = ObjectId(user_id)
    user = await collection.find_one({"_id": user_id})
    if user:
        return user.get("messages", [])
    else:
        return []
