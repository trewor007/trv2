import sys
import nltk
import tweepy
from textblob import TextBlob
from hashtag_generator import twitter_consumer_key, twitter_consumer_secret, twitter_access_token, twitter_access_token_secret

#consumer_key='3JqWefKImV0urjtGIafVEgNbM'
#consumer_secret='lJTEIWDORWA5N6cEywWolbGnwAgP3tLJMTqMdUlS6rNLGNwGbD'

#access_token='1318275138-aaMxCc6XurOTNMBzHfQykwHkCHRwMxkWYVbTXtk'
#access_token_secret='vMLLtaH3n0wAOcWvmz4acvG3scLQIUm37EGM0sTqy3EPk'

frazebook=['bitcoin','#bitcoin','btc','#btc','Bitcoin','#Bitcoin','BTC','#BTC', 'etc']
trend=[]
non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd) #magic fucking magic

auth = tweepy.OAuthHandler(twitter_consumer_key, twitter_consumer_secret)
auth.set_access_token(twitter_access_token, twitter_access_token_secret)

api = tweepy.API(auth)

for fraze in frazebook:
    public_tweets = api.search(fraze)
    for tweet in public_tweets:
        analysis = TextBlob(tweet.text)
        language=analysis.detect_language()
        if language== 'en' or 'pl':
            text=tweet.text
            print(text.translate(non_bmp_map))
            print(analysis.sentiment)
            trend.append(analysis.sentiment.polarity)
            print('=================================')
average_trend=sum(trend)/len(trend)
print(average_trend)

