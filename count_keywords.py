import ujson as json
import timeit, math, HTMLParser, re, string, nltk, operator
from ark_twokenize import tokenizeRawTweetText
from collections import defaultdict, OrderedDict

p = re.compile(r'^#*[a-z]+[\'-/]*[a-z]*$', re.UNICODE)
pLink = re.compile(r'https*:\S+\.\w+', re.IGNORECASE)
pMention = re.compile(r'@[A-Za-z0-9_]+\b')
pNewLine = re.compile(r'[\r\n]+')
pRetweet = re.compile(r'\brt\b', re.IGNORECASE)
punctuation = {0x2018:0x27, 0x2019:0x27, 0x201C:0x22, 0x201D:0x22}
h = HTMLParser.HTMLParser()

def count_all_data_keywords(fileName, keywords):

    print 'Counting keywords in file: ' + fileName

    rules = process_keywords(keywords)

    wnl = nltk.WordNetLemmatizer()

    keywords_dict = defaultdict(int)

    for line in open(fileName, "r"):
        tweet = json.loads(line.decode('utf-8'))

        if 'lang' in tweet:                
            language = tweet['lang']

            # Only process and analyze tweets written in English
            if language == 'en':
                message = tweet['text']

                # ArkTweetNLP tokenizer
                tokens = tokenizeRawTweetText(message)

                new_tokens = []
                for word in tokens:
                    normalized_word = get_normalized_word(word)
                    new_tokens.append(normalized_word)

                # new_tokens = stemmer_lemmatizer(tokens)

                for index, item in enumerate(rules):
                    intersection_word = set(new_tokens).intersection(item)
                    if len(intersection_word) == len(item):
                        keywords_dict[index] += 1

    for k, v in keywords_dict.items():
        print keywords[k], v

    return keywords_dict

def split_tweets_before_after_event(fileName, EVENT, MONTHS):

    event_date = EVENT.split()[1]
    event_month = EVENT.split()[2]
    event_year = EVENT.split()[3]

    before_dict = defaultdict(int)
    after_dict = defaultdict(int)

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
                    after_dict[msg_id] += 1
                elif int(tweet_year) == int(event_year):
                    if MONTHS.index(tweet_month) > MONTHS.index(event_month):
                        after_dict[msg_id] += 1
                    elif MONTHS.index(tweet_month) < MONTHS.index(event_month):
                        before_dict[msg_id] += 1
                    elif MONTHS.index(tweet_month) == MONTHS.index(event_month):
                        if tweet_date < event_date:
                            before_dict[msg_id] += 1
                        else:
                            after_dict[msg_id] += 1

    print "RW suicide happened on: " + EVENT
    print "%s tweets posted before this" % str(len(before_dict))
    print "%s tweets posted after this" % len(after_dict)

    return before_dict, after_dict

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

    daily_index_dict = dict()
    daily_words_count = dict()

    for line in open(fileName, "r"):
        tweet = json.loads(line.decode('utf-8'))

        if 'lang' in tweet:                
            language = tweet['lang']

            # Only process and analyze tweets written in English
            if language == 'en':
                # time information
                timestamp = tweet['created_at'].split()
                day = timestamp[0].strip(",")
                date = timestamp[1]
                month = timestamp[2]
                year = timestamp[3]

                two_digit_month = '%02d' % int(MONTHS.index(month)+1)
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
                    # intersection word is exactly the same as the item
                    if len(intersection_word) == len(item):

                        # concatenate time information and keyword index
                        # used as keys in overall dictionary
                        key = eachday + str(index)

                        try:
                            daily_index_dict[key] += 1
                        except KeyError:
                            daily_index_dict[key] = 1

    return daily_index_dict, daily_words_count

def main():
    # mark the beginning time of process
    start = timeit.default_timer()

    EVENT = 'Mon, 11 Aug 2014'
    MONTHS = [u'Jan', u'Feb', u'Mar', u'Apr', u'May', u'Jun', u'Jul', u'Aug', u'Sep', u'Oct', u'Nov', u'Dec']
    DAYS = [u'Mon', u'Tue', u'Wed', u'Thu', u'Fri', u'Sat', u'Sun']

    fileName = 'oneyear_sample.json'

    keywords = ['suicide', 'depression', 'media guideline', 'seek help', 'suicide lifeline', 'crisis hotline', 'Parkinson\'s', 'Robin Williams']

    # keywords_dict = count_all_data_keywords(fileName, keywords)

    # before_dict, after_dict = split_tweets_before_after_event(fileName, EVENT, MONTHS)

    count_tweets_unit_time_period(fileName, MONTHS, DAYS)

    daily_index_dict, daily_words_count = count_daily_words_keywords(fileName, keywords, MONTHS)

    ##### mark the ending time of process #####
    end = timeit.default_timer()
    seconds = math.ceil(end - start)
    # Convert Secs Into Human Readable Time String (HH:MM:SS)
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    print "This process took %d:%02d:%02d" % (h, m, s)

if __name__ == '__main__':
    main()