import nltk
import tweepy
from textblob import TextBlob

consumer_key= '3JqWefKImV0urjtGIafVEgNbM '
consumer_secret= 'lJTEIWDORWA5N6cEywWolbGnwAgP3tLJMTqMdUlS6rNLGNwGbD'

access_token='1318275138-mO82laAKj6JMsIuqJAtgPHbQ1Sm3eblOuBkcANl'
access_token_secret='PVZJZLacwrSnPbvP5Ki1BkFfuRYww93C6atB2SnEtuRWA'

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)
public_tweets = api.search('bitcoin')

for tweet in public_tweets:
    print(tweet.text)
    
    analysis = TextBlob(tweet.text)
    print(analysis.sentiment)
    print("")