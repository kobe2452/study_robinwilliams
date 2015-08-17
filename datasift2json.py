import os, timeit, math
import ujson as json
from collections import defaultdict

def export_DataSift_file(file_path):

    print "Now processing DataSift file: " + file_path
    
    jsonfile = open(file_path, "r")
    
    line = jsonfile.readline()
    
    metadata = json.loads(line)
    
    interactions = metadata['interactions']

    tweet_list = []
        
    for each in interactions:
        twitter = each['twitter']
        tweet_list.append(twitter)
           
    return tweet_list

def saveObjectToOutput(fileName, data):

    with open(fileName, 'a') as outfile:
        outfile.write("{}\n".format(json.dumps(data)))

def extractTweetfromMix(path, fileName):

    file_counter = 0
    tweet_counter = 0

    for eachfile in os.listdir(path):
        if not eachfile.startswith('.'):               
            file_counter += 1                   
            sub_path = path + eachfile                    
            if 'json.part' in sub_path:
                continue                                          
            records = export_DataSift_file(sub_path)
            
            for tweet in records:
                tweet_counter += 1

                saveObjectToOutput(fileName, tweet)

    print 'How many files in the folder: ' + str(file_counter)
    print 'How many tweets in total: ' + str(tweet_counter)

def extractTweetfromMonth(path, fileName):

    file_counter = 0
    tweet_counter = 0

    for root, dirs, files in os.walk(path):
        for eachfile in files:
            if not eachfile.startswith("."):
                file_counter += 1
                sub_path = os.path.join(root, eachfile)
                if "json.part" in sub_path:
                    continue
                records = export_DataSift_file(sub_path)

                for tweet in records:
                    tweet_counter += 1

                    saveObjectToOutput(fileName, tweet)
            
    print 'How many files in the folder: ' + str(file_counter)
    print 'How many tweets in total: ' + str(tweet_counter)

def main():

    # mark the beginning time of process
    start = timeit.default_timer()

    # path = 'RW_data_mix/'
    path = 'RW_data_month/'
    print 'Now processing DataSift files in: ' + path
              
    # define a destination to save exported Twitter data
    fileName = 'oneyear_sample.json'
            
    extractTweetfromMonth(path, fileName)
    print 'Done. All the data have been saved in: ' + fileName

    ##### mark the ending time of process #####
    end = timeit.default_timer()
    seconds = math.ceil(end - start)
    # Convert Secs Into Human Readable Time String (HH:MM:SS)
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    print "This process took %d:%02d:%02d" % (h, m, s)

if __name__ == '__main__':
    main()