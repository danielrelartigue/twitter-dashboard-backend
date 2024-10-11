def userEntity(userItem) -> dict:
  if not userItem: return None
  return {
    #"id": str(userItem["_id"]),
    "username": userItem["username"],
    "following": userItem["following"],
    "followers": userItem["followers"],
    "num_posts": userItem["num_posts"]
  }

def usersEntity(usersItem) -> list:
  return [userEntity(user) for user in usersItem]