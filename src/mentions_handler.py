import tweepy
from decouple import config

FILE_NAME = config('FILE_NAME', cast=str)
SCREEN_NAME = config('SCREEN_NAME')
BANNED_WORDS = []
SEEN_IDS = []

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
    
# Function initializes BANNED_WORDS dictionary from words defined
# in .env
def setupBannedWords():
    word_list = config('BANNED_WORDS', cast=str).split(',')
    for word in word_list:
        BANNED_WORDS.append(word)

# Function handles response if user mentions but with '#full'
# If the occupancy is at 100%, the bot responds 'Yes.', if an
# error occurs in scraping (curr_occupancy = -1), 
#  otherwise it responds 'Nope!' with the current occupancy
def fullHandler(api, tweet, curr_occupancy):
    try:
        curr_percent = 'Current Occupancy: ' + str(curr_occupancy) + '%'

        if curr_occupancy == 100:
            api.update_status('@' + tweet.user.screen_name + 'Yes. \U0001F61E\n'
                            + curr_percent, in_reply_to_status_id=tweet.id)
        elif curr_occupancy == -1:
            api.update_status('@' + tweet.user.screen_name + 'Uh oh, it '
                            + 'seems like I can\'t get that info right now. '
                            + 'My source is probably down.\n'
                            + 'Try this alternate link!', 
                            attachment_url='https://recwell.wisc.edu/liveusage/',
                            in_reply_to_status_id=tweet.id)
        else:
            api.update_status('@' + tweet.user.screen_name + 'Nope! \U0001F601\n'
                            + curr_percent, in_reply_to_status_id=tweet.id)
        print('Response to #full successful!')
    except tweepy.TweepError as e:
        print('Response to #full failed!')
        print(e.reason)

# This function takes care of favoriting tweets
# that compliment the bot with the phrase 'good bot'
def favHandler(api, tweet):
    try:
        api.create_favorte(tweet.id)
        print('favorite successful')
    except:
        print('favorite failed!')

# Function that handles responding to tweets that mention the bot and 
# use a specific hashtag or phrase. Saves Tweet ID into a text file (last_id.txt) 
# so it won't handle tweets it has already interacted with (won't violate
# Twitter's spam policy either)
# Possible #'s:
# - #full: responds yes or no to whether The Nick is full or not and provides current
#               occupancy
# - 'good bot': likes the tweet
def handleMentions(api, curr_occupancy):
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
        if (SCREEN_NAME not in tweet.user.screen_name and 
                        any(word not in tweet_text for word in BANNED_WORDS)):
                if '#full' in tweet_text:
                    fullHandler(api, tweet, curr_occupancy)
                if 'good bot' in tweet_text:
                    favHandler(api, tweet)
        else:
            print('Tweet ignored.')
                