from transformers import pipeline

# Load the pipeline de análisis de emociones
#TODO: Make it multilanguage
emotion_classifier = pipeline('text-classification', model='j-hartmann/emotion-english-distilroberta-base', return_all_scores=True)

def analyze_tweet_emotions(tweet):

  result = emotion_classifier(tweet)

  emotions = {emotion['label']: round(emotion['score'], 4) for emotion in result[0]}

  return emotions