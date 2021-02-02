
import pytz
import time
import tweepy
from datetime import datetime
from decouple import config
from enum import Enum
########## from /src ##########
from update_handler import handleUpdates, handleDailyUpdates
from profile_handler import handleProfile
from mentions_handler import handleMentions
from recwell_scrape import checkOccupancy

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
    Saturday = 18
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
IS_OPEN = True
REST = 15
UPDATED_OPEN = True
UPDATED_CLOSE = False


# TWEET_LIMITER: Limits the Tweet rate to 1 Tweet / 10 minutes
#               If under threshold
# NAPTIME: Counter that increases by 1 every 15s (NAPTIME = 4 
#               means 1 min). Reset to 0 everytime there is a status update
#               Initially = to TWEET_LIMITER so initial tweet is pushed
TWEET_LIMITER =  4 * 25
NAPTIME = 4 * 25

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
    curr_day = datetime.today().weekday() 
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

# Function that setups globals for close hours and updates the
# profile and pushes a status to convey The Nick is closed 
# (only tweets/updates profile once)
def closedSetup():
    global IS_OPEN, UPDATED_OPEN, UPDATED_CLOSE
    IS_OPEN = False
    if not UPDATED_CLOSE:
        handleDailyUpdates(api, IS_OPEN)
        handleProfile(api, IS_OPEN)
        UPDATED_CLOSE = True
        UPDATED_OPEN = False # reset for open update later

########## CONTROL LOOP ##########
# This loop will control when the bot updates statuses, creates favorites, etc.
# BY calling the appropriate functions at the appropriate rate. 
# Checks mentions every 15s, Tweets new status every 10 min 
#               (unless capacity is >= 95)
#       Endpoint       | Rate limit window | Rate limit per user
# POST statuses/update |       3 hours     |        300
# POST favorites/create|       3 hours     |        1000
# 900 requests / 15 Minutes
# More rate limits: https://developer.twitter.com/en/docs/twitter-api/v1/rate-limits
while True:
    try:
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
        print('Rate Limit Exceeded')
        print('Extended sleep...')
        time.sleep(REST * 60)


