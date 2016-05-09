import ujson as json
from collections import defaultdict

def main():
    
    output_dir = '/Users/tl8313/Documents/study_robinwilliams/extracted/for_crowdsourcing/'
    output_json = output_dir + 'job_895195.json'

    labels_dict = defaultdict(list)

    training_json = open(output_dir + 'training.json', 'w')

    for line in open(output_json, "r"):
        tweet = json.loads(line.decode('utf-8'))
        # tweet.keys() = [u'job_id', u'updated_at', u'created_at', u'results', u'agreement', u'missed_count', u'state', u'judgments_count', u'gold_pool', u'data', u'id']

        # tweet['results'].keys() = [u'relevant', u'judgments']
        # tweet['data'].keys() = [u'message', u'msg_id', u'user_id']

        msg_id = tweet['data']['msg_id']
        message = tweet['data']['message']

        label = tweet['results']['relevant']['agg']
        confidence = tweet['results']['relevant']['confidence']

        basic = {}
        basic['msg_id'] = msg_id
        basic['message'] = message

        if label == 'suicidal_thoughts':
            basic['suicidal_label'] = 1
        else:
            basic['suicidal_label'] = -1

        json.dump(basic, training_json)
        training_json.write("\n")

        labels_dict[label].append(msg_id)

    for k, v in labels_dict.items():
        print k, len(v)

if __name__ == '__main__':
    main()