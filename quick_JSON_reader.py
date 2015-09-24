import json, sys

def main():

    fileName = sys.argv[1]

    for line in open(fileName, "r"):
        tweet = json.loads(line.decode('utf-8'))

        print tweet

if __name__ == '__main__':
    main()