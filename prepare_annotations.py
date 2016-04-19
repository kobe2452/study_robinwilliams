import ujson as json
import timeit, math, re, string, sys, HTMLParser, nltk, random, csv
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

    case1_matched = defaultdict(int)
    case2_matched = defaultdict(int)
    case3_matched = defaultdict(int)
    case4_matched = defaultdict(int)
    case5_matched = defaultdict(int)
    case6_matched = defaultdict(int)

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

                # # define a dictionary
                # mixd = {}

                overall_tweets[msg_id] = [user_id, message]

                text_tokens = my_tokenizer(message)
                
                # tweet_length_records.append(len(text_tokens))

                if len(text_tokens) >= 5:

                    overall_long_tweets[msg_id] += 1

                    # search for patterns 
                    term1a = re.search(r'.+(\b(cutting|depres|sui)|these|bad|sad).+(thoughts|feel).+', message, re.M|re.I)
                    term1b = re.search(r'.+\b(wan).+die.+', message, re.M|re.I)
                    term1c = re.search(r'.+\b(end).+\b(all|it|life).+', message, re.M|re.I)
                    term1d = re.search(r'.+\b(can.+|don.+|take).+((go\ on)|live|(any\ more)|cop|alive).+', message, re.M|re.I)

                    term2a = re.search(r'.+\b(need|ask|call|offer).+help.+', message, re.M|re.I)
                    term2b = re.search(r'\bshut|stop\bbullying', message, re.M|re.I)

                    term3a = re.search(r'.+\b(kill|hat|throw).+', message, re.M|re.I)
                    term3b = re.search(r'.+\bfuck.+', message, re.M|re.I)
                    term3c = re.search(r'.+(boy|girl).?friend', message, re.M|re.I)
                    term3d = re.search(r'.+\bjust.+like.+', message, re.M|re.I)

                    term4a = re.search(r'.+\b(talk|speak).+\bto.+(\bone|\bsome|\bany).+', message, re.M|re.I)
                    term4b = re.search(r'.+\b(web|blog|health|advice).+', message, re.M|re.I)

                    term5a = re.search(r'.+?\b\ miss.+\b(you|her|him)\b.+', message, re.M|re.I)
                    term5b = re.search(r'.+\b(kill|die|comm).+(day|month|year).+', message, re.M|re.I)

                    term6a = re.search(r'.+\b(took|take).+\bown.+\blife.+', message, re.M|re.I)
                    term6b = re.search(r'.+\b(hanged|hanging|overdose).+', message, re.M|re.I)

                    if term1a or term1b or term1c or term1d:
                        # mixd['message'] = message
                        # mixd['msg_id'] = msg_id
                        # mixd['userid'] = userid
                        # json.dump(mixd, mixf)
                        # mixf.write("\n")
                        matched_tweets[msg_id] += 1
                        case1_matched[msg_id] += 1
                    elif term2a or term2b:
                        matched_tweets[msg_id] += 1
                        case2_matched[msg_id] += 1
                    elif term3a or term3b or term3c or term3d:
                        matched_tweets[msg_id] += 1
                        case3_matched[msg_id] += 1
                    elif term4a or term4b:
                        matched_tweets[msg_id] += 1
                        case4_matched[msg_id] += 1
                    elif term5a or term5b:
                        matched_tweets[msg_id] += 1
                        case5_matched[msg_id] += 1
                    elif term6a or term6b:
                        matched_tweets[msg_id] += 1
                        case6_matched[msg_id] += 1

    # print np.mean(tweet_length_records)
    # plt.hist(tweet_length_records)
    # plt.title("Tweets Lengths Histogram")
    # plt.xlabel("Token counts")
    # plt.ylabel("Frequency")
    # plt.savefig('tweet_length_histogram.png', bbox_inches='tight')

    return overall_tweets, overall_long_tweets, matched_tweets, case1_matched, case2_matched, case3_matched, case4_matched, case5_matched, case6_matched

def randomize_samples(myList, sample_size):

    indices = random.sample(range(len(myList)), sample_size)

    return [myList[i] for i in indices]

# def export_lists_to_csv(list_all, filename, overall_tweets):

#     with open(filename, 'wb') as f:
#         writer = csv.writer(f)

#         for item in list_all:
#             print len(item)

#         # Create headers in a row, from 1 to the end of onelist
#         headers = []
#         for i in range(len(list_all[0])):
#             # index starts from 1 (i+1)
#             header1 = "msg_id" + str(i+1)
#             header2 = "user_id" + str(i+1)
#             header3 = "message" + str(i+1)
#             headers.append(header1)
#             headers.append(header2)
#             headers.append(header3)
#         writer.writerow(headers)

#         # export data from onelist to a list
#         attributes = ['msg_id', 'user_id', 'message']

#         for onelist in list_all:
#             csv_row_data = []
#             for msg_id in onelist:
#                 csv_row_data.append(msg_id)
#                 user_id = overall_tweets[msg_id][0]
#                 csv_row_data.append(user_id)
#                 message = overall_tweets[msg_id][1]
#                 csv_row_data.append(unicode(message).encode("utf-8"))
#             writer.writerow(csv_row_data)

def export_samples_to_csv(samples, filename, overall_tweets):

    with open(filename, 'wb') as f:
        writer = csv.writer(f)

        headers = ['msg_id', 'user_id', 'message']
        writer.writerow(headers)

        for msg_id in samples:
            csv_row_data = []
            csv_row_data.append(msg_id)
            user_id = overall_tweets[msg_id][0]
            csv_row_data.append(user_id)
            message = overall_tweets[msg_id][1]
            csv_row_data.append(unicode(message).encode("utf-8"))
            writer.writerow(csv_row_data)

def main():
    # mark the beginning time of process
    start = timeit.default_timer()

    data_dir = '/Users/tl8313/Documents/study_robinwilliams/extracted/'
    data_json = data_dir + 'oneyear_sample.json'

    overall_tweets, overall_long_tweets, matched_tweets, case1_matched, case2_matched, case3_matched, case4_matched, case5_matched, case6_matched = matchWords(data_json, data_dir)

    print "there are a total of %d tweets" % len(overall_tweets)
    print "%d tweets have more than 5 tokens" % len(overall_long_tweets)
    print "%d tweets matched by the text filters" % len(matched_tweets)

    # for index, matched in enumerate([case1_matched, case2_matched, case3_matched, case4_matched, case5_matched, case6_matched]):
    #     print index+1, len(matched)
    #     samples = randomize_samples(matched.keys(), 100)
    #     filename = data_dir + str(index+1) + ".csv"
    #     print filename
    #     export_samples_to_csv(samples, filename, overall_tweets)

    notmatched = list(set(overall_long_tweets.keys()) - set(matched_tweets.keys()))
    export_samples_to_csv(randomize_samples(notmatched, 100), data_dir + "7.csv", overall_tweets)

    ##### mark the ending time of process #####
    end = timeit.default_timer()
    seconds = math.ceil(end - start)
    # Convert Secs Into Human Readable Time String (HH:MM:SS)
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    print "This process took %d:%02d:%02d" % (h, m, s)

if __name__ == '__main__':
    main()