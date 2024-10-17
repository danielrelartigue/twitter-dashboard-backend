from fastapi import FastAPI
from routes.user import user
from routes.twitt import twitt
from routes.hashtag import hashtag
from docs import tags_metadata
import uvicorn
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

# List of allowed domines
origins = [
    'http://localhost',
    'http://localhost:3000' # To consume from frontend in local
    'https://twitter-dashboard-backend-production.up.railway.app'
]

# Load environment
load_dotenv()

app = FastAPI(
  title="REST API with FastAPI and MongoDB",
  description="This is a simple REST API using FastAPI and MongoDB",
  version="0.0.1",
  openapi_tags=tags_metadata
)

# Import user routes
app.include_router(user)
app.include_router(twitt)
app.include_router(hashtag)

# Enable CORS with the middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, # Domines allowed
    allow_credentials=True,
    allow_methods=["*"], # Allow all the HTTP methods
    allow_headers=["*"], # Allow all the headers
    expose_headers=["*"]
)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)