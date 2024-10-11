from fastapi import APIRouter, Response, HTTPException
from config.db import database
from schemas.user import usersEntity, userEntity
from schemas.twitt import twittsEntity, twittEntity
from schemas.hashtag import hashtagEntity
from models.user import User
from models.twitt import Twitt
from models.hashtag import Hashtag
from passlib.hash import sha256_crypt
from bson import ObjectId
from starlette.status import HTTP_204_NO_CONTENT, HTTP_404_NOT_FOUND, HTTP_200_OK
from typing import Union
from utils.utils import getFirstValue

user = APIRouter()
usersCollection = database['users']
twittsCollection = database['twitts']
sensibilityCollection = database['sensibility']
hashtagCollection = database['hashtags']


##### ----- GETTERS ----- #####

# Method to get the information about a user
@user.get("/user/{id}", response_model=Union[User, None], tags=["users"])
async def getUserInfo(id: str):
  user_dict = await usersCollection.find_one({"_id": ObjectId(id)})

  if user_dict is None:
    raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail='User not found')

  return userEntity(user_dict)

# Method to get the twitts of a user
@user.get("/userTwitts/{id}", response_model=Union[list[Twitt], None], tags=["users"])
async def getUserTwitts(id: str, limit: int = 10): # parametro limit opcional si no lo pasan por defecto 10
  user_twitts = await twittsCollection.find({ "user_id": ObjectId(id) }).to_list(length=limit)

  return twittsEntity(user_twitts)


# Method to get the sensibility of a user
@user.get("/userSensibility/{id}", response_model=Union[str, None], tags=["users"])
async def getUserSensibility(id: str):
  sensibilityOfUser = await twittsCollection.aggregate([
    {
      '$match': { 'user_id': ObjectId(id) }
    },
    {
      '$lookup': {
        'from': 'sensibility', # Origin table that we want the info
        'localField': '_id', # Key from the table
        'foreignField': 'id_twitt', # ForeignKey from the table
        'as': 'sensibility_info'
      }
    },
    {
      '$unwind': '$sensibility_info'
    },
    {
      '$group': {
        '_id': '$sensibility_info.sentiment',
        'count': { '$sum': 1 }
      }
    },
    {
      '$sort': { 'count': -1 }
    },
    {
      '$limit': 1
    }
  ]).to_list(None)

  sensibility = getFirstValue(sensibilityOfUser)

  return sensibility.get('_id', None)

# Get most used hashtag of a user
@user.get("/mostUsedHashtag/{id}", response_model=Union[Hashtag, None], tags=["users"])
async def getMostUsedHashtag(id: str):
  mostUsedHashtag = await twittsCollection.aggregate([
    {
      '$match': { 'user_id': ObjectId(id) }
    },
    { # descomponemos los hashtags para tenerlos individuales
      '$unwind': "$hashtags"
    },
    {
      '$group': {
        '_id': '$hashtags',
        'count': { '$sum': 1 }
      }
    },
    {
      '$sort': { 'count': -1 }
    },
    {
      '$limit': 1
    }
  ]).to_list(None)

  hashtag = getFirstValue(mostUsedHashtag)

  if hashtag is None: return None

  hashtag_entity = await hashtagCollection.find_one({ '_id': ObjectId(hashtag['_id'])})

  return hashtagEntity(hashtag_entity)

# Method to get the total likes of a user
@user.get("/userTotalLikes/{id}", response_model=int, tags=["users"])
async def userTotalLikes(id: str):
  totalLikes = await twittsCollection.aggregate([
    {
      '$match': { 'user_id': ObjectId(id) }
    },
    {
      # Add all the likes of the twitts of the user
      '$group': {
        '_id': '$user_id',
        'total_likes': { '$sum': '$num_likes' }
      }
    },
    {
      '$sort': { 'total_likes': -1 }
    },
    {
      '$limit': 1
    }
  ]).to_list(None)

  totalLike = getFirstValue(totalLikes)

  return totalLike.get('total_likes', 0)

# Method to get the total retweets of a user
@user.get("/userTotalRetweets/{id}", response_model=int, tags=["users"])
async def userTotalLikes(id: str):
  totalRetweets = await twittsCollection.aggregate([
    {
      '$match': { 'user_id': ObjectId(id) }
    },
    {
      # Add all the likes of the twitts of the user
      '$group': {
        '_id': '$user_id',
        'total_retweets': { '$sum': '$num_retweets' }
      }
    },
    {
      '$sort': { 'total_retweets': -1 }
    },
    {
      '$limit': 1
    }
  ]).to_list(None)

  totalRetweet = getFirstValue(totalRetweets)

  return totalRetweet.get('total_retweets', 0)

# Method to get the most retwitted post of a user
@user.get("/mostRetwittedTwitt/{id}", response_model=Union[Twitt, None], tags=["users"])
async def getMostRetwittedTwitt(id:str):
  mostRetwittedTwitt = await twittsCollection.aggregate([
    {
      '$match': { 'user_id': ObjectId(id) }
    },
    {
      '$sort': { 'num_retweets': -1 }
    },
    {
      '$limit': 1
    }
  ]).to_list(None)

  twitt = getFirstValue(mostRetwittedTwitt)

  return twittEntity(twitt)

# Method to get the most liked post of a user
@user.get("/mostLikedTwitt/{id}", response_model=Union[Twitt, None], tags=["users"])
async def getMostLikedTwitt(id:str):
  mostLikedTwitt = await twittsCollection.aggregate([
    {
      '$match': { 'user_id': ObjectId(id) }
    },
    {
      '$sort': { 'num_likes': -1 }
    },
    {
      '$limit': 1
    }
  ]).to_list(None)

  twitt = getFirstValue(mostLikedTwitt)

  return twittEntity(twitt)

# Method to get the num of posts of a user
@user.get("/numPostsUser/{id}", response_model=int, tags=["users"])
async def getNumPostsUser(id: str):
  user = await usersCollection.find_one({ '_id': ObjectId(id)}, {'num_posts': 1})

  if user is None:
    raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="User not found")
  
  return user.get('num_posts', 0) # We return a 0 if theres no num_posts

# Method to get the num of followers of a user
@user.get("/numFollowersUser/{id}", response_model=int, tags=["users"])
async def getNumFollowersUser(id: str):
  user = await usersCollection.find_one({ '_id': ObjectId(id)}, {'followers': 1})

  if user is None:
    raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="User not found")
  
  return user.get('followers', 0) # We return a 0 if theres no followers

# Method to get the num of following of a user
@user.get("/numFollowingUser/{id}", response_model=int, tags=["users"])
async def getNumFollowingUser(id: str):
  user = await usersCollection.find_one({ '_id': ObjectId(id)}, {'following': 1})

  if user is None:
    raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="User not found")
  
  return user.get('following', 0) # We return a 0 if theres no followers

# ---------- EXAMPLES ----------

# Get methods  -- WORKS FINE
@user.get("/users", response_model=list[User], tags=["users"])
def find_all_users():
  return usersEntity(conn.sample_mflix.users.find())

# Get User
@user.get("/users/{id}", response_model=Union[User,None], tags=["users"])
def find_user(id: str):
  user = conn.sample_mflix.users.find_one({"_id": ObjectId(id)})
  return userEntity(user)

# Post methods
@user.post("/users", response_model=User, tags=["users"])
def create_user(user: User):
  new_user = dict(user)
  new_user["password"] = sha256_crypt.encrypt(new_user["password"])
  
  id = conn.sample_mflix.users.insert_one(new_user).inserted_id
  user = conn.sample_mflix.users.find_one({"_id": id})

  return userEntity(user)

# Put methods
@user.put("/users/{id}", response_model=User, tags=["users"])
def update_user(id: str, user: User):
  conn.sample_mflix.users.find_one_and_update(
    {"_id": ObjectId(id)}, {"$set": dict(user)})
  
  user = conn.sample_mflix.users.find_one({"_id": ObjectId(id)})
  return userEntity(user)

# Delete methods
@user.delete("/users/{id}", status_code=HTTP_204_NO_CONTENT, tags=["users"])
def delete_user(id: str):
  conn.sample_mflix.users.find_one_and_delete({"_id": ObjectId(id)})
  return Response(status_code=HTTP_204_NO_CONTENT)