import ujson as json
import timeit, math, subprocess, codecs, os, psutil, tempfile, re

def prepare_work_txt_file(json_data, txt_file):

    text_output = open(txt_file, "w")

    for line in open(json_data, "r"):
        tweet = json.loads(line.decode('utf-8'))

        if 'lang' in tweet:                
            language = tweet['lang']

            # Only process and analyze tweets written in English
            if language == 'en':

                message = tweet['text']
                # msg_id = tweet['id']

                # user = tweet['user']
                # user_id = user['id_str']

                # # ArkTweetNLP tokenizer
                # tokens = tokenizeRawTweetText(message)

                new_message = parse_raw_message_emoji(message)

                text_output.write(new_message + "\n")

def parse_raw_message_emoji(message):

    utf8_message = message.encode("utf-8")
    escaped_message = message.encode('unicode_escape')

    emoji = re.search(r'\\U', escaped_message)

    if emoji is not None:
        emoji_parts = escaped_message.split("\\")

        for index, string in enumerate(emoji_parts):
            string = string.rstrip()

            if string.startswith("U"):
                emoji = "\\" + string[:9]
                emoji_unicode = unicode(emoji)

                if len(string) > 9:
                    text = string[9:]

                    if text.startswith(" "):
                        new_string = emoji_unicode + text
                    else:
                        new_string = emoji_unicode + " " + text
                    emoji_parts[index] = new_string

                else:
                    emoji_parts[index] = emoji_unicode

            elif string.startswith("u"):
                emoji = "\\" + string[:5]
                emoji_unicode = unicode(emoji)

                if len(string) > 5:
                    text = string[5:]

                    if text.startswith(" "):
                        new_string = emoji_unicode + text
                    else:
                        new_string = emoji_unicode + " " + text
                    emoji_parts[index] = new_string

                else:
                    emoji_parts[index] = emoji_unicode

        new_message = ' '.join(e.encode("utf-8").rstrip() for e in emoji_parts).lstrip()           
    else:
        new_message = escaped_message

    return new_message

def run_POS_tagger_java(txt_name, tagged_output):

    print "starting POStagging ......"
    os.chdir("/Users/tl8313/Documents/study_robinwilliams/ark-tweet-nlp-0.3.2")

    print "current work in:"
    subprocess.call(["pwd"])

    command = './runTagger.sh --output-format pretsv --model model.ritter_ptb_alldata_fixed.20130723.txt ' + txt_name
    commands = command.split()

    p = subprocess.Popen(commands, stdout=subprocess.PIPE)

    output = codecs.open(tagged_output, 'w', 'utf-8')
    while p.poll() is None:
        l = p.stdout.readline()
        output.write(l.decode('utf-8'))
        output.flush()
    output.close()

    os.chdir("/Users/tl8313/Documents/study_robinwilliams/")
    print "change the directory back to:"
    subprocess.call(["pwd"])

def create_txt_name_from_json(json_data):

    prefix = json_data.split(".")[0]
    txt_name = prefix + ".txt"
    tagged_output = prefix + "_POStagged.txt"

    return txt_name,  tagged_output

def main():
    # mark the beginning time of process
    start = timeit.default_timer()

    directory = '/Users/tl8313/Documents/study_robinwilliams/'

    fileName = directory + 'oneyear_sample.json'

    txt_name, tagged_output = create_txt_name_from_json(fileName)

    # prepare_work_txt_file(fileName, txt_name)

    # use specific model ---- Penn Treebank-style POS tags for Twitter
    run_POS_tagger_java(txt_name, tagged_output)

    ##### mark the ending time of process #####
    end = timeit.default_timer()
    seconds = math.ceil(end - start)
    # Convert Secs Into Human Readable Time String (HH:MM:SS)
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    print "This process took %d:%02d:%02d" % (h, m, s)

if __name__ == '__main__':
    main()