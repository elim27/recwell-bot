import logging
import pytz
import time
import tweepy
from datetime import datetime
from decouple import config
from enum import Enum
########## from /src ##########
from handlers.update_handler import handleUpdates, handleDailyUpdates
from handlers.profile_handler import handleProfile
from handlers.mentions_handler import handleMentions
from webscrapers.recwell_scrape import checkOccupancy

# Setup logging
logging.basicConfig(filename='/var/log/scrapes.log', 
                    filemode='a',  
                    datefmt='%H:%M:%S',
                    level=logging.INFO
)

########## AUTHENTICATION ##########
auth = tweepy.OAuthHandler(config('consumer_key', default='cricket_sunday'), config('consumer_secret', default='yello_cactus'))
auth.set_access_token(config('access_token', default='blonde_penguin'), config('access_token_secret', default='happy_harpy'))

api = tweepy.API(auth)
########## END OF AUTHENTICATION ##########

########## HOURS OF OPERATIONS ENUMS ##########
# Enumerators containing the respective opening hours
# in 24 hour time (no leading 0) Used Enums for
# readability
# Spring 2021 schedule
class Opening(Enum):
    Monday = 6
    Tuesday = 6
    Wednesday = 6
    Thursday = 6
    Friday = 6
    Saturday = 8
    Sunday = 8

# Enumerators containing the respective closing hours
# in 24 hour time (no leading 0). Used Enums for
# readability
# Spring 2021 schedule
class Closing(Enum):    
    Monday = 22
    Tuesday = 22
    Wednesday = 22
    Thursday = 22
    Friday = 20
    Saturday = 20
    Sunday = 22
########## END OF HOURS OF OPERATIONS ENUMS ##########

################### GLOBAL VARS ####################
# IS_OPEN: True if operating during Open Hours, False otherwise
# REST: Duration of sleep (15s)
# UPDATED_OPEN: True if profile has been updated to open
#               default is True to prevent unwanted updates
#               when redeploying/restarting container
# UPDATED_CLOSE: True if profile has been updated to close
#               default is True to prevent unwanted updates
#               when redploying/restarting container
IS_OPEN = False
REST = 15
UPDATED_OPEN = False
UPDATED_CLOSE = True
FIRST_START = True
FILE_NAME = config('FILE_PATH_CONTEXT')
# TWEET_LIMITER: Limits the Tweet rate to 1 Tweet / 10 minutes
#               If under threshold
# NAPTIME: Counter that increases by 1 every 15s (NAPTIME = 4 
#               means 1 min). Reset to 0 everytime there is a status update
#               Initially = to TWEET_LIMITER so initial tweet is pushed
TWEET_LIMITER =  4 * 25
NAPTIME = 4 * 25 - 10

# OPENING_HOURS: List of Enum values that correspond to opening hours
# CLOSING_HOURS: List of Enum values that correspond to closing hours
OPENING_HOURS = [
                Opening.Monday.value, 
                Opening.Tuesday.value,
                Opening.Wednesday.value,  
                Opening.Thursday.value,
                Opening.Friday.value,
                Opening.Saturday.value,
                Opening.Sunday.value
                ]    
CLOSING_HOURS = [
                Closing.Monday.value, 
                Closing.Tuesday.value,
                Closing.Wednesday.value, 
                Closing.Thursday.value,
                Closing.Friday.value,
                Closing.Saturday.value,
                Closing.Sunday.value
                ]
################### END OF GLOBAL VARS ####################

# Function that reads from context.txt file to retrieve the last
# context the bot was running in (used in the cases of container restarts)
# PARAMS:
# file_name: path to file where context.txt is stored
def getLastContext(file_name):
    global IS_OPEN, UPDATED_CLOSE, UPDATED_OPEN
    try:
        fr = open(file_name, 'r')
        modes = str(fr.read().strip()).split('\n')
        if 'True' in modes[0]:
            IS_OPEN = True
        else:
            IS_OPEN = False
        if 'True' in modes[1]:
            UPDATED_OPEN = True
        else:
            UPDATED_OPEN = False
        if 'True' in modes[2]:
            UPDATED_CLOSE = True
        else:
            UPDATED_CLOSE = False
        fr.close()
    except FileNotFoundError:
        logging.info('FileNotFoundError context get')
    except Exception as e:
        logging.info(e)
   
# Funciton that writes to context.txt file to save the last
# context this but was running in.
# file_name: path to file where context.txt is stored
# context: the context to save
def saveLastContext(file_name, context):
    try:
        fw = open(file_name, 'w')
        fw.write(str(context))
        fw.close()
    except FileNotFoundError:
        logging.info('FileNotFoundError context save')
    except Exception as e:
        logging.info(e)
    
# Function that gets the current 24 hour and returns it as an integer
# i.e. 6 AM = 6, 12 PM = 12, 5 PM = 17, 12 AM = 00
# RETURN: Current hour as integer
def getCurrHour():
    CST = pytz.timezone('US/Central')
    curr_hour = datetime.today().astimezone(CST).strftime('%H:%M %p').lstrip('0').split(':')[0]
    # Edge case of checking time at 12 AM where both 0s will be stripped
    # leading to an empty string
    if not curr_hour:
        curr_hour = 0
    # print('current 24 hour: ' + str(curr_hour))
    return int(curr_hour)

# Function that get the current weekday in integer form
# i.e. Monday = 0, Tuesday = 1, ... Sunday = 6
# RETURN: Current weekday as integer
def getCurrDay():
    CST = pytz.timezone('US/Central')
    curr_day = datetime.today().astimezone(CST).weekday() 
    return int(curr_day)

# Function that setups globals for open hours and updates the
# profile and pushes a status to convey The Nick is open 
# (only tweets/updates profile once)
def openSetup():
    global IS_OPEN, UPDATED_OPEN, UPDATED_CLOSE
    IS_OPEN = True
    if not UPDATED_OPEN:
        # Tweet an Open status and
        # change profile to Open
        handleDailyUpdates(api, IS_OPEN)
        handleProfile(api, IS_OPEN)
        UPDATED_OPEN = True
        UPDATED_CLOSE = False # reset for close update later
         # save context in case of container restart
        context_save = str(IS_OPEN) + '\n' + str(UPDATED_OPEN) + '\n' + str(UPDATED_CLOSE)
        saveLastContext(FILE_NAME, context_save)

# Function that setups globals for close hours and updates the
# profile and pushes a status to convey The Nick is closed 
# (only tweets/updates profile once)
def closedSetup():
    global IS_OPEN, UPDATED_OPEN, UPDATED_CLOSE, NAPTIME
    IS_OPEN = False
    if not UPDATED_CLOSE:
        handleDailyUpdates(api, IS_OPEN)
        handleProfile(api, IS_OPEN)
        # reset to push a tweet in the morning ~ 5-6min after opening
        NAPTIME = TWEET_LIMITER -  25
        UPDATED_CLOSE = True
        UPDATED_OPEN = False # reset for open update later
        # save context in case of container restart
        context_save = str(IS_OPEN) + '\n' + str(UPDATED_OPEN) + '\n' + str(UPDATED_CLOSE)
        saveLastContext(FILE_NAME, context_save)

# ########## CONTROL LOOP ##########
# # This loop will control when the bot updates statuses, creates favorites, etc.
# # BY calling the appropriate functions at the appropriate rate. 
# # Checks mentions every 15s, Tweets new status every 10 min 
# #               (unless capacity is >= 95)
# #       Endpoint       | Rate limit window | Rate limit per user
# # POST statuses/update |       3 hours     |        300
# # POST favorites/create|       3 hours     |        1000
# # 900 requests / 15 Minutes
# # More rate limits: https://developer.twitter.com/en/docs/twitter-api/v1/rate-limits
while True:
    try:
        # If Container restart, setup from last running context
        if FIRST_START:
            getLastContext(FILE_NAME)
            FIRST_START = False
            logging.info('Init setup successful!')
            logging.info('IS_OPEN: ' + str(IS_OPEN) + ' U_OPEN: ' + str(UPDATED_OPEN) + 'U_CLOSE: ' + str(UPDATED_CLOSE))

        curr_hour = getCurrHour()
        curr_day = getCurrDay()
       
       # Setup is called at open/close hours:
        if curr_hour == OPENING_HOURS[curr_day]:
            openSetup()
        elif curr_hour == CLOSING_HOURS[curr_day]:
            closedSetup()
        
        # Checks if the current hour is within open hours for the
        # current day. Pushes an update ~25 minutes 
        if OPENING_HOURS[curr_day] <= curr_hour < CLOSING_HOURS[curr_day]:
            NAPTIME += 1   
            # if it has been more than 25 minutes since last Tweet -> Push Tweet
            if NAPTIME >= TWEET_LIMITER:
                NAPTIME = 0
                handleUpdates(api)

        handleMentions(api, IS_OPEN)
        time.sleep(REST)
    except tweepy.RateLimitError:
        logging.info('Rate Limit Exceeded')
        logging.info('Extended sleep...')
        time.sleep(REST * 60)

# Function deletes all Tweets
# Uses to easily clear timeline.
# Called manually.
def deleteAllTweets():
    tweets = api.user_timeline(screen_name=config('SCREEN_NAME'), count=1000)
    for index in range(len(tweets)):
        api.destroy_status(tweets[index].id)


