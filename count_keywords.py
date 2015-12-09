import ujson as json
import timeit, math, HTMLParser, re, string, nltk, operator
from ark_twokenize import tokenizeRawTweetText
from collections import defaultdict, OrderedDict
import plotly.plotly as py
from plotly.graph_objs import *
from nltk.corpus import stopwords
from wordcloud import WordCloud
import matplotlib.pyplot as plt

p = re.compile(r'^#*[a-z]+[\'-/]*[a-z]*$', re.UNICODE)
pLink = re.compile(r'https*:\S+\.\w+', re.IGNORECASE)
pMention = re.compile(r'@[A-Za-z0-9_]+\b')
pNewLine = re.compile(r'[\r\n]+')
pRetweet = re.compile(r'\brt\b', re.IGNORECASE)
punctuation = {0x2018:0x27, 0x2019:0x27, 0x201C:0x22, 0x201D:0x22}
h = HTMLParser.HTMLParser()

def count_all_data_keywords(fileName, keywords, stopset):

    print 'Counting keywords in file: ' + fileName

    rules = process_keywords(keywords)

    keywords_dict = defaultdict(list)
    users_dict = defaultdict(list)

    messages_dict = {}
    tweet_keywords_dict = defaultdict(list)

    # crisis_hotline_json = open("crisis_hotline.json", "w")
    # media_guideline_json = open("media_guideline.json", "w")

    for line in open(fileName, "r"):
        tweet = json.loads(line.decode('utf-8'))

        if 'lang' in tweet:                
            language = tweet['lang']

            # Only process and analyze tweets written in English
            if language == 'en':

                message = tweet['text']
                msg_id = tweet['id']

                user = tweet['user']
                user_id = user['id_str']

                # ArkTweetNLP tokenizer
                tokens = tokenizeRawTweetText(message)

                new_tokens = []
                for word in tokens:
                    normalized_word = get_normalized_word(word)
                    new_tokens.append(normalized_word)

                # new_tokens = stemmer_lemmatizer(tokens)

                for index, item in enumerate(rules):
                    intersection_word = set(new_tokens).intersection(item)
                    # Tweets are found to have similar words as keywords list
                    if len(intersection_word) == len(item):
                        keywords_dict[index].append(msg_id)
                        users_dict[index].append(user_id)
                        tweet_keywords_dict[msg_id].append(index)

                        # if index == 4:
                        #     json.dump(tweet, crisis_hotline_json)
                        #     crisis_hotline_json.write("\n")
                        # elif index == 7:
                        #     json.dump(tweet, media_guideline_json)
                        #     media_guideline_json.write("\n")

                stopwords_removed_tokens = []
                for item in new_tokens:
                    if (item not in stopset) and (item is not None):
                        stopwords_removed_tokens.append(item)
                messages_dict[msg_id] = stopwords_removed_tokens

    print "Keyword : Number of tweets which contain the keyword:"
    for k, v in keywords_dict.items():
        print keywords[k], len(v)

    print

    print "Keyword : Number of users who used the keyword:"
    for k, v in users_dict.items():
        print keywords[k], len(v)

    return keywords_dict, messages_dict, users_dict, tweet_keywords_dict

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

def split_tweets_before_after_event(fileName, EVENT, MONTHS):

    event_date = EVENT.split()[1]
    event_month = EVENT.split()[2]
    event_year = EVENT.split()[3]

    before_tweets_dict = defaultdict(int)
    after_tweets_dict = defaultdict(int)

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
        # word = word.translate(punctuation).encode('ascii', 'ignore')  # find ASCII equivalents for unicode quotes
        word = word.translate(punctuation)
    if len(word) < 1:
        return None
    if word[0] == '#':
        word = word.strip('.,*;-:"\'`?!)(#').lower()
    else:
        word = word.strip(string.punctuation).lower()
    if not(p.match(word)):
        return None
    return word

def stemmer_lemmatizer(tokens):

    wnl = nltk.WordNetLemmatizer()

    return [wnl.lemmatize(get_normalized_word(t)) for t in tokens]

def count_tweets_unit_time_period(fileName, MONTHS, DAYS):

    day_dict = defaultdict(int)
    date_dict = defaultdict(int)
    month_dict = defaultdict(int)
    year_dict = defaultdict(int)
    eachday_dict = defaultdict(int)

    for line in open(fileName, "r"):
        tweet = json.loads(line.decode('utf-8'))

        if 'lang' in tweet:                
            language = tweet['lang']

            # Only process and analyze tweets written in English
            if language == 'en':
                
                user = tweet['user']
                user_id_str = user['id_str']
                user_id = user['id']

                timestamp = tweet['created_at'].split()

                day = timestamp[0].strip(",")
                date = timestamp[1]
                month = timestamp[2]
                year = timestamp[3]

                two_digit_month = '%02d' % int(MONTHS.index(month)+1)
                eachday = year + two_digit_month + date

                day_dict[day] += 1
                date_dict[date] += 1
                month_dict[month] += 1
                year_dict[year] += 1
                eachday_dict[eachday] += 1

    print "Numbers of tweets from 1st to 31th:"
    for k, v in sorted(date_dict.items(), key=operator.itemgetter(0)):
        print k, v

    print

    print "Numbers of tweets in 2014 and 2015:"
    for k, v in sorted(year_dict.items(), key=operator.itemgetter(0)):
        print k, v

    print

    print "Numbers of tweets from Monday to Sunday:"
    for day in DAYS:
        print day, day_dict[day]

    print

    print "Numbers of tweets in each month:"
    for month in MONTHS:
        print month, month_dict[month]

    print

    print "Numbers of tweets in each single day:"
    for k, v in sorted(eachday_dict.items(), key=operator.itemgetter(0)):
        print k, v

def count_daily_words_keywords(fileName, keywords, MONTHS):

    rules = process_keywords(keywords)

    daily_keyword_index_dict = dict()
    daily_words_count = dict()

    for line in open(fileName, "r"):
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

                # ArkTweetNLP tokenizer
                tokens = tokenizeRawTweetText(message)
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

        day_keyword_rate_dict[day][index] = (count, total_words, rate)

    return day_keyword_rate_dict

def get_eachday_keyword_rate(day_keyword_rate_dict, keywords):

    sorted_day_keyword_rate_dict = OrderedDict(sorted(day_keyword_rate_dict.items(), key=operator.itemgetter(0)))

    date_list = []
    rate_dict = defaultdict(list)

    for k, v in sorted_day_keyword_rate_dict.items():
        date = str(k[:4]) + "-" + str(k[4:6]) + "-" + str(k[6:]) 
        date_list.append(date)

        # print date

        sorted_v = OrderedDict(sorted(v.items(), key=operator.itemgetter(0)))
        for k0, v0 in sorted_v.items():
            rate_dict[keywords[int(k0)]].append(v0[2])

            # print keywords[int(k0)], v0

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

    plot_url = py.plot(fig, filename = output_name)

def plot_keywords_rates(date_list, rate_dict, keywords, EVENT):

    for index, item in enumerate(keywords):

        keyword = rate_dict[keywords[index]]
        layout_title = "The appearance of " + item + " along the time"
        X_title = "Six months before and after RW suicide date: " + EVENT
        Y_title = "The ratio between number of " + item + " \\and total number of words in one day"
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

def plot_before_after_keyword_wordcloud(keywords_dict, messages_dict, before_tweets_dict, after_tweets_dict, keywords):

    wordcloud_dict = {}

    time_marks = ["before", "after"]
    for index, word in enumerate(keywords):
        for mark in time_marks:
            wordcloud_dict[str(index) + "_" + mark] = []
    
    for k, v in keywords_dict.items():
        for msg_id in v:
            stopwords_removed_tokens = messages_dict[msg_id]

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

    print "keyword -- number of appearances before -- number of appearances after:"
    for index, item in enumerate(keywords):
        print item, len(keywords_before_dict[index]), len(keywords_after_dict[index])

    return keywords_before_dict, keywords_after_dict

def main():
    # mark the beginning time of process
    start = timeit.default_timer()

    EVENT = 'Mon, 11 Aug 2014'
    MONTHS = [u'Jan', u'Feb', u'Mar', u'Apr', u'May', u'Jun', u'Jul', u'Aug', u'Sep', u'Oct', u'Nov', u'Dec']
    DAYS = [u'Mon', u'Tue', u'Wed', u'Thu', u'Fri', u'Sat', u'Sun']

    fileName = 'oneyear_sample.json'

    keywords = ['suicide', 'depression', 'seek help', 'suicide lifeline', 'crisis hotline', 'Parkinson\'s', 'Robin Williams']

    stopset = build_stopsets()

    keywords_dict, messages_dict, users_dict, tweet_keywords_dict = count_all_data_keywords(fileName, keywords, stopset)

    # find_tweets_with_different_keywords(keywords_dict, keywords)

    # before_tweets_dict, after_tweets_dict = split_tweets_before_after_event(fileName, EVENT, MONTHS)

    # keywords_before_dict, keywords_after_dict = compare_keyword_counts_before_after(keywords_dict, before_tweets_dict, after_tweets_dict, keywords)

    # count_tweets_unit_time_period(fileName, MONTHS, DAYS)

    # daily_words_count, daily_keyword_index_dict = count_daily_words_keywords(fileName, keywords, MONTHS)

    # day_keyword_rate_dict = get_daily_keyword_rate(daily_keyword_index_dict, daily_words_count)

    # date_list, rate_dict = get_eachday_keyword_rate(day_keyword_rate_dict, keywords)

    # # plot_keywords_rates(date_list, rate_dict, keywords, EVENT)

    # # plot_before_after_keyword_wordcloud(keywords_dict, messages_dict, before_tweets_dict, after_tweets_dict, keywords)
    
    ##### mark the ending time of process #####
    end = timeit.default_timer()
    seconds = math.ceil(end - start)
    # Convert Secs Into Human Readable Time String (HH:MM:SS)
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    print "This process took %d:%02d:%02d" % (h, m, s)

if __name__ == '__main__':
    main()