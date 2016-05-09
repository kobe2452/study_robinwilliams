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

def read_data_json(data_json):

    overall_tweets = defaultdict(list)
    overall_long_tweets = defaultdict(int)

    for line in open(data_json, "r"):
        tweet = json.loads(line.decode('utf-8'))

        if 'lang' in tweet:                
            language = tweet['lang']

            # Only process and analyze tweets written in English
            if language == 'en':

                message = tweet['text']
                msg_id = tweet['id']
                user_id = tweet['user']['id_str']
                overall_tweets[msg_id] = [user_id, message]

                text_tokens = my_tokenizer(message)
                if len(text_tokens) >= 5:
                    # print message, msg_id, user_id
                    overall_long_tweets[msg_id] += 1

    return overall_tweets, overall_long_tweets

def randomize_samples(myList, sample_size):

    indices = random.sample(range(len(myList)), sample_size)

    return [myList[i] for i in indices]

def match_patterns_in_each_message(msg_id, message, matched_tweets, case1_matched, case2_matched, case3_matched, case4_matched, case5_matched, case6_matched):

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

    return matched_tweets, case1_matched, case2_matched, case3_matched, case4_matched, case5_matched, case6_matched

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
            csv_row_data.append(str(user_id))
            message = overall_tweets[msg_id][1]
            # de-indentify tweets and remove non-printable characters
            message = protect_info(message)
            csv_row_data.append(unicode(message).encode("utf-8"))
            writer.writerow(csv_row_data)

def protect_info(message):

    # de-indentify tweets and remove non-printable characters
    message = re.sub('\s+', ' ', message)
    message = re.sub('(@\S+)', '@SOMEONE', message)
    message = re.sub('https?:\/\/.*[\r\n]*', 'http://LINK', message)        
    message = filter(lambda x: x in string.printable, message)

    return message

def main():
    # mark the beginning time of process
    start = timeit.default_timer()

    ##### datasift format #####
    rochester_json1 = '/Users/tl8313/Documents/work_project/Extracted/new1year.json'
    print rochester_json1
    roc1_overall_tweets, roc1_overall_long_tweets = read_data_json(rochester_json1)
    print "there are a total of %d tweets" % len(roc1_overall_tweets)
    print "%d tweets have more than 5 tokens" % len(roc1_overall_long_tweets)

    ##### twitter format #####
    detroit_json = '/Users/tl8313/Documents/Data_Sets/detroit/Extracted/twitter5_detroit.json'
    print detroit_json
    dt_overall_tweets, dt_overall_long_tweets = read_data_json(detroit_json)
    print "there are a total of %d tweets" % len(dt_overall_tweets)
    print "%d tweets have more than 5 tokens" % len(dt_overall_long_tweets)

    rochester_json2 = '/Users/tl8313/Documents/Data_Sets/greater_roch_filtered/Extracted/twitter5_greater_roch_filtered.json'
    print rochester_json2
    roc2_overall_tweets, roc2_overall_long_tweets = read_data_json(rochester_json2)
    print "there are a total of %d tweets" % len(roc2_overall_tweets)
    print "%d tweets have more than 5 tokens" % len(roc2_overall_long_tweets)

    nyc_json = '/Users/tl8313/Documents/Data_Sets/NYC/09-2016_NYC.json'
    print nyc_json
    nyc_overall_tweets, nyc_overall_long_tweets = read_data_json(nyc_json)
    print "there are a total of %d tweets" % len(nyc_overall_tweets)
    print "%d tweets have more than 5 tokens" % len(nyc_overall_long_tweets)

    overall_tweets = {}
    for area_tweets in [roc1_overall_tweets, dt_overall_tweets, roc2_overall_tweets, nyc_overall_tweets]:
        for k, v in area_tweets.items():
            overall_tweets[k] = v

    roc1_samples = randomize_samples(roc1_overall_long_tweets.keys(), 20000)
    dt_samples = randomize_samples(dt_overall_long_tweets.keys(), 20000)
    roc2_samples = randomize_samples(roc2_overall_long_tweets.keys(), 20000)
    nyc_samples = randomize_samples(nyc_overall_long_tweets.keys(), 20000)

    total_samples = roc1_samples + dt_samples + roc2_samples + nyc_samples
    print type(total_samples), len(total_samples)

    matched_tweets = defaultdict(int)
    case1_matched = defaultdict(int)
    case2_matched = defaultdict(int)
    case3_matched = defaultdict(int)
    case4_matched = defaultdict(int)
    case5_matched = defaultdict(int)
    case6_matched = defaultdict(int)

    for msg_id in total_samples:
        message = overall_tweets[msg_id][1]
        matched_tweets, case1_matched, case2_matched, case3_matched, case4_matched, case5_matched, case6_matched = match_patterns_in_each_message(msg_id, message, matched_tweets, case1_matched, case2_matched, case3_matched, case4_matched, case5_matched, case6_matched)

    data_dir = '/Users/tl8313/Documents/study_robinwilliams/extracted/for_crowdsourcing/'

    matched_samples = []
    filename = data_dir + "areas_source_samples_800.csv"

    for index, matched in enumerate([case1_matched, case2_matched, case3_matched, case4_matched, case5_matched, case6_matched]):
        print index+1, len(matched)
        # filename = data_dir + str(index+1) + "_areas.csv"
        # print filename
        # export_samples_to_csv(matched.keys(), filename, overall_tweets)

        matched_samples += matched.keys()

    samples = randomize_samples(matched_samples, 800)
    random.shuffle(samples)
    print filename
    print len(matched_samples), len(samples)
    export_samples_to_csv(samples, filename, overall_tweets)

    ##### mark the ending time of process #####
    end = timeit.default_timer()
    seconds = math.ceil(end - start)
    # Convert Secs Into Human Readable Time String (HH:MM:SS)
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    print "This process took %d:%02d:%02d" % (h, m, s)

if __name__ == '__main__':
    main()