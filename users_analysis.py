import ujson as json
import timeit, math, csv, nltk
from collections import defaultdict, OrderedDict
import matplotlib.pyplot as plt
import plotly.plotly as py
from ark_twokenize import tokenizeRawTweetText
from NER_tagger import parse_raw_message_emoji
from wordclouds_plot import get_normalized_word
from count_keywords import build_stopsets
from wordcloud import WordCloud

def count_users_tweets(json_data):

    user_tweets_dict = defaultdict(list)
    user_profile = defaultdict(set)
    tweet_user_dict = {}

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
                user_tweets_dict[user_id].append(msg_id)
                tweet_user_dict[msg_id] = user_id

                if 'description' in user:
                    user_description = user['description']
                    user_profile[user_id].add(user_description)

    return user_tweets_dict, user_profile, tweet_user_dict

def cluster_users_by_tweets_count(user_tweets_dict):

    tweets_count_dict = defaultdict(list)

    for k, v in user_tweets_dict.items():

        user_id = k
        tweets = len(v)

        tweets_count_dict[tweets].append(user_id)

    # print "number of tweets matched -- how many users in our dataset"
    # for k in OrderedDict(sorted(tweets_count_dict.items(), key=lambda t: t[0])):
    #     print k, len(tweets_count_dict[k])

    # print "user_id sorted -- number of tweets"
    # for k in OrderedDict(sorted(user_tweets_dict.items(), key=lambda t: len(t[1]))):
    #     print k, len(user_tweets_dict[k])

    return tweets_count_dict

def find_users_before_after_event(before_tweets, after_tweets, user_tweets_dict):
    
    before_users = defaultdict(list)
    after_users = defaultdict(list)

    for k, v in user_tweets_dict.items():
        user_id = k
        for msg_id in v:
            if msg_id in before_tweets:
                before_users[user_id].append(msg_id)
            elif msg_id in after_tweets:
                after_users[user_id].append(msg_id)

    return before_users, after_users

def split_tweets_into_unit_time(fileName, EVENT, MONTHS):

    event_date = EVENT.split()[1]
    event_month = EVENT.split()[2]
    event_year = EVENT.split()[3]

    before_tweets = defaultdict(int)
    after_tweets = defaultdict(int)

    tweets_in_each_month = defaultdict(list)
    users_in_each_month = defaultdict(list)

    for line in open(fileName, "r"):
        tweet = json.loads(line.decode('utf-8'))

        if 'lang' in tweet:                
            language = tweet['lang']

            # Only process and analyze tweets written in English
            if language == 'en':
                user = tweet['user']
                user_id = user['id_str']

                msg_id = tweet['id']
                timestamp = tweet['created_at'].split()

                tweet_date = timestamp[1]
                tweet_month = timestamp[2]
                tweet_year = timestamp[3]

                day = timestamp[0].strip(",")
                two_digit_month = '%02d' % int(MONTHS.index(tweet_month)+1)

                tweets_in_each_month[tweet_year + two_digit_month].append(msg_id)
                users_in_each_month[tweet_year + two_digit_month].append(user_id)

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

    return before_tweets, after_tweets, tweets_in_each_month, users_in_each_month

def compare_common_users_changes(common_users, before_users, after_users):
    
    csv_output = open("common_users_tweets_changes.txt", "w")

    writer = csv.writer(csv_output)
    writer.writerow( ('User id', 'Number of tweets before', 'Number of tweets after') )

    for user_id in common_users:

        before_number = len(before_users[user_id])      
        after_number = len(after_users[user_id])

        writer.writerow( (user_id, before_number, after_number) )

def plot_word_cloud_from_tuples(tuples, yearmonth):

    directory = '/Users/tl8313/Documents/study_robinwilliams/figures/monthly_profile/'

    wordcloud = WordCloud(color_func=always_black, background_color='white').fit_words(tuples)

    # Open a plot of the generated image.
    plt.imshow(wordcloud)
    plt.axis("off")
    plt.savefig(directory + yearmonth + '.png', bbox_inches='tight')

def always_black(word=None, font_size=None, position=None, orientation=None, font_path=None, random_state=None):
    """
        Always return black color for font
    """
    return "black"

def description_text_to_tokens(description):

    stopset = build_stopsets()

    if "\n" in description:
        new_message = description.replace("\n", " ")
    else:
        new_message = description

    # customized function to parse messages with emoji and emoticons
    new_message = parse_raw_message_emoji(new_message)

    # ArkTweetNLP tokenizer
    tokens = tokenizeRawTweetText(new_message)
    new_tokens = []
    for word in tokens:
        normalized_word = get_normalized_word(word.strip("\n"))
        if normalized_word != '':
            new_tokens.append(normalized_word)

    new_tokens_stwdsremoved = removeStopwords(new_tokens, stopset)

    return new_tokens_stwdsremoved

# Given a list of words, remove any that are in a list of stop words.
def removeStopwords(wordlist, stopset):
    return [w for w in wordlist if w not in stopset]

def main():

    # mark the beginning time of process
    start = timeit.default_timer()

    EVENT = 'Mon, 11 Aug 2014'
    print "RW suicide happened on: " + EVENT

    MONTHS = [u'Jan', u'Feb', u'Mar', u'Apr', u'May', u'Jun', u'Jul', u'Aug', u'Sep', u'Oct', u'Nov', u'Dec']
    DAYS = [u'Mon', u'Tue', u'Wed', u'Thu', u'Fri', u'Sat', u'Sun']
    
    data_dir = '/Users/tl8313/Documents/study_robinwilliams/extracted/'
    fileName = data_dir + 'oneyear_sample.json'

    user_tweets_dict, user_profile, tweet_user_dict = count_users_tweets(fileName)
    # tweets_count_dict = cluster_users_by_tweets_count(user_tweets_dict)

    before_tweets, after_tweets, tweets_in_each_month, users_in_each_month = split_tweets_into_unit_time(fileName, EVENT, MONTHS)
    print "%s tweets posted before this" % str(len(before_tweets))
    print "%s tweets posted after this" % len(after_tweets)

    print "Users in each month:"
    for k, v in OrderedDict(sorted(users_in_each_month.items(), key=lambda t: t[0])).items():
        print k, len(v)

    monthly_user_descriptions = defaultdict(list)
    print "Tweets in each month:"
    for k, v in OrderedDict(sorted(tweets_in_each_month.items(), key=lambda t: t[0])).items():
        print k, len(v)
        for msg_id in v:
            user_id = tweet_user_dict[msg_id]
            description = ' '.join(user_profile[user_id])
            new_tokens_stwdsremoved = description_text_to_tokens(description)
            monthly_user_descriptions[k].extend(new_tokens_stwdsremoved)

    for yearmonth, v in monthly_user_descriptions.items():
        print(yearmonth)
        f = open('/Users/tl8313/Documents/study_robinwilliams/figures/monthly_profile/'+yearmonth, 'w')
        f.write(str(yearmonth) + "----" + str(len(v)) + "\n")

        # Calculate frequency distribution
        fdist = nltk.FreqDist(v)

        tuples = []
        factor = 1.0 / sum(fdist.itervalues())
        # normalised_fdist = {k : v*factor for k, v in fdist.iteritems()}
        for k, v in fdist.iteritems():
            tuples.append((k, v*factor))
            if len(k) > 0:
                f.write(k.encode('utf-8') + "    " + str(v) + "\n")
        f.close()

        # # Output top words
        # for word, frequency in fdist.most_common(10):
        #     print((word, frequency))

        # plot_word_cloud_from_tuples(tuples, yearmonth)

    before_users, after_users = find_users_before_after_event(before_tweets, after_tweets, user_tweets_dict)
    print "%d users posted tweets before this" % len(before_users)
    print "%d users posted tweets after this" % len(after_users)
    common_users = set(before_users.keys()).intersection(after_users.keys())
    print "%d users found both before and after this" % len(common_users)

    # # compare_common_users_changes(common_users, before_users, after_users)

    ##### mark the ending time of process #####
    end = timeit.default_timer()
    seconds = math.ceil(end - start)
    # Convert Secs Into Human Readable Time String (HH:MM:SS)
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    print "This process took %d:%02d:%02d" % (h, m, s)
    
if __name__ == '__main__':
    main()

