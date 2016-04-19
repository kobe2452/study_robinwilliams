from gensim.models import LdaModel
from gensim.corpora import Dictionary, MmCorpus
import ujson as json
import timeit, math
from nltk.corpus import stopwords
from sklearn import cross_validation
from collections import defaultdict
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from count_keywords import build_stopsets
from wordclouds_plot import get_normalized_word
from NER_tagger import parse_raw_message_emoji
from ark_twokenize import tokenizeRawTweetText

TOPIC_NUM  = 3
WORD_NUM   = 100
DICT       = 'lda.bow.dict'
BOW        = 'lda.bow.mm'
LDA        = 'lda.%03d' % TOPIC_NUM

def pretty_topics(lda_model):
    """
    Args:
        lda_model: gensim LDA model
    Returns:
        a list of frequencies
    """
    frequencies_list = []

    for idx, topic in enumerate(lda_model.show_topics(num_topics=TOPIC_NUM, num_words=WORD_NUM, log=True, formatted=True)):
        print 'Topic %d:' % (idx+1)

        frequency = []
        word_list = set()

        for item in topic[1].split("+"):
            prob = float(item.split("*")[0].strip())
            word = str(item.split("*")[1].strip())
            word_list.add(word)
            print (word, prob)       
            frequency.append( (word, prob) )

        frequencies_list.append(frequency)

    return frequencies_list

def aggregate_tweets_by_users(data_dir, jsonfile, stopset):

    docs = []
    texts = []

    user_origin = defaultdict(list)
    user_normalized = defaultdict(list)

    for line in open(data_dir + jsonfile, "r"):
        tweet = json.loads(line.decode('utf-8'))

        msg_id = tweet['id']
        userid = tweet['user']['id_str']
        user_origin[userid].append(msg_id)

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
            normalized_word = get_normalized_word(word.strip("\n"))
            if normalized_word not in stopset and normalized_word is not "xa0":
                new_tokens.append(normalized_word)
                user_normalized[userid].append(normalized_word)

    docs = user_origin.values()
    texts = user_normalized.values()

    return docs, texts

def always_black(word=None, font_size=None, position=None,
                 orientation=None, font_path=None, random_state=None):
    """
        Always return black color for font
    """
    return "black"

def plot_word_cloud(tuples, index, jsonfile):

    keyword = jsonfile.split(".")[0]

    lda_dir = '/Users/tl8313/Documents/study_robinwilliams/lda/'

    wordcloud = WordCloud(color_func=always_black, background_color='white').fit_words(tuples)

    # Open a plot of the generated image.
    plt.imshow(wordcloud)
    plt.axis("off")
    plt.title('word cloud for ' + keyword + ' tweets at user level')
    plt.savefig(lda_dir + keyword + '_' + str(index+1) + '.png')
    # plt.show()

# def prepare_single_tweet(jsonfile):
#     docs = []
#     texts = []

#     for line in open(jsonfile, "r"):
#         tweet = json.loads(line.decode('utf-8'))

#         msg_id = tweet['msg_id']
#         userid = tweet['userid']
#         message = tweet['message']

#         docs.append(message)

#         normalized_tweet = filter_words(message)

#         # # remove stopwords from normalized tweet
#         # stopwords_removed = []
#         # for word in normalized_tweet:
#         #     if word not in stopset:
#         #         stopwords_removed.append(word)
        
#         # texts.append(stopwords_removed)

#         texts.append(normalized_tweet)

#     return docs, texts

def lda_process(data_dir, jsonfile, stopset):

    print 'Loading documents from %s ...' % (data_dir + jsonfile)
    docs, texts = aggregate_tweets_by_users(data_dir, jsonfile, stopset)

    print '%d documents' % len(docs)

    print 'After preprocessing texts ...'
    print '%d normalized tweets' % len(texts)

    print 'Building dictionary of terms ...'
    dictionary = Dictionary(texts)
    print '%d word types' % len(dictionary)

    print 'Filtering infrequent and frequent terms ...'
    dictionary.filter_extremes(no_below=5, no_above=0.5)
    print '%d word types, after filtering' % len(dictionary)

    print 'Saving dictionary (%s)...' % DICT
    dictionary.save(DICT)

    print 'Building bag-of-words corpus ...'
    bow_corpus = [ dictionary.doc2bow(t) for t in texts ]

    print 'Serializing corpus (%s) ...' % BOW
    MmCorpus.serialize(BOW, bow_corpus)

    training, testing = cross_validation.train_test_split(bow_corpus, test_size=0.1, random_state=5)

    print 'Training LDA w/ %d topics on first %d texts ...' % (TOPIC_NUM, len(training))
    lda = LdaModel(training, id2word=dictionary, num_topics=TOPIC_NUM, passes=5, alpha='symmetric')

    # document_topics = lda.get_document_topics(bow_corpus)
    # for item in document_topics:
    #     print item

    print 'Saving LDA model (%s) ...' % LDA
    lda.save(LDA)

    print 'Random subset of topics:'
    frequencies_list = pretty_topics(lda)

    print 'Computing perplexity on %d held-out documents ...' % len(testing)
    perplexity = 2 ** -(lda.log_perplexity(testing))
    print 'Perplexity: %.2f' % perplexity

    print 'Plot word cloud ...'
    for index, tuples in enumerate(frequencies_list):
        plot_word_cloud(tuples, index, jsonfile)

################################################################################

if __name__ == "__main__":
    # mark the beginning time of process
    start = timeit.default_timer()

    data_dir = "/Users/tl8313/Documents/study_robinwilliams/extracted/"

    stopset = build_stopsets()

    # suicide_json = "suicide.json"
    # depression_json = "depression.json"
    # seekhelp_json = "seek_help.json"
    # suicidelifeline_json = "suicide_lifeline.json"
    # crisishotline_json = "crisis_hotline.json"
    # parkinsons_json = "parkinsons.json"
    # robinwilliams_json = "robin_williams.json"

    # lda_process(data_dir, suicide_json, stopset)
    # lda_process(data_dir, depression_json, stopset)
    # lda_process(data_dir, seekhelp_json, stopset)
    # lda_process(data_dir, suicidelifeline_json, stopset)
    # lda_process(data_dir, crisishotline_json, stopset)
    # lda_process(data_dir, parkinsons_json, stopset)
    # lda_process(data_dir, robinwilliams_json, stopset)

    suicide_json_0 = "suicide_0.json"
    depression_json_0 = "depression_0.json"
    seekhelp_json_0 = "seek_help_0.json"
    suicidelifeline_json_0 = "suicide_lifeline_0.json"
    crisishotline_json_0 = "crisis_hotline_0.json"
    parkinsons_json_0 = "parkinsons_0.json"
    robinwilliams_json_0 = "robin_williams_0.json"

    lda_process(data_dir, suicide_json_0, stopset)
    lda_process(data_dir, depression_json_0, stopset)
    lda_process(data_dir, seekhelp_json_0, stopset)
    lda_process(data_dir, suicidelifeline_json_0, stopset)
    lda_process(data_dir, crisishotline_json_0, stopset)
    lda_process(data_dir, parkinsons_json_0, stopset)
    lda_process(data_dir, robinwilliams_json_0, stopset)

    suicide_json_1 = "suicide_1.json"
    depression_json_1 = "depression_1.json"
    seekhelp_json_1 = "seek_help_1.json"
    suicidelifeline_json_1 = "suicide_lifeline_1.json"
    crisishotline_json_1 = "crisis_hotline_1.json"
    parkinsons_json_1 = "parkinsons_1.json"
    robinwilliams_json_1 = "robin_williams_1.json"

    lda_process(data_dir, suicide_json_1, stopset)
    lda_process(data_dir, depression_json_1, stopset)
    lda_process(data_dir, seekhelp_json_1, stopset)
    lda_process(data_dir, suicidelifeline_json_1, stopset)
    lda_process(data_dir, crisishotline_json_1, stopset)
    lda_process(data_dir, parkinsons_json_1, stopset)
    lda_process(data_dir, robinwilliams_json_1, stopset)

    ##### mark the ending time of process #####
    end = timeit.default_timer()
    seconds = math.ceil(end - start)
    # Convert Secs Into Human Readable Time String (HH:MM:SS)
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    print "This process took %d:%02d:%02d" % (h, m, s)
