from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
import json,HTMLParser,re
from unicodedata import normalize

ckey=""
csecret=""
atoken=""
asecret=""

class listener(StreamListener):
    def __init__(self, api=None):
        super(listener, self).__init__()
        self.num_tweets = 0
    
    def on_data(self, data):
        #print data
        data=data.replace('&amp;','&')
        data=str(data)
        data=data.replace('\n','')
        all_data=json.loads(data)
        lang=all_data["lang"]
        if lang=='en':
            tweet=all_data['text']
            if tweet[0:4]=='RT @' and "via" not in tweet:
                if 'quoted_status' in all_data:
                    tweet=all_data['quoted_status']['text']+' $$q'
                else:
                    tweet=all_data['retweeted_status']['text']+' $$r'
            tweet=''.join([i if ord(i) < 128 else '' for i in tweet])
            tweet=tweet.replace('\n','')
            #print tweet
            user=all_data['user']['screen_name']
            #print user,"->",tweet,'\n'
            f1.write(user+"->"+tweet+'\n')
            self.num_tweets += 1
            if self.num_tweets < 20:
                return True
            else:
                f1.close()
                return False

    def on_error(self, status):
        print status

auth = OAuthHandler(ckey, csecret)
auth.set_access_token(atoken, asecret)

f1=open('tweet.txt','w')
twitterStream = Stream(auth, listener())
twitterStream.filter(track=["trump"])

#PREPROCESSING
def processTweet(tweet):
    # process the tweets
    #Convert to lower case
    tweet = tweet.lower()
    #Convert www.* or https?://* to URL
    tweet = re.sub('((www\.[^\s]+)|(https?://[^\s]+))','URL',tweet)
    #Convert @username to AT_USER
    tweet = re.sub('@[^\s]+','AT_USER',tweet)
    #Remove additional white spaces
    tweet = re.sub('[\s]+', ' ', tweet)
    #Replace #word with word
    tweet = re.sub(r'#([^\s]+)', r'\1', tweet)
    #trim
    tweet = tweet.strip('\'"')
    return tweet

fp = open('tweet.txt', 'r')
line = fp.readline()

while line:
    processedTweet = processTweet(line)
    print processedTweet
    line = fp.readline()
fp.close()

#PROCESSING
stopWords = []

#start replaceTwoOrMore
def replaceTwoOrMore(s):
    #look for 2 or more repetitions of character and replace with the character itself
    pattern = re.compile(r"(.)\1{1,}", re.DOTALL)
    return pattern.sub(r"\1\1", s)
#end

#start getStopWordList
def getStopWordList(stopWordListFileName):
    #read the stopwords file and build a list
    stopWords = []
    stopWords.append('AT_USER')
    stopWords.append('URL')

    fp = open(stopWordListFileName, 'r')
    line = fp.readline()
    while line:
        word = line.strip()
        stopWords.append(word)
        line = fp.readline()
    fp.close()
    return stopWords
#end

#start getfeatureVector
def getFeatureVector(tweet):
    featureVector = []
    #split tweet into words
    words = tweet.split()
    for w in words:
        #replace two or more with two occurrences
        w = replaceTwoOrMore(w)
        #strip punctuation
        w = w.strip('\'"?,.')
        #check if the word stats with an alphabet
        val = re.search(r"^[a-zA-Z][a-zA-Z0-9]*$", w)
        #ignore if it is a stop word
        if(w in stopWords or val is None):
            continue
        else:
            featureVector.append(w.lower())
    return featureVector
#end

#Read the tweets one by one and process it
fp = open('tweet.txt', 'r')
line = fp.readline()

st = open('stopwords.txt', 'r')
stopWords = getStopWordList('stopwords.txt')

while line:
    processedTweet = processTweet(line)
    featureVector = getFeatureVector(processedTweet)
    print featureVector
    line = fp.readline()
#end loop
fp.close()
