import timeit, math, nltk
from count_keywords import build_stopsets, process_keywords
from collections import defaultdict, OrderedDict
import ujson as json
from ark_twokenize import tokenizeRawTweetText
from NER_tagger import parse_raw_message_emoji
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# Given a list of words, remove any that are in a list of stop words.
def removeStopwords(wordlist, stopset):
    return [w for w in wordlist if w not in stopset]

def plot_word_cloud_from_tuples(tuples, yearmonth):

    directory = '/Users/tl8313/Documents/study_robinwilliams/figures/monthly_hashtags/'

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

def separate_tweets_contain_RWname(json_file, keywords, stopset, MONTHS):

    rules = process_keywords(keywords)

    total_tweets = {}
    monthly_hashtags_dict = defaultdict(list)

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

                for word in tokens:
                    if word[0] == '#':
                        hashtag = word.strip('.,*;-:"\'`?!)(#').lower()
                        monthly_hashtags_dict[year+two_digit_month].append(hashtag)

    print '%d total tweets in the data' % len(total_tweets)

    return total_tweets, monthly_hashtags_dict

def main():
    # mark the beginning time of process
    start = timeit.default_timer()

    EVENT = 'Mon, 11 Aug 2014'
    MONTHS = [u'Jan', u'Feb', u'Mar', u'Apr', u'May', u'Jun', u'Jul', u'Aug', u'Sep', u'Oct', u'Nov', u'Dec']

    keywords = ['suicide', 'depression', 'seek help', 'suicide lifeline', 'crisis hotline', 'Parkinson\'s disease', 'Robin Williams']

    stopset = build_stopsets()

    data_dir = "/Users/tl8313/Documents/study_robinwilliams/extracted/"
    json_file = data_dir + 'oneyear_sample.json'

    total_tweets, monthly_hashtags_dict = separate_tweets_contain_RWname(json_file, keywords, stopset, MONTHS)

    for yearmonth, v in OrderedDict(sorted(monthly_hashtags_dict.items(), key=lambda t: t[0])).items():
        print yearmonth, len(v)
        f = open('/Users/tl8313/Documents/study_robinwilliams/figures/monthly_hashtags/'+yearmonth, 'w')
        f.write(str(yearmonth) + "----" + str(len(v)) + "\n")

        # Calculate frequency distribution
        fdist = nltk.FreqDist(v)

        tuples = []
        factor = 1.0 / sum(fdist.itervalues())
        # normalised_fdist = {k : v*factor for k, v in fdist.iteritems()}
        for k, v in fdist.iteritems():
            tuples.append((k, v*factor))
            if len(k) > 0: 
                f.write(k + "    " + str(v) + "\n")
        f.close()

        # plot_word_cloud_from_tuples(tuples, yearmonth)

    ##### mark the ending time of process #####
    end = timeit.default_timer()
    seconds = math.ceil(end - start)
    # Convert Secs Into Human Readable Time String (HH:MM:SS)
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    print "This process took %d:%02d:%02d" % (h, m, s)
    
if __name__ == '__main__':
    main()