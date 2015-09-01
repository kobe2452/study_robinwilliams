# python find_users.py  ../13-2015_master_user_list.json pipe-3.pkl entity_data_all.json > entity_data.json

from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy import API
import tweepy
import datetime
import time
import sys
import json
import pickle
from sklearn.decomposition import TruncatedSVD

# Go to http://dev.twitter.com and create an app. 
# The consumer key and secret will be generated for you after
consumer_key=""
consumer_secret=""

# After the step above, you will be redirected to your app's page.
# Create an access token under the the "Your access token" section
access_token=""
access_token_secret=""

class BalancingTruncatedSVD(TruncatedSVD):
    balance = 0

class StdOutListener(StreamListener):
	""" A listener handles tweets are the received from the stream. 
	This is a basic listener that just prints received tweets to stdout.

	"""
	def on_data(self, data):
		print data
		return True

	def on_error(self, status):
		print status

if __name__ == '__main__':
    
    f = open(sys.argv[1])
    ul = json.load(f)
    f.close()
    f = open (sys.argv[2])
    userlist, entitylist, logistic = pickle.load(f)
    f.close()
    
    us = set()
    f = open (sys.argv[3]) 
    while True:
        try:
            line = f.readline()
            if line == "":
                break
            user = json.loads(line)
            us.add(user["id"])
        except (KeyError, ValueError):
            sys.stderr.write(line)
    f.close ()
    us = us | {int(k) for k in ul}
    ones_we_need = list(set(entitylist) - us)
    sys.stderr.write( "number of entities to gather %d\n" % len(ones_we_need))
    
    #sys.exit(0)

    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = API(auth_handler = auth,parser=tweepy.parsers.JSONParser())
    
    i = 0
    l = 0
    while i < len(ones_we_need):
        current_time = datetime.datetime.now()

        try:
            l = 0
            for k in range(180):
                offset = min(100, len(ones_we_need) - i - 1)
                sublist = [ones_we_need[j] for j in range(i, i+offset)]
                users = api.lookup_users(user_ids = sublist)
                for u in users:
                    print json.dumps(u)
                i += 100
                l += 1
        except tweepy.error.TweepError:
            sys.stderr.write ("%d\n" % l)
            time.sleep(900)

        while datetime.datetime.now() - current_time < datetime.timedelta(minutes=15):

            time.sleep(1)



        
