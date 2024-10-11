def sensibilityEntity(sensibilityItem) -> dict:
  if not sensibilityItem: return None
  return {
    "id_twitt": str(sensibilityItem["id_twitt"]),
    "confidence": sensibilityItem["confidence"],
    "sentiment": sensibilityItem["sentiment"]
  }

def sensibilitiesEntity(sensibilitiesItem) -> list:
  return [sensibilitiesEntity(sensibility) for sensibility in sensibilitiesItem]