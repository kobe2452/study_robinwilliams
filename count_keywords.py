import ujson as json
import timeit, math, HTMLParser, re, string, nltk, operator, csv
from ark_twokenize import tokenizeRawTweetText
from collections import defaultdict, OrderedDict
import plotly.plotly as py
from plotly.graph_objs import *
from nltk.corpus import stopwords
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from NER_tagger import parse_raw_message_emoji

p = re.compile(r'^#*[a-z]+[\'-/]*[a-z]*$', re.UNICODE)
pLink = re.compile(r'https*:\S+\.\w+', re.IGNORECASE)
pMention = re.compile(r'@[A-Za-z0-9_]+\b')
pNewLine = re.compile(r'[\r\n]+')
pRetweet = re.compile(r'\brt\b', re.IGNORECASE)
punctuation = {0x2018:0x27, 0x2019:0x27, 0x201C:0x22, 0x201D:0x22}
h = HTMLParser.HTMLParser()

def count_all_data_keywords(oneyeardata_json, keywords, stopset, before_tweets_dict, after_tweets_dict):

    print 'Counting keywords in file: ' + oneyeardata_json

    rules = process_keywords(keywords)

    keywords_dict = defaultdict(list)
    users_dict = defaultdict(list)

    messages_normalized_word_dict = {}
    messages_stopwords_removed_dict = {}
    tweet_keywords_dict = defaultdict(list)

    # suicide_json = open("suicide_tweets.json", "w")
    # depression_json = open("depression_tweets.json", "w")
    # seekhelp_json = open("seek_help_tweets.json", "w")
    # suicidelifeline_json = open("suicide_lifeline_tweets.json", "w")
    # crisishotline_json = open("crisis_hotline_tweets.json", "w")
    # parkinsons_json = open("parkinsons_tweets.json", "w")
    # robinwilliams_json = open("robin_williams_tweets.json", "w")

    # suicide_json_0 = open("suicide_tweets_0.json", "w")
    # depression_json_0 = open("depression_tweets_0.json", "w")
    # seekhelp_json_0 = open("seek_help_tweets_0.json", "w")
    # suicidelifeline_json_0 = open("suicide_lifeline_tweets_0.json", "w")
    # crisishotline_json_0 = open("crisis_hotline_tweets_0.json", "w")
    # parkinsons_json_0 = open("parkinsons_tweets_0.json", "w")
    # robinwilliams_json_0 = open("robin_williams_tweets_0.json", "w")

    # suicide_json_1 = open("suicide_tweets_1.json", "w")
    # depression_json_1 = open("depression_tweets_1.json", "w")
    # seekhelp_json_1 = open("seek_help_tweets_1.json", "w")
    # suicidelifeline_json_1 = open("suicide_lifeline_tweets_1.json", "w")
    # crisishotline_json_1 = open("crisis_hotline_tweets_1.json", "w")
    # parkinsons_json_1 = open("parkinsons_tweets_1.json", "w")
    # robinwilliams_json_1 = open("robin_williams_tweets_1.json", "w")

    for line in open(oneyeardata_json, "r"):
        tweet = json.loads(line.decode('utf-8'))

        if 'lang' in tweet:                
            language = tweet['lang']

            # Only process and analyze tweets written in English
            if language == 'en':

                message = tweet['text']
                msg_id = tweet['id']

                user = tweet['user']
                user_id = user['id_str']

                if "\n" in message:
                    new_message = message.replace("\n", " ")
                else:
                    new_message = message

                # customized function to parse messages with emoji and emoticons
                new_message = parse_raw_message_emoji(new_message)

                # ArkTweetNLP tokenizer
                tokens = tokenizeRawTweetText(new_message)

                new_tokens = []
                for word in tokens:
                    normalized_word = get_normalized_word(word.strip("\n"))
                    new_tokens.append(normalized_word)
                messages_normalized_word_dict[msg_id] = new_tokens

                # new_tokens = stemmer_lemmatizer(tokens)

                for index, item in enumerate(rules):
                    intersection_word = set(new_tokens).intersection(item)
                    # Tweets are found to have similar words as keywords list
                    if len(intersection_word) == len(item):
                        keywords_dict[index].append(msg_id)
                        users_dict[index].append(user_id)
                        tweet_keywords_dict[msg_id].append(index)

    # keywords = ['suicide', 'depression', 'seek help', 'suicide lifeline', 'crisis hotline', 'Parkinson\'s', 'Robin Williams']
                        if msg_id in before_tweets_dict:
                            if index == 0:
                                json.dump(tweet, suicide_json_0)
                                suicide_json_0.write("\n")

                            if index == 1:
                                json.dump(tweet, depression_json_0)
                                depression_json_0.write("\n")

                            if index == 2:
                                json.dump(tweet, seekhelp_json_0)
                                seekhelp_json_0.write("\n")

                            if index == 3:
                                json.dump(tweet, suicidelifeline_json_0)
                                suicidelifeline_json_0.write("\n")

                            if index == 4:
                                json.dump(tweet, crisishotline_json_0)
                                crisishotline_json_0.write("\n")

                            if index == 5:
                                json.dump(tweet, parkinsons_json_0)
                                parkinsons_json_0.write("\n")

                            if index == 6:
                                json.dump(tweet, robinwilliams_json_0)
                                robinwilliams_json_0.write("\n")

                        if msg_id in after_tweets_dict:
                            if index == 0:
                                json.dump(tweet, suicide_json_1)
                                suicide_json_1.write("\n")

                            if index == 1:
                                json.dump(tweet, depression_json_1)
                                depression_json_1.write("\n")

                            if index == 2:
                                json.dump(tweet, seekhelp_json_1)
                                seekhelp_json_1.write("\n")

                            if index == 3:
                                json.dump(tweet, suicidelifeline_json_1)
                                suicidelifeline_json_1.write("\n")

                            if index == 4:
                                json.dump(tweet, crisishotline_json_1)
                                crisishotline_json_1.write("\n")

                            if index == 5:
                                json.dump(tweet, parkinsons_json_1)
                                parkinsons_json_1.write("\n")

                            if index == 6:
                                json.dump(tweet, robinwilliams_json_1)
                                robinwilliams_json_1.write("\n")

                stopwords_removed_tokens = []
                for item in new_tokens:
                    if (item not in stopset) and (item is not None):
                        stopwords_removed_tokens.append(item)
                messages_stopwords_removed_dict[msg_id] = stopwords_removed_tokens

    print "keyword :  Number of tweets : Number of users"
    for k, v in keywords_dict.items():
        print "%s : %d : %d" % (keywords[k], len(set(v)), len(set(users_dict[k])))

    return keywords_dict, messages_normalized_word_dict, messages_stopwords_removed_dict, users_dict, tweet_keywords_dict

def find_tweets_with_different_keywords(keywords_dict, keywords):

#    keywords = ['suicide', 'depression', 'seek help', 'suicide lifeline', 'crisis hotline', 'Parkinson\'s', 'Robin Williams']

    # suicide_ids = keywords_dict[0]
    # depression_ids = keywords_dict[1]
    # seekhelp_ids = keywords_dict[2]
    # suicidelifeline_ids = keywords_dict[3]
    # crisishotline_ids = keywords_dict[4]
    # parkinsons_ids = keywords_dict[5]
    # robinwilliams_ids = keywords_dict[6]

    print keywords[0] + " + " + keywords[1]
    print len(set.intersection(set(keywords_dict[0]), set(keywords_dict[1])))
    
    print keywords[0] + " + " + keywords[2]
    print len(set.intersection(set(keywords_dict[0]), set(keywords_dict[2])))
    
    print keywords[0] + " + " + keywords[3]
    print len(set.intersection(set(keywords_dict[0]), set(keywords_dict[3])))

    print keywords[0] + " + " + keywords[4]
    print len(set.intersection(set(keywords_dict[0]), set(keywords_dict[4])))

    print keywords[0] + " + " + keywords[5]
    print len(set.intersection(set(keywords_dict[0]), set(keywords_dict[5])))

    print keywords[0] + " + " + keywords[6]
    print len(set.intersection(set(keywords_dict[0]), set(keywords_dict[6])))

    print keywords[1] + " + " + keywords[2]
    print len(set.intersection(set(keywords_dict[1]), set(keywords_dict[2])))

    print keywords[1] + " + " + keywords[3]
    print len(set.intersection(set(keywords_dict[1]), set(keywords_dict[3])))

    print keywords[1] + " + " + keywords[4]
    print len(set.intersection(set(keywords_dict[1]), set(keywords_dict[4])))

    print keywords[1] + " + " + keywords[5]
    print len(set.intersection(set(keywords_dict[1]), set(keywords_dict[5])))

    print keywords[1] + " + " + keywords[6]
    print len(set.intersection(set(keywords_dict[1]), set(keywords_dict[6])))

    print keywords[2] + " + " + keywords[3]
    print len(set.intersection(set(keywords_dict[2]), set(keywords_dict[3])))

    print keywords[2] + " + " + keywords[4]
    print len(set.intersection(set(keywords_dict[2]), set(keywords_dict[4])))

    print keywords[2] + " + " + keywords[5]
    print len(set.intersection(set(keywords_dict[2]), set(keywords_dict[5])))

    print keywords[2] + " + " + keywords[6]
    print len(set.intersection(set(keywords_dict[2]), set(keywords_dict[6])))

    print keywords[3] + " + " + keywords[4]
    print len(set.intersection(set(keywords_dict[3]), set(keywords_dict[4])))

    print keywords[3] + " + " + keywords[5]
    print len(set.intersection(set(keywords_dict[3]), set(keywords_dict[5])))

    print keywords[3] + " + " + keywords[6]
    print len(set.intersection(set(keywords_dict[3]), set(keywords_dict[6])))

    print keywords[4] + " + " + keywords[5]
    print len(set.intersection(set(keywords_dict[4]), set(keywords_dict[5])))

    print keywords[4] + " + " + keywords[6]
    print len(set.intersection(set(keywords_dict[4]), set(keywords_dict[6])))

    print keywords[5] + " + " + keywords[6]
    print len(set.intersection(set(keywords_dict[5]), set(keywords_dict[6])))

def split_tweets_before_after_event(oneyeardata_json, EVENT, MONTHS):

    event_date = EVENT.split()[1]
    event_month = EVENT.split()[2]
    event_year = EVENT.split()[3]

    before_tweets_dict = defaultdict(int)
    after_tweets_dict = defaultdict(int)

    for line in open(oneyeardata_json, "r"):
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
                    after_tweets_dict[msg_id] += 1
                elif int(tweet_year) == int(event_year):
                    if MONTHS.index(tweet_month) > MONTHS.index(event_month):
                        after_tweets_dict[msg_id] += 1
                    elif MONTHS.index(tweet_month) < MONTHS.index(event_month):
                        before_tweets_dict[msg_id] += 1
                    elif MONTHS.index(tweet_month) == MONTHS.index(event_month):
                        if tweet_date < event_date:
                            before_tweets_dict[msg_id] += 1
                        else:
                            after_tweets_dict[msg_id] += 1

    print "RW suicide happened on: " + EVENT
    print "%s tweets posted before this" % str(len(before_tweets_dict))
    print "%s tweets posted after this" % len(after_tweets_dict)

    return before_tweets_dict, after_tweets_dict

def process_keywords(keywords):
    """
    Break up keywords into a list of words as rules
    """

    rules = []

    for item in keywords:
        rules.append(item.lower().split())

    return rules

def get_normalized_word(word):
    """
    Returns normalized word or None, if it doesn't have a normalized representation.
    """
    if pLink.match(word):
        return '[http://LINK]'
    if pMention.match(word):
        return '[@SOMEONE]'
    if type(word) is unicode:
        word = word.translate(punctuation)
    if len(word) < 1:
        return None
    if word[0] == '#':
        word = word.strip('.,*;-:"\'`?!)(#').lower()
    else:
        word = word.lower()

    return word

def stemmer_lemmatizer(tokens):

    wnl = nltk.WordNetLemmatizer()

    return [wnl.lemmatize(get_normalized_word(t)) for t in tokens]

def count_tweets_unit_time_period(oneyeardata_json, MONTHS, DAYS):

    day_dict = defaultdict(list)
    date_dict = defaultdict(list)
    month_dict = defaultdict(list)
    year_dict = defaultdict(list)
    eachday_dict = defaultdict(list)

    for line in open(oneyeardata_json, "r"):
        tweet = json.loads(line.decode('utf-8'))

        if 'lang' in tweet:                
            language = tweet['lang']

            # Only process and analyze tweets written in English
            if language == 'en':
                
                msg_id = tweet['id']

                # user = tweet['user']
                # user_id = user['id_str']

                timestamp = tweet['created_at'].split()

                day = timestamp[0].strip(",")
                date = timestamp[1]
                month = timestamp[2]
                year = timestamp[3]

                two_digit_month = '%02d' % int(MONTHS.index(month)+1)
                eachday = year + two_digit_month + date

                day_dict[day].append(msg_id)
                date_dict[date].append(msg_id)
                month_dict[year + two_digit_month].append(msg_id)
                year_dict[year].append(msg_id)
                eachday_dict[eachday].append(msg_id)

    date_k_list = []
    date_v_list = []
    print "Numbers of tweets from 1st to 31th:"
    for k, v in sorted(date_dict.items(), key=operator.itemgetter(0)):
        # print k, len(v)
        date_k_list.append(k)
        date_v_list.append(len(v))

    print

    year_k_list = []
    year_v_list = []
    print "Numbers of tweets in 2014 and 2015:"
    for k, v in sorted(year_dict.items(), key=operator.itemgetter(0)):
        # print k, len(v)
        year_k_list.append(k)
        year_v_list.append(len(v))

    print

    weekday_k_list = []
    weekday_v_list = []
    print "Numbers of tweets from Monday to Sunday:"
    for day in DAYS:
        # print day, len(day_dict[day])
        weekday_k_list.append(day)
        weekday_v_list.append(len(day_dict[day]))        

    print

    month_k_list = []
    month_v_list = []
    print "Numbers of tweets in each month:"
    for k, v in sorted(month_dict.items(), key=lambda t: t[0]):
        # print k, len(v)
        month_k_list.append(k)
        month_v_list.append(len(v))

    print

    day_k_list = []
    day_v_list = []
    print "Numbers of tweets in each single day:"
    for k, v in sorted(eachday_dict.items(), key=operator.itemgetter(0)):
        # print k, len(v)
        day_k_list.append(k)
        day_v_list.append(len(v))

    return date_k_list, date_v_list, year_k_list, year_v_list, weekday_k_list, weekday_v_list, month_k_list, month_v_list, day_k_list, day_v_list

def count_daily_words_keywords(oneyeardata_json, keywords, MONTHS):

    rules = process_keywords(keywords)

    daily_keyword_index_dict = dict()
    daily_words_count = dict()

    for line in open(oneyeardata_json, "r"):
        tweet = json.loads(line.decode('utf-8'))

        if 'lang' in tweet:                
            language = tweet['lang']

            # Only process and analyze tweets written in English
            if language == 'en':
                # time information
                timestamp = tweet['created_at']

                year, month, two_digit_month, day, date, hour, minute, second, timezone = parse_timestamp(timestamp, MONTHS)

                eachday = year + two_digit_month + date

                # tweet information
                message = tweet['text']

                if "\n" in message:
                    new_message = message.replace("\n", " ")
                else:
                    new_message = message

                # customized function to parse messages with emoji and emoticons
                new_message = parse_raw_message_emoji(new_message)

                # ArkTweetNLP tokenizer
                tokens = tokenizeRawTweetText(new_message)

                new_tokens = []
                for word in tokens:
                    normalized_word = get_normalized_word(word)
                    new_tokens.append(normalized_word)

                try:
                    daily_words_count[eachday] += len(new_tokens)
                except KeyError:
                    daily_words_count[eachday] = len(new_tokens)

                for index, item in enumerate(rules):
                    intersection_word = set(new_tokens).intersection(item)

                    # concatenate time information and keyword index
                    # used as keys in overall dictionary
                    key = eachday + str(index)
                    daily_keyword_index_dict.setdefault(key, 0)

                    # intersection word is exactly the same as the item
                    if len(intersection_word) == len(item):
                        try:
                            daily_keyword_index_dict[key] += 1
                        except KeyError:
                            daily_keyword_index_dict[key] = 1

    return daily_words_count, daily_keyword_index_dict

def get_daily_keyword_rate(daily_keyword_index_dict, daily_words_count):

    sorted_eachday_index_dict = OrderedDict(sorted(daily_keyword_index_dict.items(), key=operator.itemgetter(0)))

    # initialize a dictionary to summarize tweets numbers from Mon to Sun
    day_keyword_rate_dict = defaultdict(dict)

    for k, v in sorted_eachday_index_dict.items():
        day = k[:-1]
        index = k[-1:]
        count = v

        total_words = daily_words_count[day]

        rate = count / float(total_words) * 100
        print day, index, count, total_words, rate

        day_keyword_rate_dict[day][index] = (count, total_words, rate)

    return day_keyword_rate_dict

def get_eachday_keyword_rate(day_keyword_rate_dict, keywords):

    sorted_day_keyword_rate_dict = OrderedDict(sorted(day_keyword_rate_dict.items(), key=operator.itemgetter(0)))

    date_list = []
    rate_dict = defaultdict(list)

    for k, v in sorted_day_keyword_rate_dict.items():
        date = str(k[:4]) + "-" + str(k[4:6]) + "-" + str(k[6:]) 
        date_list.append(date)

        sorted_v = OrderedDict(sorted(v.items(), key=operator.itemgetter(0)))
        for k0, v0 in sorted_v.items():

            keyword = keywords[int(k0)]
            rate = v0[2]
            rate_dict[keyword].append(rate)

    return date_list, rate_dict

def plot_separate_keyword_rate(date_list, keyword_rate_list, layout_title, X_title, Y_title, output_name):

    data = Data([
        Scatter(
            x = date_list,
            y = keyword_rate_list
        )
    ])

    layout = Layout(
        title = layout_title,
        width = 2000,
        xaxis = XAxis(
            title = X_title
        ),
        yaxis = YAxis(
            title = Y_title
        )
    )

    fig = Figure(
        data = data,
        layout = layout
    )

    plot_url = py.plot(fig, oneyeardata_json = output_name)

def plot_keywords_rates(date_list, rate_dict, keywords, EVENT):

    for index, item in enumerate(keywords):

        keyword = rate_dict[keywords[index]]
        layout_title = "appearances of " + item + " : total number of words in each day along the timeline"
        X_title = "Six months before and after RW's suicide date " + EVENT
        Y_title = "ratio (percentage)"
        output_name = item + ' daily rate'

        plot_separate_keyword_rate(date_list, keyword, layout_title, X_title, Y_title, output_name)        

def parse_timestamp(timestamp, MONTHS):

    day = timestamp.split()[0].strip(",")
    date = timestamp.split()[1]
    month = timestamp.split()[2]
    year = timestamp.split()[3]
    hour = timestamp.split()[4].split(":")[0]
    minute = timestamp.split()[4].split(":")[1]
    second = timestamp.split()[4].split(":")[2]
    two_digit_month = '%02d' % int(MONTHS.index(month)+1)
    timezone = timestamp.split()[5]

    return year, month, two_digit_month, day, date, hour, minute, second, timezone

def plot_before_after_keyword_wordcloud(keywords_dict, messages_stopwords_removed_dict, before_tweets_dict, after_tweets_dict, keywords):

    wordcloud_dict = {}

    time_marks = ["before", "after"]
    for index, word in enumerate(keywords):
        for mark in time_marks:
            wordcloud_dict[str(index) + "_" + mark] = []
    
    for k, v in keywords_dict.items():
        for msg_id in v:
            stopwords_removed_tokens = messages_stopwords_removed_dict[msg_id]

            if msg_id in before_tweets_dict:
                wordcloud_dict[str(k) + "_before"] += stopwords_removed_tokens
            elif msg_id in after_tweets_dict:
                wordcloud_dict[str(k) + "_after"] += stopwords_removed_tokens

    for k, v in wordcloud_dict.items():
        text = ' '.join(v)
        title = (keywords[int(k.split("_")[0])]).replace(" ", "") + "_" + k.split("_")[1]
        plot_word_cloud(text, title)

def build_stopsets():

    stop1 = stopwords.words('english')

    stop2 = []

    for line in open('stopwords.txt', "r"):
        stop2.append(line.strip())

    stopset = set(stop1) | set(stop2)

    return stopset

def always_black(word=None, font_size=None, position=None,
                 orientation=None, font_path=None, random_state=None):
    """
        Always return black color for font
    """
    return "black"

def plot_word_cloud(text, title):

    wordcloud = WordCloud(color_func=always_black, background_color='white').generate(text)
    # Open a plot of the generated image.
    plt.imshow(wordcloud)
    plt.axis("off")
    plt.title('word cloud for ' + title + ' tweets')
    plt.savefig(title + '.png')

def compare_keyword_counts_before_after(keywords_dict, before_tweets_dict, after_tweets_dict, keywords):

    keywords_before_dict = defaultdict(list)
    keywords_after_dict = defaultdict(list)
    
    for k, v in keywords_dict.items():
        keyword_index = k
        matched_tweets = v

        for msg_id in matched_tweets:
            if msg_id in before_tweets_dict:
                keywords_before_dict[keyword_index].append(msg_id)
            elif msg_id in after_tweets_dict:
                keywords_after_dict[keyword_index].append(msg_id)

    print "keyword : number of appearances BEFORE : number of appearances AFTER"
    for index, item in enumerate(keywords):
        print "%s : %d : %d" % ( item, len(keywords_before_dict[index]), len(keywords_after_dict[index]) )

    return keywords_before_dict, keywords_after_dict

def export_lists_to_csv(list_all, filename):

    with open(filename, 'wb') as f:
        writer = csv.writer(f)

        # Create headers in a row, from 1 to the end of onelist
        headers = []
        headers.append('time')
        headers.append('suicide')
        headers.append('depression')
        headers.append('seek help')
        headers.append('suicide lifeline')
        headers.append('crisis hotline')
        headers.append('Parkinson\'s')
        headers.append('Robin Williams')
        writer.writerow(headers)

        # # export data from onelist to a list
        # attributes = ['msg_id', 'message']

        for onelist in list_all:
            writer.writerow(onelist)

def main():
    # mark the beginning time of process
    start = timeit.default_timer()

    EVENT = 'Mon, 11 Aug 2014'
    MONTHS = [u'Jan', u'Feb', u'Mar', u'Apr', u'May', u'Jun', u'Jul', u'Aug', u'Sep', u'Oct', u'Nov', u'Dec']
    DAYS = [u'Mon', u'Tue', u'Wed', u'Thu', u'Fri', u'Sat', u'Sun']

    data_dir = "/Users/tl8313/Documents/study_robinwilliams/extracted/"
    oneyeardata_json = data_dir + 'oneyear_sample.json'
    suicide_json = data_dir + "suicide.json"
    depression_json = data_dir + "depression.json"
    seekhelp_json = data_dir + "seek_help.json"
    suicidelifeline_json = data_dir + "suicide_lifeline.json"
    crisishotline_json = data_dir + "crisis_hotline.json"
    parkinsons_json = data_dir + "parkinsons.json"
    robinwilliams_json = data_dir + "robin_williams.json"

    keywords = ['suicide', 'depression', 'seek help', 'suicide lifeline', 'crisis hotline', 'Parkinson\'s', 'Robin Williams']

    stopset = build_stopsets()

    # find_tweets_with_different_keywords(keywords_dict, keywords)

    before_tweets_dict, after_tweets_dict = split_tweets_before_after_event(oneyeardata_json, EVENT, MONTHS)

    keywords_dict, messages_normalized_word_dict, messages_stopwords_removed_dict, users_dict, tweet_keywords_dict = count_all_data_keywords(oneyeardata_json, keywords, stopset, before_tweets_dict, after_tweets_dict)

    # keywords_before_dict, keywords_after_dict = compare_keyword_counts_before_after(keywords_dict, before_tweets_dict, after_tweets_dict, keywords)

    # count_tweets_unit_time_period(oneyeardata_json, MONTHS, DAYS)

    json_files = [suicide_json, depression_json, seekhelp_json, suicidelifeline_json, crisishotline_json, parkinsons_json, robinwilliams_json]

    date_k_1, date_v_1, year_k_1, year_v_1, weekday_k_1, weekday_v_1, month_k_1, month_v_1, day_k_1, day_v_1 = count_tweets_unit_time_period(suicide_json, MONTHS, DAYS)
    date_k_2, date_v_2, year_k_2, year_v_2, weekday_k_2, weekday_v_2, month_k_2, month_v_2, day_k_2, day_v_2 = count_tweets_unit_time_period(depression_json, MONTHS, DAYS)
    date_k_3, date_v_3, year_k_3, year_v_3, weekday_k_3, weekday_v_3, month_k_3, month_v_3, day_k_3, day_v_3 = count_tweets_unit_time_period(seekhelp_json, MONTHS, DAYS)
    date_k_4, date_v_4, year_k_4, year_v_4, weekday_k_4, weekday_v_4, month_k_4, month_v_4, day_k_4, day_v_4 = count_tweets_unit_time_period(suicidelifeline_json, MONTHS, DAYS)
    date_k_5, date_v_5, year_k_5, year_v_5, weekday_k_5, weekday_v_5, month_k_5, month_v_5, day_k_5, day_v_5 = count_tweets_unit_time_period(crisishotline_json, MONTHS, DAYS)
    date_k_6, date_v_6, year_k_6, year_v_6, weekday_k_6, weekday_v_6, month_k_6, month_v_6, day_k_6, day_v_6 = count_tweets_unit_time_period(parkinsons_json, MONTHS, DAYS)
    date_k_7, date_v_7, year_k_7, year_v_7, weekday_k_7, weekday_v_7, month_k_7, month_v_7, day_k_7, day_v_7 = count_tweets_unit_time_period(robinwilliams_json, MONTHS, DAYS)

    DATE = zip(date_k_1, date_v_1, date_v_2, date_v_3, date_v_4, date_v_5, date_v_6, date_v_7)
    export_lists_to_csv(DATE, "date.csv")

    YEAR = zip(year_k_1, year_v_1, year_v_2, year_v_3, year_v_4, year_v_5, year_v_6, year_v_7)
    export_lists_to_csv(YEAR, "year.csv")

    WEEKDAY = zip(weekday_k_1, weekday_v_1, weekday_v_2, weekday_v_3, weekday_v_4, weekday_v_5, weekday_v_6, weekday_v_7)
    export_lists_to_csv(WEEKDAY, "weekday.csv")

    MONTH = zip(month_k_1, month_v_1, month_v_2, month_v_3, month_v_4, month_v_5, month_v_6, month_v_7)
    export_lists_to_csv(MONTH, "month.csv")

    DAY = zip(day_k_1, day_v_1, day_v_2, day_v_3, day_v_4, day_v_5, day_v_6, day_v_7)
    export_lists_to_csv(DAY, "day.csv")

    daily_words_count, daily_keyword_index_dict = count_daily_words_keywords(oneyeardata_json, keywords, MONTHS)

    day_keyword_rate_dict = get_daily_keyword_rate(daily_keyword_index_dict, daily_words_count)

    date_list, rate_dict = get_eachday_keyword_rate(day_keyword_rate_dict, keywords)

    plot_keywords_rates(date_list, rate_dict, keywords, EVENT)

    plot_before_after_keyword_wordcloud(keywords_dict, messages_stopwords_removed_dict, before_tweets_dict, after_tweets_dict, keywords)
    
    ##### mark the ending time of process #####
    end = timeit.default_timer()
    seconds = math.ceil(end - start)
    # Convert Secs Into Human Readable Time String (HH:MM:SS)
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    print "This process took %d:%02d:%02d" % (h, m, s)

if __name__ == '__main__':
    main()