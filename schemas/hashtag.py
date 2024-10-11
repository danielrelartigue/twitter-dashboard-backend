def hashtagEntity(hashtagItem) -> dict:
  if not hashtagItem: return None
  return {
    "title": hashtagItem["title"]
  }

def hashtagsEntity(hashtagsItem) -> list:
  return [hashtagEntity(hashtag) for hashtag in hashtagsItem]