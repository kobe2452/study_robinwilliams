import ujson as json
import timeit, math, re, string, sys, HTMLParser, nltk
from collections import defaultdict
from nltk.corpus import wordnet
from ark_twokenize import *
import matplotlib.pyplot as plt
import numpy as np

p = re.compile(r'^#*[a-z]+[\'-/]*[a-z]*$', re.UNICODE)
pLink = re.compile(r'https*:\S+\.\w+', re.IGNORECASE)
pMention = re.compile(r'@[A-Za-z0-9_]+\b')
pNewLine = re.compile(r'[\r\n]+')
pRetweet = re.compile(r'\brt\b', re.IGNORECASE)
punctuation = { 0x2018:0x27, 0x2019:0x27, 0x201C:0x22, 0x201D:0x22 }
h = HTMLParser.HTMLParser()

def my_tokenizer(message):
    ##### rewrite filter_words function, used as tokenizer attribute
    # naive tokenization
    # words = message.split()

    # ArkTweetNLP tokenizer
    words = tokenizeRawTweetText(message)

    tokens = []
    for w in words:
        normalized_word = get_normalized_word(w)

        if normalized_word is not None:
            tokens.append(normalized_word)

    tokens = stemmer_lemmatizer(tokens)

    return tokens

def get_normalized_word(w):
    """
    Returns normalized word or None, if it doesn't have a normalized representation.
    """
    if pLink.match(w):
        return '[http://LINK]'
    if pMention.match(w):
        return '[@SOMEONE]'
    if type(w) is unicode:
        w = w.translate(punctuation).encode('ascii', 'ignore')  # find ASCII equivalents for unicode quotes
    if len(w) < 1:
        return None
    if w[0] == '#':
        w = w.strip('.,*;-:"\'`?!)(').lower()
    else:
        w = w.strip(string.punctuation).lower()
    if not(p.match(w)):
        return None
    return w

def stemmer_lemmatizer(tokens):

    wnl = nltk.WordNetLemmatizer()

    return [wnl.lemmatize(t) for t in tokens]

def matchWords(data_json, data_dir):

    print data_json

    overall_tweets = defaultdict(int)
    overall_long_tweets = defaultdict(int)
    matched_tweets = defaultdict(int)

    # mixf = open(data_dir + 'words_matched_tweets.json', 'w')

    # tweet_length_records = []

    for line in open(data_json, "r"):
        tweet = json.loads(line.decode('utf-8'))

        if 'lang' in tweet:                
            language = tweet['lang']

            # Only process and analyze tweets written in English
            if language == 'en':

                message = tweet['text']
                msg_id = tweet['id']
                user_id = tweet['user']['id_str']

                # define a dictionary
                mixd = {}

                overall_tweets[msg_id] += 1

                text_tokens = my_tokenizer(message)
                
                # tweet_length_records.append(len(text_tokens))

                if len(text_tokens) >= 5:

                    overall_long_tweets[msg_id] += 1

                    # search for patterns 
                    term1a = re.search(r'.+((cutting|depres|sui)|these|bad|sad).+(thoughts|feel).+', message, re.M|re.I)
                    term1b = re.search(r'.+(wan).+die.+', message, re.M|re.I)
                    term1c = re.search(r'.+\b(end).+\b(all|it|life).+', message, re.M|re.I)
                    term1d = re.search(r'.+(can.+|don.+|take).+((go\ on)|live|(any\ more)|cop|alive).+', message, re.M|re.I)

                    if term1d:
                        print message
                        print
        #                     mixd['message'] = message
        #                     mixd['msg_id'] = msg_id
        #                     mixd['userid'] = userid
        #                     # json.dump(mixd, mixf)
        #                     # mixf.write("\n")
        #                     matched_tweets[msg_id] += 1

    # print np.mean(tweet_length_records)
    # plt.hist(tweet_length_records)
    # plt.title("Tweets Lengths Histogram")
    # plt.xlabel("Token counts")
    # plt.ylabel("Frequency")
    # plt.savefig('tweet_length_histogram.png', bbox_inches='tight')

    return overall_tweets, overall_long_tweets, matched_tweets

def main():
    # mark the beginning time of process
    start = timeit.default_timer()

    data_dir = '/Users/tl8313/Documents/study_robinwilliams/extracted/'
    data_json = data_dir + 'oneyear_sample.json'

    overall_tweets, overall_long_tweets, matched_tweets = matchWords(data_json, data_dir)

    print "there are a total of %d tweets" % len(overall_tweets)
    print "%d tweets have more than 5 tokens" % len(overall_long_tweets)
    print "%d tweets matched by the text filters" % len(matched_tweets)

    # matched_msgid_text = open(data_dir + 'words_matched_tweets.txt', 'w')
    # for k, v in matched_tweets.items():
    #     matched_msgid_text.write(k)
    #     matched_msgid_text.write("\n")

    ##### mark the ending time of process #####
    end = timeit.default_timer()
    seconds = math.ceil(end - start)
    # Convert Secs Into Human Readable Time String (HH:MM:SS)
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    print "This process took %d:%02d:%02d" % (h, m, s)

if __name__ == '__main__':
    main()