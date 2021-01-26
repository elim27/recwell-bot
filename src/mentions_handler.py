import tweepy
from decouple import config

FILE_NAME = config('FILE_NAME', cast=str)
SCREEN_NAME = config('SCREEN_NAME')
BANNED_WORDS = []
SEEN_IDS = []

# Function initializes BANNED_WORDS dictionary from words defined
# in .env
def setupBannedWords():
    word_list = config('BANNED_WORDS', cast=str).split(',')
    for word in word_list:
        BANNED_WORDS.append(word)

# Function that reads from last_id.txt file to retrieve the ID 
# of the last tweet that mentioned the bot
# PARAMS:
# file_name: path to file where last seen mention ID is stored
# RETURN: last seen ID
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
# file_name: path to file where last seen mention ID is stored
# last_id: the last seen ID to be stored into text file
def storeLastID(file_name, last_id):
    try:
        fw = open(file_name, 'w')
        fw.write(str(last_id))
        fw.close()
    except FileNotFoundError:
        print(FILE_NAME + ' not found :(')
    
# Function handles response if user mentions but with '#full'
# If the occupancy is at 100%, the bot responds 'Yes.', if an
# error occurs in scraping (curr_occupancy = -1), 
#  otherwise it responds 'Nope!' with the current occupancy
# PARAMS:
# api: api object that gives access to Twitter's REST API methods
# tweet: Status object that needs to be responded to
# curr_occupancy: current occupancy of The Nick as an integer
def fullHandler(api, tweet, curr_occupancy):
    print('fullHandler() called')
    try:
        curr_percent = 'Current Occupancy: ' + str(curr_occupancy) + '%'

        if curr_occupancy == 100:
            api.update_status('@' + tweet.user.screen_name + ' Yes. \U0001F614\n'
                            + curr_percent, in_reply_to_status_id=tweet.id)
        elif curr_occupancy == -1:
            api.update_status('@' + tweet.user.screen_name + ' Uh oh, it '
                            + 'seems like my source is currently down '
                            + '\U0001F62C \U0001F6E0\n Try this alternate link!', 
                            attachment_url='https://recwell.wisc.edu/liveusage/',
                            in_reply_to_status_id=tweet.id)
        else:
            api.update_status('@' + tweet.user.screen_name + ' Nope! \U0001F601\n'
                            + curr_percent, in_reply_to_status_id=tweet.id)
        print('Response to #full successful!')
    except tweepy.TweepError as e:
        print('Response to #full failed!')
        print(e.reason)

# This function takes care of favoriting tweets
# that compliment the bot with the phrase 'good bot'
# api: api object that gives access to Twitter's REST API methods
# tweet: Status object that needs to be responded to
def favHandler(api, tweet):
    try:
        api.create_favorte(tweet.id)
        print('favorite successful')
    except tweepy.TweepError:
        print('favorite failed!')

# Function that handles responding to tweets that mention the bot
# but it is outside of open hours (meaning it doesn't make sense to
# provide capacity information during these times)
# PARAMS:
# api: api object that gives access to Twitter's REST API methods
# tweet: Status object that needs to be responded to
def closedHandler(api, tweet):
    try:
        api.update_status('@' + tweet.user.screen_name + ' The Nick is currently '
                        + 'closed \U0001F634 \U0001F319', 
                        in_reply_to_status_id=tweet.id)
        print('Closed Response to #full successful!')
    except tweepy.TweepError as e:
        print('Closed Response to #full failed!')
        print(e.reason)

# Function that handles responding to tweets that mention the bot and 
# use a specific hashtag or phrase. Saves Tweet ID into a text file (last_id.txt) 
# so it won't handle tweets it has already interacted with (won't violate
# Twitter's spam policy either)
# Possible #'s:
# - #full: responds yes or no to whether The Nick is full or not and provides current
#               occupancy
# - 'good bot': likes the tweet
# PARAMS:
# api: api object that gives access to Twitter's REST API methods
# curr_occupancy: current occupancy of The Nick as an integer
# IS_OPEN: True when The Nick is open, False otherwise
def handleMentions(api, curr_occupancy, open):
    print('handleMentions() called')
    setupBannedWords()
    last_id = getLastID(FILE_NAME)
    try:
        mentions = api.mentions_timeline(last_id, tweet_mode='extended')
    except tweepy.TweepError:
        print('Error, unable to get mentions')
        return

    # Responds to tweets from oldest to newest
    for tweet in reversed(mentions):
        print('Reading tweets...')
        print(str(tweet.id))
        last_id = tweet.id # ID of last tweet seen
        storeLastID(FILE_NAME, last_id)
        tweet_text = tweet.full_text.lower()

        # Make sure the bot doesn't respond to its own tweets
        # Ensure the bot doesn't respond to words that are in BANNED_WORDS
        # Make sure The Nick is open and not closed
        if (SCREEN_NAME not in tweet.user.screen_name and
                        any(word not in tweet_text for word in BANNED_WORDS)):
            if open:
                if '#full' in tweet_text:
                    fullHandler(api, tweet, curr_occupancy)
                if 'good bot' in tweet_text:
                    favHandler(api, tweet)
            else:
                closedHandler(api, tweet)
        else:
            print('Tweet ignored')

