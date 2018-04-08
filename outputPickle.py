from pickle import *

#TODO: Append to files every minute to prevent data loss?
def outputTweet(id, data):
    with open(str(id)+'.csv', 'w') as f:
        f.write("Minutes After Posting,Likes,Retweets\n")
        minsAfter = 0
        for (favorites, retweet_count) in data:
            f.write("%d,%d,%d\n" % (minsAfter, favorites, retweet_count))
            minsAfter = minsAfter + 1

if __name__ == "__main__":
	with open('data.pickle', 'rb') as f:
		data = load(f)
	for tweet in data:
		outputTweet(tweet, data[tweet])
