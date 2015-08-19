import ujson as json
import timeit, math, HTMLParser, re, string, nltk
from ark_twokenize import tokenizeRawTweetText
from collections import defaultdict

p = re.compile(r'^#*[a-z]+[\'-/]*[a-z]*$', re.UNICODE)
pLink = re.compile(r'https*:\S+\.\w+', re.IGNORECASE)
pMention = re.compile(r'@[A-Za-z0-9_]+\b')
pNewLine = re.compile(r'[\r\n]+')
pRetweet = re.compile(r'\brt\b', re.IGNORECASE)
punctuation = { 0x2018:0x27, 0x2019:0x27, 0x201C:0x22, 0x201D:0x22 }
h = HTMLParser.HTMLParser()

def count_all_data_keywords(fileName, keywords):

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

                for item in rules:
                    intersection_word = set(new_tokens).intersection(item)
                    if len(intersection_word) == len(item):
                        keywords_dict[rules.index(item)] += 1

    for k, v in keywords_dict.items():
        print keywords[k], v

    return keywords_dict

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
        word = word.translate(punctuation).encode('ascii', 'ignore')  # find ASCII equivalents for unicode quotes
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

def compare_user_ids_change(fileName):

    day_dict = defaultdict(int)
    date_dict = defaultdict(int)
    month_dict = defaultdict(int)
    year_dict = defaultdict(int)

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

                day = timestamp[0]
                date = timestamp[1]
                month = timestamp[2]
                year = timestamp[3]

                day_dict[day] += 1
                date_dict[date] += 1
                month_dict[month] += 1
                year_dict[year] += 1

    # for dic in [day_dict, date_dict, month_dict, year_dict]:
    #     for k, v in dic.items():
    #         print k, v
    #     print
    
    

def main():
    # mark the beginning time of process
    start = timeit.default_timer()

    fileName = 'oneyear_sample.json'
    print 'Counting keywords in file: ' + fileName

    keywords = ['suicide', 'depression', 'media guideline', 'seek help', 'suicide lifeline', 'crisis hotline', 'Parkinson\'s', 'Robin Williams']

    # keywords_dict = count_all_data_keywords(fileName, keywords)

    compare_user_ids_change(fileName)

    ##### mark the ending time of process #####
    end = timeit.default_timer()
    seconds = math.ceil(end - start)
    # Convert Secs Into Human Readable Time String (HH:MM:SS)
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    print "This process took %d:%02d:%02d" % (h, m, s)

if __name__ == '__main__':
    main()