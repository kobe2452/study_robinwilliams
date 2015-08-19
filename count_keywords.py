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

def count_keywords_all(fileName, rules):

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
                        # print intersection_word, item, message

                        keywords_dict[rules.index(item)] += 1

    for k, v in keywords_dict.items():
        print rules[k], v

def process_keywords(keywords):

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

def main():
    # mark the beginning time of process
    start = timeit.default_timer()

    fileName = 'oneyear_sample.json'
    print 'Counting keywords in file: ' + fileName

    keywords = ['suicide', 'depression', 'media guideline', 'seek help', 'suicide lifeline', 'crisis hotline', 'Parkinson\'s', 'Robin Williams']
    rules = process_keywords(keywords)

    count_keywords_all(fileName, rules)


    ##### mark the ending time of process #####
    end = timeit.default_timer()
    seconds = math.ceil(end - start)
    # Convert Secs Into Human Readable Time String (HH:MM:SS)
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    print "This process took %d:%02d:%02d" % (h, m, s)

if __name__ == '__main__':
    main()