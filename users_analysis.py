import ujson as json
import timeit, math, csv
from collections import defaultdict, OrderedDict
import matplotlib.pyplot as plt
import plotly.plotly as py

def count_users_tweets(json_data):

    user_profile = defaultdict(list)

    for line in open(json_data, "r"):
        tweet = json.loads(line.decode('utf-8'))

        if 'lang' in tweet:                
            language = tweet['lang']

            # Only process and analyze tweets written in English
            if language == 'en':

                message = tweet['text']
                msg_id = tweet['id']

                user = tweet['user']
                user_id = user['id_str']

                user_profile[user_id].append(msg_id)

    return user_profile

def cluster_users_by_tweets_count(user_profile):

    tweets_count_dict = defaultdict(list)

    for k, v in user_profile.items():

        user_id = k
        tweets = len(v)

        tweets_count_dict[tweets].append(user_id)

    # print "number of tweets matched -- how many users in our dataset"
    # for k in OrderedDict(sorted(tweets_count_dict.items(), key=lambda t: t[0])):
    #     print k, len(tweets_count_dict[k])

    # print "user_id sorted -- number of tweets"
    # for k in OrderedDict(sorted(user_profile.items(), key=lambda t: len(t[1]))):
    #     print k, len(user_profile[k])

    return tweets_count_dict

def find_users_before_after_event(before_tweets, after_tweets, user_profile):
    
    before_users = defaultdict(list)
    after_users = defaultdict(list)

    for k, v in user_profile.items():
        user_id = k
        for msg_id in v:
            if msg_id in before_tweets:
                before_users[user_id].append(msg_id)
            elif msg_id in after_tweets:
                after_users[user_id].append(msg_id)

    return before_users, after_users

def split_tweets_before_after_event(fileName, EVENT, MONTHS):

    event_date = EVENT.split()[1]
    event_month = EVENT.split()[2]
    event_year = EVENT.split()[3]

    before_tweets = defaultdict(int)
    after_tweets = defaultdict(int)

    for line in open(fileName, "r"):
        tweet = json.loads(line.decode('utf-8'))

        if 'lang' in tweet:                
            language = tweet['lang']

            # Only process and analyze tweets written in English
            if language == 'en':
                msg_id = tweet['id']
                timestamp = tweet['created_at'].split()

                tweet_date = timestamp[1]
                tweet_month = timestamp[2]
                tweet_year = timestamp[3]

                if int(tweet_year) > int(event_year):
                    after_tweets[msg_id] += 1
                elif int(tweet_year) == int(event_year):
                    if MONTHS.index(tweet_month) > MONTHS.index(event_month):
                        after_tweets[msg_id] += 1
                    elif MONTHS.index(tweet_month) < MONTHS.index(event_month):
                        before_tweets[msg_id] += 1
                    elif MONTHS.index(tweet_month) == MONTHS.index(event_month):
                        if tweet_date < event_date:
                            before_tweets[msg_id] += 1
                        else:
                            after_tweets[msg_id] += 1

    return before_tweets, after_tweets

def compare_common_users_changes(common_users, before_users, after_users):
    
    csv_output = open("common_users_tweets_changes.txt", "w")

    writer = csv.writer(csv_output)
    writer.writerow( ('User id', 'Number of tweets before', 'Number of tweets after') )

    for user_id in common_users:

        before_number = len(before_users[user_id])      
        after_number = len(after_users[user_id])

        writer.writerow( (user_id, before_number, after_number) )

def main():

    # mark the beginning time of process
    start = timeit.default_timer()

    EVENT = 'Mon, 11 Aug 2014'
    print "RW suicide happened on: " + EVENT

    MONTHS = [u'Jan', u'Feb', u'Mar', u'Apr', u'May', u'Jun', u'Jul', u'Aug', u'Sep', u'Oct', u'Nov', u'Dec']
    DAYS = [u'Mon', u'Tue', u'Wed', u'Thu', u'Fri', u'Sat', u'Sun']
    
    data_dir = '/Users/tl8313/Documents/study_robinwilliams/extracted/'
    fileName = data_dir + 'oneyear_sample.json'

    user_profile = count_users_tweets(fileName)
    tweets_count_dict = cluster_users_by_tweets_count(user_profile)

    before_tweets, after_tweets = split_tweets_before_after_event(fileName, EVENT, MONTHS)
    print "%s tweets posted before this" % str(len(before_tweets))
    print "%s tweets posted after this" % len(after_tweets)

    before_users, after_users = find_users_before_after_event(before_tweets, after_tweets, user_profile)
    print "%d users posted tweets before this" % len(before_users)
    print "%d users posted tweets after this" % len(after_users)

    common_users = set(before_users.keys()).intersection(after_users.keys())
    print "%d users found both before and after this" % len(common_users)

    # compare_common_users_changes(common_users, before_users, after_users)

    ##### mark the ending time of process #####
    end = timeit.default_timer()
    seconds = math.ceil(end - start)
    # Convert Secs Into Human Readable Time String (HH:MM:SS)
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    print "This process took %d:%02d:%02d" % (h, m, s)
    
if __name__ == '__main__':
    main()

