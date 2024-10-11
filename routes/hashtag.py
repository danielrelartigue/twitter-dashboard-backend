from fastapi import APIRouter
from models.hashtag import Hashtag
from models.sensibility import Sensibility
from config.db import database
from schemas.hashtag import hashtagEntity
from schemas.sensibility import sensibilityEntity
from utils.utils import getFirstValue
from bson import ObjectId
from typing import Union

hashtag = APIRouter()
hashtagsCollection = database['hashtags']
twittsCollection = database['twitts']

# Get Methods

# Method to get the sensibility of a hashtag
@hashtag.get("/sensibilityHashtag/{id}", response_model=Union[str, None], tags=["hashtags"])
async def getSensibilityHashtag(id: str):
  sensibilityOfHashtag = await twittsCollection.aggregate([
    {
      '$match': { 'hashtags': { "$in": [ObjectId(id)] } } # We found the twitss that contains the hashtag
    },
    # We unify the collection "sensibility" with a lookup
    {
      '$lookup': {
        'from': 'sensibility', # Origin table that we want the info
        'localField': '_id', # key from the table
        'foreignField': 'id_twitt', # foreignKey from the table
        'as': 'sensibility_info' 
      }
    },
    # We need to make a unwind to descompose the sensibility_info to obtain a doc for each sensibility
    {
      '$unwind': '$sensibility_info'
    },
    # Group by sensibility and count how many are
    {
      '$group': {
        '_id': '$sensibility_info.sentiment',
        'count': { '$sum': 1 }
      }
    },
    # Order the results descending
    {
      '$sort': { 'count': -1 }
    },
    # We get only the first element
    {
      '$limit': 1
    }
  ]).to_list(None)

  sensibility = getFirstValue(sensibilityOfHashtag)

  return sensibility.get('_id', None)

# Method to get the most used hashtag
@hashtag.get("/hashtagMostUsed", response_model=Union[Hashtag, None], tags=["hashtags"])
async def getMostUsedHashtag():
  mostUsed = await hashtagsCollection.find().sort({'num_uses': -1}).limit(1).to_list(None)
  mostUsed = getFirstValue(mostUsed)

  return hashtagEntity(mostUsed)
