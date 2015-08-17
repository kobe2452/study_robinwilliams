import ujson as json
import sys, pickle, timeit, math
from collections import defaultdict

def buildDict(fileName):

    userid_counter = 0
    messageid_counter = 0
    geouser_counter = 0
    user_NO_geo = 0
    tweets_counter = 0
    geotag_tweets = 0
    NOgeo_tweets = 0
    NoGeoUser = 0
    EN_counter = 0
    NoLangTag = 0

    dictionaryUsers = defaultdict(int)
    dictionaryTweets = defaultdict(int)
    dictionaryNoGeoUsers = defaultdict(int)
    
    with open(fileName, 'r') as jsonfile:

        for line in jsonfile:

            line = line.rstrip()
            tweet = json.loads(line)

            ##### USER LEVEL #####
            user = tweet['user']

            if 'id_str' in user:
                userid = user['id_str']
                if userid not in dictionaryUsers:
                	dictionaryUsers[userid] += 1
            else:
                print user    

            if 'geo_enabled' in user:
                geosetting = user['geo_enabled']
                if geosetting is True:
                    geouser_counter += 1
                else:
                    print geosetting
            else:
                user_NO_geo += 1
                if userid not in dictionaryNoGeoUsers:
            		dictionaryNoGeoUsers[userid] += 1


            ##### TWEET LEVEL #####        
            # message = tweet['text']

            messageid = tweet['id']
            if messageid not in dictionaryTweets:
                dictionaryTweets[messageid] += 1

            if 'geo' in tweet:
                geo = (tweet['geo']['latitude'], tweet['geo']['longitude'])
                geotag_tweets += 1
            else:
                NOgeo_tweets += 1

            if 'lang' in tweet:                
                language = tweet['lang']
                if language == 'en':
                    EN_counter +=1
            else:
                NoLangTag += 1 

        userid_counter = len(dictionaryUsers)
        messageid_counter = len(dictionaryTweets)
        NoGeoUser = len(dictionaryNoGeoUsers)

        # display results on console
        print '--------------------'
        print 'unique user IDs: ' + str(userid_counter)
        print 'user profile with (geo_enabled=True): ' + str(geouser_counter)
        print 'user profile without (geo_enabled): ' + str(user_NO_geo) + ' from ' + str(NoGeoUser) + ' user IDs'
        print '--------------------'
        print 'unique message IDs/tweets: ' + str(messageid_counter)
        print 'tweets with geotag: ' + str(geotag_tweets)
        print 'tweets without geotag: ' + str(NOgeo_tweets)
        print 'tweets in English: ' + str(EN_counter) + " Percentage: " + str( float(EN_counter)/float(messageid_counter)*100 )
        print 'tweets without Language Tag: ' + str(NoLangTag)
        print '--------------------'

def main():

    # mark the beginning time of process
    start = timeit.default_timer()
    
    fileName = 'oneyear_sample.json'
    print 'Analyzing the file: ' + fileName

    buildDict(fileName)

    ##### mark the ending time of process #####
    end = timeit.default_timer()
    seconds = math.ceil(end - start)
    # Convert Secs Into Human Readable Time String (HH:MM:SS)
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    print "This process took %d:%02d:%02d" % (h, m, s)
    
if __name__ == '__main__':
    main()

