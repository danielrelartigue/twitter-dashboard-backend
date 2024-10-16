from fastapi import APIRouter, HTTPException
from typing import Union
from models.twitt import Twitt
from models.user import User
from models.hashtag import Hashtag
from models.sensibility import Sensibility
from config.db import database
from bson import ObjectId
from schemas.twitt import twittEntity, twittsEntity
from schemas.hashtag import hashtagsEntity
from schemas.sensibility import sensibilityEntity
from schemas.user import userEntity
from datetime import datetime
from utils.utils import getFirstValue, getValueFromDict
from starlette.status import HTTP_204_NO_CONTENT, HTTP_404_NOT_FOUND, HTTP_200_OK, HTTP_400_BAD_REQUEST
from utils.analyze import analyze_tweet_emotions
from fastapi.encoders import jsonable_encoder

twitt = APIRouter()
twittsCollection = database['twitts']
sensibilityCollection = database['sensibility']
usersCollection = database['users']
hashtagsCollection = database['hashtags']

##### ----- GETTERS ----- #####

# Method to get the information about a twitt
@twitt.get("/twitt/{id}", response_model=Union[Twitt, None], tags=["twitts"])
async def getTwittInfo(id: str):
  twitt_dict = await twittsCollection.find_one({"_id": ObjectId(id)})

  if twitt_dict is None:
    raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='Twitt not found')

  return twittEntity(twitt_dict)

# Method to get the user information of a twitt
@twitt.get("/twittUser/{id}", response_model=Union[User, None], tags=["twitts"])
async def getTwittUser(id: str):
  twitt_dict = await twittsCollection.find_one({"_id": ObjectId(id)})

  if twitt_dict is None:
    raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='Twitt not found')

  user_id = getValueFromDict(twitt_dict, 'user_id')

  user_dict = await usersCollection.find_one({"_id": user_id})

  if user_dict is None:
    raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='User associate to twitt not found')

  return userEntity(user_dict)

# Method to get the hashtags of a twitt
@twitt.get("/twittHashtags/{id}", response_model=Union[list[Hashtag], None], tags=["twitts"])
async def getTwittHashtags(id: str):
  twitt_dict = await twittsCollection.find_one({"_id": ObjectId(id)})

  if twitt_dict is None:
    raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='Twitt not found')

  hashtags_of_twitt = getValueFromDict(twitt_dict, 'hashtags')

  hashtagsModels = await hashtagsCollection.find({ "_id": { "$in": hashtags_of_twitt }}).to_list(None)
  return hashtagsEntity(hashtagsModels)

# Method to get the creation date of a twitt
@twitt.get("/twittCreationDate/{id}", response_model=Union[datetime, None], tags=["twitts"])
async def getTwittCreationDate(id: str):
  twitt_dict = await twittsCollection.find_one({"_id": ObjectId(id)})
  
  if twitt_dict is None:
    raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='Twitt not found')

  created_date = getValueFromDict(twitt_dict, 'created_at')
  
  return created_date

# Method to get the sensibility of a twitt
@twitt.get("/twittSensibility/{id}", response_model=Union[Sensibility, None], tags=["twitts"])
async def getTwittSensibility(id: str):
  twitt_dict = await twittsCollection.find_one({"_id": ObjectId(id)})

  if twitt_dict is None:
    raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='Twitt not found')

  sensibility_id = getValueFromDict(twitt_dict, 'sensibility_id')

  sensibility_dict = await sensibilityCollection.find_one({"_id": sensibility_id})

  if sensibility_dict is None:
    raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='Sensibility associate to twitt not found')

  return sensibilityEntity(sensibility_dict)

# Method to get the most popular twitts
#TODO: Improve metrics for popularity of a twitt
@twitt.get("/mostPopularsTwitts", response_model=list[Twitt], tags=["twitts"])
async def getMostPopularTwitts(limit: int = 10): # parametro limit opcional si no lo pasan por defecto 10
  mostPopularTwitts = await twittsCollection.aggregate([
    {
      '$addFields': {
        'total': { '$sum': ['$num_likes', '$num_retweets'] }
      }
    },
    {
      '$sort': { 'total': -1 }
    },
    {
      '$limit': limit
    }
  ]).to_list(None)

  return twittsEntity(mostPopularTwitts)

# Method to get the most retwitted twitt
@twitt.get("/mostRetwittedTwitt", response_model=Union[Twitt, None], tags=["twitts"])
async def getMostRetwittedTwitts():
  mostRetwittedTwitt = await twittsCollection.aggregate([
    {
      '$sort': { 'num_retweets': -1 }
    },
    {
      '$limit': 1
    }
  ]).to_list(None)

  mostRetwittedTwitt = getFirstValue(mostRetwittedTwitt)

  return twittEntity(mostRetwittedTwitt)

# Method to get the most liked twitt
@twitt.get("/mostLikedTwitt", response_model=Union[Twitt, None], tags=["twitts"])
async def getMostLikedTwitts():
  mostLikedTwitt = await twittsCollection.aggregate([
    {
      '$sort': { 'num_likes': -1 }
    },
    {
      '$limit': 1
    }
  ]).to_list(None)

  mostLikedTwitt = getFirstValue(mostLikedTwitt)

  return twittEntity(mostLikedTwitt)

# Method to get twitts by a sensibility
@twitt.get("/twittsBySensibility", response_model=list[Twitt], tags=["twitts"])
async def getTwittsBySensibility(sensibilityId: str):

  twittsBySensibility = await twittsCollection.find({ "sensibility_id": ObjectId(sensibilityId) }).to_list(None)

  return twittsEntity(twittsBySensibility)

# Method to get the twitts between two dates
@twitt.get("/twittsBetweenDates", response_model=list[Twitt], tags=["twitts"])
async def getTwittsBetweenDates(startDate: str, endDate: str):

  try:
    start_date_obj = datetime.strptime(startDate, "%Y-%m-%d")
    end_date_obj = datetime.strptime(endDate, '%Y-%m-%d')
  except ValueError:
    raise HTTPException(status_code = HTTP_400_BAD_REQUEST, detail="Invalid date format. Use YYYY-MM-DD.")

  twittsBetweenDates = await twittsCollection.find({
    'created_at': {
      '$gte': start_date_obj,
      '$lte': end_date_obj
    }
  }).to_list(None)

  return twittsEntity(twittsBetweenDates)

# Method to calculate the sentiments of a twitt
@twitt.get("/calculateTwittAnalysis/{id}", response_model=dict, tags=["twitts"])
async def calculateTwittAnalysis(id: str):

  twitt_dict = await twittsCollection.find_one({"_id": ObjectId(id)})

  if twitt_dict is None:
    raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='Twitt not found')
  
  emotions = analyze_tweet_emotions(getValueFromDict(twitt_dict, 'message'))

  return {"emotions": emotions}

# Method to caculate the max sentiment of a twitt
@twitt.get("/calculateMaxTwittSentiment/{id}", response_model=str, tags=["twitts"])
async def calculateMaxTwittSentiment(id: str):

  twitt_dict = await twittsCollection.find_one({"_id": ObjectId(id)})

  if twitt_dict is None:
    raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail='Twitt not found')
  
  emotions = analyze_tweet_emotions(getValueFromDict(twitt_dict, 'message'))

  return max(emotions, key=emotions.get)

# Method to update the sentiment of a twitt
@twitt.patch("/recalculateSentiment/{id}", response_model=dict, tags=["twitts"])
async def recalculateSentiment(id: str):

  # Calculate the new sentiment and score
  twitt_dict = await twittsCollection.find_one({"_id": ObjectId(id)})

  if twitt_dict is None:
    raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail='Twitt not found')
  
  emotions = analyze_tweet_emotions(getValueFromDict(twitt_dict, 'message'))

  max_emotion = max(emotions, key=emotions.get)
  max_score = emotions[max_emotion]

  # Update the sentiment with the new values
  updated_sensibility = await sensibilityCollection.find_one_and_update(
    {'id_twitt': ObjectId(id)}, # Search by twitt id
    {'$set': {'sentiment': max_emotion, 'confidence': max_score}},  # Update the fields
    return_document=True # Return the document updated
  )

  if not updated_sensibility:
    raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='Twitt sensibility not found')
  
  return {'message': 'Sentiment and confidence updated successfully', 'sensibility': sensibilityEntity(updated_sensibility)}
  