from fastapi import FastAPI
from enum import Enum
import httpx # Asynchronous HTTP client

class ModelName(str, Enum):
  alexnet = "alexnet"
  resnet = "resnet"
  lenet = "lenet"

app = FastAPI()

fake_items_db = [
  {"item_name": "Foo"},
  {"item_name": "Bar"},
  {"item_name": "Baz"}
]

@app.get("/")
# Example of call: http://127.0.0.1:8000/
async def root():
  return {"message": "Hello World"}

# ---------- Path Parameters ----------

@app.get("/items/{item_id}")
# Example of call: http://127.0.0.1:8000/items/3
async def read_item(item_id: int):
  return {"item_id": item_id}

@app.get("/users/{user_id}")
# Example of call: http://127.0.0.1:8000/users/you
async def read_user(user_id: str):
  return {"user_id": user_id}

@app.get("/users")
async def read_users():
  return ["Rick", "Morty"]

# Working with Python enumerations
@app.get("/models/{model_name}")
# Example of call: http://127.0.0.1:8000/models/lenet
async def get_model(model_name: ModelName):
  if model_name is ModelName.alexnet:
    return {"model_name": model_name, "message": "Deep Learning FTW!"}
  
  if model_name.value == "lenet":
    return {"model_name": model_name, "message": "LeCNN all the images"}
  
  return {"model_name": model_name, "message": "Have some residuals"}

# Path parameters containing paths
@app.get("/files/{file_path:path}")
# Example of call: http://127.0.0.1:8000/files//home/johndoe/myfile.txt
async def read_file(file_path: str):
  return {"file_path": file_path}

# ---------- Query Parameters ----------
@app.get("/items/")
# Example of call: http://127.0.0.1:8000/items/
# Internally does http://127.0.0.1:8000/items/?skip=0&limit=10
async def read_item(skip: int = 0, limit: int = 10):
  return fake_items_db[skip : skip + limit]

# Optional Parameters
@app.get("/items_queryParam/{item_id}")
# Example of optional parameter
# In this case q is optional and we put a default value as None
# Example of call: http://127.0.0.1:8000/items_queryParam/patata
# Example of call: http://127.0.0.1:8000/items_queryParam/patata?q=mandarina
async def read_item(item_id: str, q: str | None = None):
  if q:
    return {"item_id": item_id, "q": q}
  return {"item_id": item_id}

# Example reading a file
@app.get("/example_reading")
# Example of call: http://127.0.0.1:8000/example_reading
async def example_reading():
  async with httpx.AsyncClient() as client:
    response = await client.get('https://dummyjson.com/c/3029-d29f-4014-9fb4')
    return {"data": response.json()}