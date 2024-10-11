def getFirstValue(list):

  return None if (list is None or not list) else list[0]

def getValueFromDict(dict, valueToGet):
  
  return None if dict is None else dict[valueToGet]