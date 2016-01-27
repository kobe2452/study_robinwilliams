import ujson as json
import timeit, math, re, string, HTMLParser
from collections import defaultdict
from ark_twokenize import tokenizeRawTweetText
from NER_tagger import parse_raw_message_emoji
from count_keywords import build_stopsets, process_keywords
from wordclouds_plot import get_normalized_word
import matplotlib.pyplot as plt
import plotly.plotly as py
from plotly.graph_objs import *

def count_all_data_keywords(fileName, keywords, stopset, MONTHS):

    print 'Counting keywords in file: ' + fileName

    rules = process_keywords(keywords)

    keywords_dict = defaultdict(list)
    messages_normalized_word_dict = {}
    tweet_keywords_dict = defaultdict(list)
    overall_month_tweets_dict = defaultdict(list)

    for line in open(fileName, "r"):
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

                overall_month_tweets_dict[year + two_digit_month].append(msg_id)

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
                    new_tokens.append(normalized_word)
                messages_normalized_word_dict[msg_id] = new_tokens

                for index, item in enumerate(rules):
                    intersection_word = set(new_tokens).intersection(item)
                    # Tweets are found to have similar words as keywords list
                    if len(intersection_word) == len(item):
                        keywords_dict[index].append(msg_id)
                        tweet_keywords_dict[msg_id].append(index)

    return keywords_dict, messages_normalized_word_dict, tweet_keywords_dict, overall_month_tweets_dict

def count_tweets_each_month(data_dir, fileName, MONTHS, stopset):

    print "processing %s" % (data_dir + fileName)

    subset_tweets_month_dict = defaultdict(list)
    messages_dict = {}
    monthly_words_count = dict()

    for line in open(data_dir + fileName, "r"):
        tweet = json.loads(line.decode('utf-8'))

        if 'lang' in tweet:                
            language = tweet['lang']

            # Only process and analyze tweets written in English
            if language == 'en':
                
                msg_id = tweet['id']

                timestamp = tweet['created_at'].split()
                day = timestamp[0].strip(",")
                date = timestamp[1]
                month = timestamp[2]
                year = timestamp[3]
                two_digit_month = '%02d' % int(MONTHS.index(month)+1)

                subset_tweets_month_dict[msg_id] = year + two_digit_month

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
                    new_tokens.append(normalized_word)
                messages_dict[msg_id] = new_tokens

                try:
                    monthly_words_count[year + two_digit_month] += len(new_tokens)
                except KeyError:
                    monthly_words_count[year + two_digit_month] = len(new_tokens)

    print "Numbers of normalized words in each month:"
    for k, v in sorted(monthly_words_count.items(), key=lambda t: t[0]):
        print k, v

    return subset_tweets_month_dict, messages_dict, monthly_words_count

def plot_word_produced_tweets(month_array, ratio_array, word):

    trace = Scatter(
        x = month_array,
        y = ratio_array,
        mode = 'lines',
        name = 'lines'
    )
    data = [trace]
    layout = Layout(
        title = 'From the tweets drawn from all the keyword queries EXCEPT ' + word,
        width = 1500,
        xaxis = XAxis(
            title = 'each month from 2014-02 to 2015-02'
        ),
        yaxis = YAxis(
            title = 'percentage of ' + word + ' VS. all tokens'
        )
    )
    fig = Figure(
        data = data,
        layout = layout
    )
    plot_url = py.plot(fig, filename = word + '_except_percentage.png')

def main():
    # mark the beginning time of process
    start = timeit.default_timer()

    EVENT = 'Mon, 11 Aug 2014'
    MONTHS = [u'Jan', u'Feb', u'Mar', u'Apr', u'May', u'Jun', u'Jul', u'Aug', u'Sep', u'Oct', u'Nov', u'Dec']

    keywords = ['suicide', 'depression', 'seek help', 'suicide lifeline', 'crisis hotline', 'Parkinson\'s disease', 'Robin Williams']

    stopset = build_stopsets()

    data_dir = "/Users/tl8313/Documents/study_robinwilliams/extracted/"
    fileName = data_dir + 'oneyear_sample.json'

    suicide_json = "suicide.json"
    depression_json = "depression.json"
    seekhelp_json = "seek_help.json"
    suicidelifeline_json = "suicide_lifeline.json"
    crisishotline_json = "crisis_hotline.json"
    parkinsons_json = "parkinsons.json"
    robinwilliams_json = "robin_williams.json"

    json_files = [suicide_json, depression_json, seekhelp_json, suicidelifeline_json, crisishotline_json, parkinsons_json, robinwilliams_json]

    keywords_dict, messages_normalized_word_dict, tweet_keywords_dict, overall_month_tweets_dict = count_all_data_keywords(fileName, keywords, stopset, MONTHS)

    suicide_month_dict, suicide_messages, suicide_monthly_words_count = count_tweets_each_month(data_dir, suicide_json, MONTHS, stopset)
    depression_month_dict, depression_messages, depression_monthly_words_count = count_tweets_each_month(data_dir, depression_json, MONTHS, stopset)
    seekhelp_month_dict, seekhelp_messages, seekhelp_monthly_words_count = count_tweets_each_month(data_dir, seekhelp_json, MONTHS, stopset)
    suicidelifeline_month_dict, suicidelifeline_messages, suicidelifeline_monthly_words_count = count_tweets_each_month(data_dir, suicidelifeline_json, MONTHS, stopset)
    crisishotline_month_dict, crisishotline_messages, crisishotline_monthly_words_count = count_tweets_each_month(data_dir, crisishotline_json, MONTHS, stopset)
    parkinsons_month_dict, parkinsons_messages, parkinsons_monthly_words_count = count_tweets_each_month(data_dir, parkinsons_json, MONTHS, stopset)
    robinwilliams_month_dict, robinwilliams_messages, robinwilliams_monthly_words_count = count_tweets_each_month(data_dir, robinwilliams_json, MONTHS, stopset)

    keyword_messages_list = [suicide_messages, depression_messages, seekhelp_messages, suicidelifeline_messages, crisishotline_messages, parkinsons_messages, robinwilliams_messages]

    keyword_monthly_words_count_list = [suicide_monthly_words_count, depression_monthly_words_count, seekhelp_monthly_words_count, suicidelifeline_monthly_words_count, crisishotline_monthly_words_count, parkinsons_monthly_words_count, robinwilliams_monthly_words_count]

    ##### 0 suicide #####
    print "suicide"
    suicide_except_month_dict = defaultdict(int)
    for k, v in suicide_messages.items():
        msg_id = k
        for tweets in [x for x in keyword_messages_list if x is not suicide_messages]:
            if msg_id in tweets:
                new_tokens = messages_normalized_word_dict[msg_id]
                yearmonth = suicide_month_dict[msg_id]
                suicide_except_month_dict[yearmonth] += len(new_tokens)

    month_array = []
    suicide_except_ratio_array = []

    for k, v in sorted(suicide_except_month_dict.items(), key=lambda t: t[0]):
        total_words = 0
        for count_dict in [x for x in keyword_monthly_words_count_list if x is not suicide_monthly_words_count]:
            total_words += count_dict[k]
        percentage = v / float(total_words) * 100
        print k, percentage
        month_array.append(k[:4] + '_' + k[4:])
        suicide_except_ratio_array.append(percentage)

    plot_word_produced_tweets(month_array, suicide_except_ratio_array, keywords[0])

    ##### 1 depression #####
    print "depression"
    depression_except_month_dict = defaultdict(int)
    for k, v in depression_messages.items():
        msg_id = k
        for tweets in [x for x in keyword_messages_list if x is not depression_messages]:
            if msg_id in tweets:
                new_tokens = messages_normalized_word_dict[msg_id]
                yearmonth = depression_month_dict[msg_id]
                depression_except_month_dict[yearmonth] += len(new_tokens)

    month_array = []
    depression_except_ratio_array = []

    for k, v in sorted(depression_except_month_dict.items(), key=lambda t: t[0]):
        total_words = 0
        for count_dict in [x for x in keyword_monthly_words_count_list if x is not depression_monthly_words_count]:
            total_words += count_dict[k]
        percentage = v / float(total_words) * 100
        print k, percentage
        month_array.append(k[:4] + '_' + k[4:])
        depression_except_ratio_array.append(percentage)

    plot_word_produced_tweets(month_array, depression_except_ratio_array, keywords[1])

    ##### 2 seek help #####
    print "seek help"
    seekhelp_except_month_dict = defaultdict(int)
    for k, v in seekhelp_messages.items():
        msg_id = k
        for tweets in [x for x in keyword_messages_list if x is not seekhelp_messages]:
            if msg_id in tweets:
                new_tokens = messages_normalized_word_dict[msg_id]
                yearmonth = seekhelp_month_dict[msg_id]
                seekhelp_except_month_dict[yearmonth] += len(new_tokens)

    month_array = []
    seekhelp_except_ratio_array = []

    for k, v in sorted(seekhelp_except_month_dict.items(), key=lambda t: t[0]):
        total_words = 0
        for count_dict in [x for x in keyword_monthly_words_count_list if x is not seekhelp_monthly_words_count]:
            total_words += count_dict[k]
        percentage = v / float(total_words) * 100
        print k, percentage
        month_array.append(k[:4] + '_' + k[4:])
        seekhelp_except_ratio_array.append(percentage)

    plot_word_produced_tweets(month_array, seekhelp_except_ratio_array, keywords[2])

    ##### 3 suicide lifeline #####
    print "suicide lifeline"
    suicidelifeline_except_month_dict = defaultdict(int)
    for k, v in suicidelifeline_messages.items():
        msg_id = k
        for tweets in [x for x in keyword_messages_list if x is not suicidelifeline_messages]:
            if msg_id in tweets:
                new_tokens = messages_normalized_word_dict[msg_id]
                yearmonth = suicidelifeline_month_dict[msg_id]
                suicidelifeline_except_month_dict[yearmonth] += len(new_tokens)

    month_array = []
    suicidelifeline_except_ratio_array = []

    for k, v in sorted(suicidelifeline_except_month_dict.items(), key=lambda t: t[0]):
        total_words = 0
        for count_dict in [x for x in keyword_monthly_words_count_list if x is not suicidelifeline_monthly_words_count]:
            total_words += count_dict[k]
        percentage = v / float(total_words) * 100
        print k, percentage
        month_array.append(k[:4] + '_' + k[4:])
        suicidelifeline_except_ratio_array.append(percentage)

    plot_word_produced_tweets(month_array, suicidelifeline_except_ratio_array, keywords[3])

    ##### 4 crisis hotline #####
    print "crisis hotline"
    crisishotline_except_month_dict = defaultdict(int)
    for k, v in crisishotline_messages.items():
        msg_id = k
        for tweets in [x for x in keyword_messages_list if x is not crisishotline_messages]:
            if msg_id in tweets:
                new_tokens = messages_normalized_word_dict[msg_id]
                yearmonth = crisishotline_month_dict[msg_id]
                crisishotline_except_month_dict[yearmonth] += len(new_tokens)

    month_array = []
    crisishotline_except_ratio_array = []

    for k, v in sorted(crisishotline_except_month_dict.items(), key=lambda t: t[0]):
        total_words = 0
        for count_dict in [x for x in keyword_monthly_words_count_list if x is not crisishotline_monthly_words_count]:
            total_words += count_dict[k]
        percentage = v / float(total_words) * 100
        print k, percentage
        month_array.append(k[:4] + '_' + k[4:])
        crisishotline_except_ratio_array.append(percentage)

    plot_word_produced_tweets(month_array, crisishotline_except_ratio_array, keywords[4])

    ##### 5 Parkinson's disease #####
    print "Parkinson\'s disease"
    parkinsons_except_month_dict = defaultdict(int)
    for k, v in parkinsons_messages.items():
        msg_id = k
        for tweets in [x for x in keyword_messages_list if x is not parkinsons_messages]:
            if msg_id in tweets:
                new_tokens = messages_normalized_word_dict[msg_id]
                yearmonth = parkinsons_month_dict[msg_id]
                parkinsons_except_month_dict[yearmonth] += len(new_tokens)

    month_array = []
    parkinsons_except_ratio_array = []

    for k, v in sorted(parkinsons_except_month_dict.items(), key=lambda t: t[0]):
        total_words = 0
        for count_dict in [x for x in keyword_monthly_words_count_list if x is not parkinsons_monthly_words_count]:
            total_words += count_dict[k]
        percentage = v / float(total_words) * 100
        print k, percentage
        month_array.append(k[:4] + '_' + k[4:])
        parkinsons_except_ratio_array.append(percentage)

    plot_word_produced_tweets(month_array, parkinsons_except_ratio_array, keywords[5])

    ##### 6 Robin Williams #####
    print "Robin Williams"
    robinwilliams_except_month_dict = defaultdict(int)
    for k, v in robinwilliams_messages.items():
        msg_id = k
        for tweets in [x for x in keyword_messages_list if x is not robinwilliams_messages]:
            if msg_id in tweets:
                new_tokens = messages_normalized_word_dict[msg_id]
                yearmonth = robinwilliams_month_dict[msg_id]
                robinwilliams_except_month_dict[yearmonth] += len(new_tokens)

    month_array = []
    robinwilliams_except_ratio_array = []

    for k, v in sorted(robinwilliams_except_month_dict.items(), key=lambda t: t[0]):
        total_words = 0
        for count_dict in [x for x in keyword_monthly_words_count_list if x is not robinwilliams_monthly_words_count]:
            total_words += count_dict[k]
        percentage = v / float(total_words) * 100
        print k, percentage
        month_array.append(k[:4] + '_' + k[4:])
        robinwilliams_except_ratio_array.append(percentage)

    plot_word_produced_tweets(month_array, robinwilliams_except_ratio_array, keywords[6])

    ##### mark the ending time of process #####
    end = timeit.default_timer()
    seconds = math.ceil(end - start)
    # Convert Secs Into Human Readable Time String (HH:MM:SS)
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    print "This process took %d:%02d:%02d" % (h, m, s)
    
if __name__ == '__main__':
    main()