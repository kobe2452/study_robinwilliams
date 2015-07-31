import os, timeit, math
import ujson as json
from collections import defaultdict


def exportDataSift(file_path):
    print "Now processing DataSift file: " + file_path
    
    jsonfile = open(file_path, "r")
    
    line = jsonfile.readline()
    
    metadata = json.loads(line)
    
    interactions = metadata['interactions']

    tweet_list = []
        
    for each in interactions:

        twitter = each['twitter']

        # if 'twitter' in each:
        #     # content = each['demographic']
        #     keys = each['twitter'].keys()
        #     print keys
 
        tweet_list.append(twitter)
           
    return tweet_list


def saveObjectToFile(fileName, data):
    with open(fileName, 'a') as outfile:
        outfile.write("{}\n".format(json.dumps(data)))
        
    
def main():

    # mark the beginning time of process
    start = timeit.default_timer()

    # target folder which stores every 4-week data
    # replace 01 with [01--24], orders and details please see EXCEL table
    path = 'RW_data/'

    print 'Now processing DataSift files in: ' + path
              
    file_counter = 0
    tweet_counter = 0

    # define a destination to save Twitter data
    fileName = 'two_months_sample.json'
            
    for eachfile in os.listdir(path):
        if not eachfile.startswith('.'):
               
            file_counter += 1
                   
            sub_path = path + eachfile
                    
            if 'json.part' in sub_path:
                continue                        
                  
            records = exportDataSift(sub_path)
            
            for tweet in records:
                tweet_counter += 1

                saveObjectToFile(fileName, tweet)
     
    print 'How many files in the folder: ' + str(file_counter)
    print 'How many tweets in total: ' + str(tweet_counter)
    print 'Data are saved in: ' + fileName

    ##### mark the ending time of process #####
    end = timeit.default_timer()
    seconds = math.ceil(end - start)
    # Convert Secs Into Human Readable Time String (HH:MM:SS)
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    print "This process took %d:%02d:%02d" % (h, m, s)


if __name__ == '__main__':
    main()