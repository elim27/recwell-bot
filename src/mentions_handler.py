import tweepy
from decouple import config


FILE_NAME = config('FILE_NAME')
SCREEN_NAME = config('SCREEN_NAME')
BANNED_WORDS = []
# Function that reads from last_id.txt file to retrieve the ID 
# of the last tweet that mentioned the bot
def getLastID(file_name):
    last_id = 0
    try:
        fr = open(file_name, 'r')
        last_id = int(fr.read().strip())           
        fr.close()
    except ValueError:
        last_id = 0
    except FileNotFoundError:
        print('FileNotFoundError :(')

    return last_id

# Funciton that writes to last_id.txt file to save the ID
# of the last tweet that mentioned the bot
def storeLastID(file_name, last_id):
    try:
        fw = open(file_name, 'w')
        fw.write(str(last_id))
        fw.close()
    except FileNotFoundError:
        print(FILE_NAME + ' not found :(')
    

def setupBannedWords():
    word_list = config('BANNED_WORDS', cast=str).split(',')
    for word in word_list:
        BANNED_WORDS.append(word)

def capHandler(api, tweet, curr_occupancy):
    try:
        curr_percent = 'Current Occupancy: ' + str(curr_occupancy) + '%'

        if curr_occupancy == 100:
            api.update_status('@' + tweet.user.screen_name + 'Yes. \U0001F61E\n'
                            + curr_percent, in_reply_to_status_id=tweet.id)
        else:
            api.update_status('@' + tweet.user.screen_name + 'Nope! \U0001F601\n'
                            + curr_percent, in_reply_to_status_id=tweet.id)
        print('Response to #cap successful!')
    except tweepy.TweepError as e:
        print('Response to #cap failed!')
        print(e.reason)

def handleMentions(api, curr_occupancy):
    print('handleMentions() called')
    setupBannedWords()
    last_id = getLastID(FILE_NAME)
    mentions = api.mentions_timeline(last_id, tweet_mode='extended')

    for tweet in reversed(mentions):
        print('Reading tweets...')
        print(str(tweet.id))
        last_id = tweet.id # ID of last tweet seen
        storeLastID(FILE_NAME, last_id)
        tweet_text = tweet.full_text.lower()

        # Make sure the bot doesn't respond to its own tweets
        #Ensure the bot doesn't respond to words that are in BANNED_WORDS
        if SCREEN_NAME not in tweet.user.screen_name and 
                        any(word not in tweet_text for word in BANNED_WORDS):
                if '#cap' in tweet_text:
                    capHandler(api, tweet, curr_occupancy)
        else:
            print('Tweet ignored.')
                