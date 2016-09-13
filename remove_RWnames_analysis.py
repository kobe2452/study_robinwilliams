import timeit, math, nltk
from count_keywords import build_stopsets, process_keywords
from collections import defaultdict
import ujson as json
from ark_twokenize import tokenizeRawTweetText
from NER_tagger import parse_raw_message_emoji
from wordclouds_plot import get_normalized_word

# Given a list of words, remove any that are in a list of stop words.
def removeStopwords(wordlist, stopset):
    return [w for w in wordlist if w not in stopset]

def separate_tweets_contain_RWname(json_file, keywords, stopset, MONTHS):

    print 'Counting keywords in file: ' + json_file

    rules = process_keywords(keywords)

    total_tweets = {}
    tweets_contain_RWname = defaultdict(int)

    for line in open(json_file, "r"):
        tweet = json.loads(line.decode('utf-8'))

        if 'lang' in tweet:                
            language = tweet['lang']

            # Only process and analyze tweets written in English
            if language == 'en':

                message = tweet['text']
                msg_id = tweet['id']

                timestamp = tweet['created_at'].split()
                day = timestamp[0].strip(",")
                date = timestamp[1]
                month = timestamp[2]
                year = timestamp[3]
                two_digit_month = '%02d' % int(MONTHS.index(month)+1)

                total_tweets[msg_id] = (message, year+two_digit_month)

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
                    normalized_word = get_normalized_word(word.strip(" \n"))
                    if normalized_word != '':
                        new_tokens.append(normalized_word)

                new_tokens_stwdsremoved = removeStopwords(new_tokens, stopset)

                for index, item in enumerate(rules):
                    intersection_word = set(new_tokens_stwdsremoved).intersection(item)
                    # Tweets are found to have similar words as keywords list
                    if len(intersection_word) == len(item):
                        tweets_contain_RWname[msg_id] += 1

    print '%d total tweets in the data' % len(total_tweets)
    print '%d tweets contains RW name' % len(tweets_contain_RWname)

    return total_tweets, tweets_contain_RWname

def main():
    # mark the beginning time of process
    start = timeit.default_timer()

    EVENT = 'Mon, 11 Aug 2014'
    MONTHS = [u'Jan', u'Feb', u'Mar', u'Apr', u'May', u'Jun', u'Jul', u'Aug', u'Sep', u'Oct', u'Nov', u'Dec']

    # keywords = ['suicide', 'depression', 'seek help', 'suicide lifeline', 'crisis hotline', 'Parkinson\'s disease', 'Robin Williams']
    keywords = ['Robin Williams']

    stopset = build_stopsets()

    data_dir = "/Users/tl8313/Documents/study_robinwilliams/extracted/"
    json_file = data_dir + 'oneyear_sample.json'

    total_tweets, tweets_contain_RWname = separate_tweets_contain_RWname(json_file, keywords, stopset, MONTHS)

    overall_month_tweets_dict = defaultdict(list)

    for msg_id in (set(total_tweets.keys()) - set(tweets_contain_RWname.keys())):

        (message, yearmonth) = total_tweets[msg_id]

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
            if normalized_word != '':
                new_tokens.append(normalized_word)

        new_tokens_stwdsremoved = removeStopwords(new_tokens, stopset)

        overall_month_tweets_dict[yearmonth].extend(new_tokens_stwdsremoved)

    for k, v in overall_month_tweets_dict.items():
        print(k)
        # Calculate frequency distribution
        fdist = nltk.FreqDist(v)
        # Output top 50 words
        for word, frequency in fdist.most_common(10):
            print(u'{} {}'.format(word, frequency))
        print

    ##### mark the ending time of process #####
    end = timeit.default_timer()
    seconds = math.ceil(end - start)
    # Convert Secs Into Human Readable Time String (HH:MM:SS)
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    print "This process took %d:%02d:%02d" % (h, m, s)
    
if __name__ == '__main__':
    main()