from sklearn.externals import joblib
import ujson as json
import timeit, math
from collections import defaultdict

def build_trained_tweetsID_dict(trained_data):

    trained_dict = defaultdict(int)

    for line in open(trained_data, "r"):
        tweet = json.loads(line.decode('utf-8'))
        msg_id = tweet['msg_id']
        trained_dict[msg_id] += 1

    return trained_dict

def main():
    # mark the beginning time of process
    start = timeit.default_timer()

    ##### find out those tweets which have been trained #####
    annotated_dir = "/Users/tl8313/Documents/study_robinwilliams/extracted/for_crowdsourcing/"
    trained_data = annotated_dir + 'training.json'
    trained_dict = build_trained_tweetsID_dict(trained_data)

    ##### use model to label all the unknown tweets #####
    data_dir = '/Users/tl8313/Documents/study_robinwilliams/extracted/'
    # INPUT
    oneyeardata = open(data_dir + 'oneyear_sample.json', 'r')
    # OUTPUT
    suicidal_json = open(data_dir + 'suicidal_C1.json', 'w')
    others_json = open(data_dir + 'others_C1.json', 'w')

    model_dir = '/Users/tl8313/Documents/study_robinwilliams/'
    vectorizer = joblib.load(model_dir + 'vectorizer.pkl')
    clf = joblib.load(model_dir + 'roc_auc_SVC.pkl')

    visited = set()

    for line in oneyeardata:
        tweet = json.loads(line.decode('utf-8'))

        userid = tweet['user']['id_str']
        msg_id = tweet['id']
        message = tweet['text']

        test_X = vectorizer.transform([message])
        y_pred_class = clf.predict(test_X)[0]
        y_value = clf.decision_function(test_X)[0]

        if (msg_id not in visited) and (msg_id not in trained_dict):
            visited.add(msg_id)

            if y_pred_class == 1.0:
                basic = {}
                basic['msg_id'] = msg_id
                basic['message'] = message
                basic['userid'] = userid
                basic['pred_suicidal_label'] = 1
                basic['pred_suicidal_conf'] = y_value
                json.dump(basic, suicidal_json)
                suicidal_json.write("\n")
            elif y_pred_class == -1.0:
                basic = {}
                basic['msg_id'] = msg_id
                basic['message'] = message
                basic['userid'] = userid
                basic['pred_suicidal_label'] = -1
                basic['pred_suicidal_conf'] = y_value
                json.dump(basic, others_json)
                others_json.write("\n")

    ##### mark the ending time of process #####
    end = timeit.default_timer()
    seconds = math.ceil(end - start)
    # Convert Secs Into Human Readable Time String (HH:MM:SS)
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    print "This process took %d:%02d:%02d" % (h, m, s)

if __name__ == '__main__':
    main()