def twittEntity(twittItem) -> dict:
  if not twittItem: return None
  return {
    #"id": str(twittItem["_id"]),
    "user_id": str(twittItem["user_id"]),
    "message": twittItem["message"],
    "num_likes": twittItem["num_likes"],
    "num_retweets": twittItem["num_retweets"],
    "created_at": twittItem["created_at"],
    "hashtags": twittItem["hashtags"]
  }

def twittsEntity(twittsItem) -> list:
  return [twittEntity(twitt) for twitt in twittsItem]
