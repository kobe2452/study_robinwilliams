import ujson as json
from collections import defaultdict
import timeit, math, csv, random

def export_samples_to_csv(sample_msgids, overall_tweets, filename):

    with open(filename, 'wb') as f:
        writer = csv.writer(f)

        headers = ['msg_id', 'user_id', 'message']
        writer.writerow(headers)

        for msg_id in sample_msgids:
            csv_row_data = []
            csv_row_data.append(msg_id)

            user_id = overall_tweets[msg_id]['user_id']
            csv_row_data.append(str(user_id))

            message = overall_tweets[msg_id]['message']
            csv_row_data.append(unicode(message).encode("utf-8"))

            writer.writerow(csv_row_data)

    print 'Output to: %s' % filename

def count_tweets_in_each_category(labels_dict):

    total = 0

    for k, v in labels_dict.items():
        print k, len(v)
        total += len(v)

    print total

def extract_annotations_from_CFjson(output_json):

    tweets_dict = defaultdict(list)
    labels_dict = defaultdict(list)

    # training_json = open(output_dir + 'training.json', 'w')

    unanimous_ids = []
    discordant_ids = [] 

    for line in open(output_json, "r"):
        tweet = json.loads(line.decode('utf-8'))
        # tweet.keys() = [u'job_id', u'updated_at', u'created_at', u'results', u'agreement', u'missed_count', u'state', u'judgments_count', u'gold_pool', u'data', u'id']

        # tweet['results'].keys() = [u'relevant', u'judgments']
        for item in (tweet['results']['judgments']):
            # item.keys() = [u'unit_data', u'golden', u'trust', u'missed', u'unit_state', u'city', u'country', u'created_at', u'job_id', u'rejected', u'id', u'worker_trust', u'worker_id', u'tainted', u'unit_id', u'region', u'started_at', u'data', u'external_type', u'acknowledged_at']

            annotation = item['data']['relevant']
            annotation_trust = item['trust']
            worker_trust = item['worker_trust']

        # tweet['data'].keys() = [u'message', u'msg_id', u'user_id']
        msg_id = tweet['data']['msg_id']
        message = tweet['data']['message']
        tweets_dict[msg_id] = tweet['data']

        # Best Answer ('agg') - Returns the highest confidence response
        label = tweet['results']['relevant']['agg']
        confidence = tweet['results']['relevant']['confidence']

        ##### BUILD TRAINING JSON #####
        basic = {}
        basic['msg_id'] = msg_id
        basic['message'] = message

        if label == 'suicidal_thoughts':
            basic['suicidal_label'] = 1
        else:
            basic['suicidal_label'] = -1

        # json.dump(basic, training_json)
        # training_json.write("\n")

        ##### AGGREGATE LABELS BY TWEET IDS #####
        labels_dict[label].append(msg_id)

        ##### OUPUT TWEETS W/ DISCORDANT LABELS, FOR FURTHER ANNOTATIONS #####
        agreement = tweet['agreement']
        if agreement != 1.0:
            discordant_ids.append(msg_id)
        else:
            unanimous_ids.append(msg_id)

    return tweets_dict, labels_dict, unanimous_ids, discordant_ids

def main():
    # mark the beginning time of process
    start = timeit.default_timer()
    
    output_dir = '/Users/tl8313/Documents/study_robinwilliams/extracted/for_crowdsourcing/'
    output_json = output_dir + 'job_895195.json'

    tweets_dict, labels_dict, unanimous_ids, discordant_ids = extract_annotations_from_CFjson(output_json)
    print 'unanimous_ids: %d' % len(unanimous_ids)
    print 'discordant_ids: %d' % len(discordant_ids)

    print

    count_tweets_in_each_category(labels_dict)

    print

    nextround_CSV = output_dir + 'R1_discordant_labels.csv'
    random.shuffle(discordant_ids)
    export_samples_to_csv(discordant_ids, tweets_dict, nextround_CSV)

    ##### mark the ending time of process #####
    end = timeit.default_timer()
    seconds = math.ceil(end - start)
    # Convert Secs Into Human Readable Time String (HH:MM:SS)
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    print "This process took %d:%02d:%02d" % (h, m, s)

if __name__ == '__main__':
    main()