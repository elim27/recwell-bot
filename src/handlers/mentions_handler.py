import logging
import tweepy
from webscrapers.recwell_scrape import checkOccupancy
from decouple import config

FILE_NAME = config('FILE_PATH_ID', cast=str)
SCREEN_NAME = config('SCREEN_NAME')
BANNED_WORDS = []
SEEN_IDS = []

# Setup logging
logging.basicConfig(filename='/var/log/handlers.log', 
                    filemode='a', 
                    datefmt='%H:%M:%S',
                    level=logging.INFO
)

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
        logging.error('FileNotFoundError :(')

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
        logging.info(FILE_NAME + ' not found :(')
    except:
        logging.info('error in storeLastID')
    
# Function handles response if user mentions but with '#full'
# If the occupancy is at 100%, the bot responds 'Yes.', if an
# error occurs in scraping (curr_occupancy = -1), 
#  otherwise it responds 'Nope!' with the current occupancy
# PARAMS:
# api: api object that gives access to Twitter's REST API methods
# tweet: Status object that needs to be responded to
# curr_occupancy: current occupancy of The Nick as an integer
def fullHandler(api, tweet):
    logging.info('fullHandler() called')
    try:
        curr_occupancy = checkOccupancy()['occupancy_num']
        backup_data = checkOccupancy()['BACKUP_DATA']
        curr_percent = 'Current Occupancy: ' + str(curr_occupancy) + '%'     
        # Attach notice if curr_occupancy is from backup data
        if backup_data:
            curr_percent += ('\nNOTE: Recwell Services down, using backup '
                            + 'data... Results are an estimation!')
        # At capacity scenario
        if curr_occupancy == 100:
            api.update_status('@' + tweet.user.screen_name + ' Yes. \U0001F614\n'
                            + curr_percent, in_reply_to_status_id=tweet.id)
        # Error scenario                   
        elif curr_occupancy == -1:
            api.update_status('@' + tweet.user.screen_name + ' Uh oh, it '
                            + 'seems like my source is currently down '
                            + '\U0001F62C \U0001F6E0\n ',
                            in_reply_to_status_id=tweet.id)
        elif curr_occupancy == 69:
            api.update_status('@' + tweet.user.screen_name + ' Nope! \U0001F60E\n'
                            + curr_percent, in_reply_to_status_id=tweet.id)
        # Normal scenario
        elif curr_occupancy != 100:
            api.update_status('@' + tweet.user.screen_name + ' Nope! \U0001F601\n'
                            + curr_percent, in_reply_to_status_id=tweet.id)
        logging.info('Response to #full successful! ' + str(curr_occupancy))
    except Exception as e:
        logging.error('Response to #full failed!')
        logging.error(e)

# This function takes care of favoriting tweets
# that compliment the bot with the phrase 'good bot'
# api: api object that gives access to Twitter's REST API methods
# tweet: Status object that needs to be responded to
def favHandler(api, tweet):
    try:
        api.create_favorite(tweet.id)
        logging.info('favorite successful')
    except Exception as e:
        logging.info('favorite failed!')
        logging.info(e)

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
        logging.info('Closed Response to #full successful!')
    except Exception as e:
        logging.info('Closed Response to #full failed!')
        logging.info(e)

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
def handleMentions(api, open):
    try:
        setupBannedWords()
        last_id = getLastID(FILE_NAME)
        # Retrieve mentions  
        logging.info('Getting mentions..')
        mentions = api.mentions_timeline(last_id, tweet_mode='extended')
        # Responds to tweets from oldest to newest
        for tweet in reversed(mentions):
            logging.info(str(tweet.id))
            
            last_id = tweet.id # ID of last tweet seen
            storeLastID(FILE_NAME, last_id)
           
            # convert the mention text to lower case
            tweet_text = tweet.full_text.lower()

            # Make sure the bot doesn't respond to its own tweets
            # Ensure the bot doesn't respond to words that are in BANNED_WORDS
            # Make sure The Nick is open and not closed
            if (SCREEN_NAME not in tweet.user.screen_name and
                            any(word not in tweet_text for word in BANNED_WORDS)):
                if open:
                    if '#full' in tweet_text:
                        fullHandler(api, tweet)
                    if 'good bot' in tweet_text:
                        favHandler(api, tweet)
                else:
                    closedHandler(api, tweet)
            else:
                logging.info('Tweet ignored')
    except tweepy.TweepError as e:
        logging.error('TweepyError in Mentions')
        logging.error(e.reason)
    except Exception as e:
            logging.info('Error, unable to get mentions')
            logging.info(e)

