from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os

load_dotenv() # load environment

#Load environment variables
uri = os.getenv("MONGO_DB_ENDPOINT")
database_name = os.getenv("DATABASE_NAME")

# Create a new client and connect to the server
client = AsyncIOMotorClient(uri)
database = client[database_name]