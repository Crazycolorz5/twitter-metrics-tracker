import twitter

from auth import ckey, csecret, atkey, atsecret
from time import time, sleep
from random import random

api = twitter.Api(consumer_key= ckey,
                  consumer_secret= csecret,
                  access_token_key= atkey,
                  access_token_secret= atsecret)

trumpID = 25073877 #Twitter ID for realDonaldTrump
minutesToRun = 60*24*7

startTimeline = api.GetUserTimeline(trumpID)
ignoreTweets = set(map(lambda x: x.AsDict()['id'], startTimeline))

trackingStatuses = set() # :: Set (Time, Id)
statusData = dict() # :: Map Id [(Int, Int)]

nextTime = time()

#TODO: Append to files every minute to prevent data loss?
def outputTweet(id, data):
    with open(str(id)+'.csv', 'w') as f:
        f.write("Minutes After Posting,Likes,Retweets\n")
        minsAfter = 0
        for (favorites, retweet_count) in data:
            f.write("%d,%d,%d\n" % (minsAfter, favorites, retweet_count))
            minsAfter = minsAfter + 1

for i in range(minutesToRun): #TODO: Replace with number on minutes to run for. 
    prevTime = nextTime
    nextTime = prevTime + 60
    
    nextStatuses = set()
    
    #Get data for all statuses we're tracking. 
    for (timeAdded, statusID) in trackingStatuses:
        currentStatus = api.GetStatus(statusID).AsDict()
        favorites = currentStatus['favorite_count']
        retweets = currentStatus['retweet_count']
        statusData[statusID].append((favorites, retweets))
        
        # For each status, finalize the data and stop tracking it if sufficiently late.
        if prevTime - timeAdded > 60 * 60 * 24 * 3:
            outputTweet(statusID, statusData[statusID])
            del statusData[statusID]
        else: # Otherwise continue tracking it
            nextStatuses.add((timeAdded, statusID))
    
    # Check for new tweets
    timelineTweets = map(lambda x: x.AsDict(), api.GetUserTimeline(trumpID))
    # From that construct a structure of a dictionary from id to status object (as a dictionary)
    trackedStatuses = set(map(lambda x: x[1], trackingStatuses))
    newTweets = dict()
    for status in timelineTweets:
        statusID = status['id']
        if statusID in ignoreTweets or statusID in trackedStatuses:
            continue
        else:
            newTweets[statusID] = status
    
    for tweet in newTweets:
        # twitter API only allows 900 calls per 15 minutes, which equates to following 60 tweets.
        # to stick to that restriction, I will soft-cap the number of tweets I follow at 65, 
        # But I won't just ignore tweets close to that limit; I'll jsut pick them with lowering probability
        # I'll use min(1, (55 - #following)/15)
        if random() < min(1, (55 - len(nextStatuses))/15):
            nextStatuses.add((prevTime, tweet))
            statusData[tweet] = [(newTweets[tweet]['favorite_count'], newTweets[tweet]['retweet_count'])]
    
    trackingStatuses = nextStatuses
    curTime = time()
    sleep(max(nextTime - curTime, 0))

for tweet in statusData:
    outputTweet(tweet, statusData[tweet])
