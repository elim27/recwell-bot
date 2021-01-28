import tweepy
import time
import pytz
from enum import Enum
from datetime import datetime
from decouple import config
from update_handler import handleUpdates, handleClosedUpdate, handleOpenUpdate
from profile_handler import handleClosedProfile, handleOpenProfile
from mentions_handler import handleMentions
from recwell_scrape import checkOccupancy

########## Authentication ##########
auth = tweepy.OAuthHandler(config('consumer_key', default='cricket_sunday'), config('consumer_secret', default='yello_cactus'))
auth.set_access_token(config('access_token', default='blonde_penguin'), config('access_token_secret', default='happy_harpy'))

api = tweepy.API(auth)


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
    Saturday = 10
    Sunday = 10

# Enumerators containing the respective closing hours
# in 24 hour time (no leading 0). Used Enums for
# readability
# Spring 2021 schedule
class Closing(Enum):    
    Monday = 20
    Tuesday = 20
    Wednesday = 20
    Thursday = 20
    Friday = 20
    Saturday = 18
    Sunday = 18

# GLOBAL VARS
# IS_OPEN: True if operating during Open Hours, False otherwise
# REST: Duration of sleep (15s)
# TWEET_LIMITER: 
# UPDATED_OPEN: True if profile has been updated to open
#               default is True to prevent unwanted updates
#               when redeploying/restarting container
# UPDATED_CLOSE: True if profile has been updated to close
#               default is True to prevent unwanted updates
#               when redploying/restarting container
# OPENING_HOURS: List of Enum values that correspond to opening and closing hours
# DAILY_TOTAL: Keeps track of total number of tweets posted in a day. 
#                Used to circumvent duplicate status error. Reset to 0 at close
IS_OPEN = None
UPDATED_OPEN = False
UPDATED_CLOSE = False
REST = 15
TWEET_LIMITER =  4 * 10
DAILY_TOTAL = 0
OPENING_HOURS = [
                Opening.Monday.value, 
                Opening.Tuesday.value, 
                Opening.Thursday.value,
                Opening.Friday.value,
                Opening.Saturday.value,
                Opening.Sunday.value
                ]    
CLOSING_HOURS = [
                Closing.Monday.value, 
                Closing.Tuesday.value, 
                Closing.Thursday.value,
                Closing.Friday.value,
                Closing.Saturday.value,
                Closing.Sunday.value
                ]

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
# profile to convey The Nick is open (only updates profile once)
def openSetup():
    global IS_OPEN, UPDATED_OPEN, UPDATED_CLOSE
    IS_OPEN = True
    if not UPDATED_OPEN:
        handleOpenUpdate(api)
        handleOpenProfile(api)
        UPDATED_OPEN = True
        UPDATED_CLOSE = False # reset for close update later

# Function that setups globals for close hours and updates the
# profile to convey The Nick is closed (only updates profile once)
def closedSetup():
    global IS_OPEN, UPDATED_OPEN, UPDATED_CLOSE, DAILY_TOTAL
    IS_OPEN = False
    if not UPDATED_CLOSE:
        UPDATED_CLOSE = True
        UPDATED_OPEN = False # reset for open update later
        DAILY_TOTAL = 0
        handleClosedUpdate(api)
        handleClosedProfile(api)

# This loop will control when the bot updates statuses, creates favorites, etc. by
# calling the appropriate functions at the appropriate rate. 
# Checks mentions every 15s, Tweets new status every 10 min (unless capacity is >= 95)

#       Endpoint       | Rate limit window | Rate limit per user
# POST statuses/update |       3 hours     |        300

# POST favorites/create|       3 hours     |        1000
# 900 requests / 15 Minutes
#
# More rate limits: https://developer.twitter.com/en/docs/twitter-api/v1/rate-limits
#
update_naptime = 0
while True:
    try:
        curr_hour = getCurrHour()
        curr_day = getCurrDay()
        # Operates normally during The Nick's open and close hours
        if OPENING_HOURS[curr_day] <= curr_hour < CLOSING_HOURS[curr_day]:
            curr_occupancy = checkOccupancy()
            openSetup()
            update_naptime += 1
            # checkOccupancy returns -1 if exception occurs
            # if the current capacity is under acceptable threshold (95%)
            # and it's been 10 minutes
            if 0 <= curr_occupancy <= 95 and update_naptime == TWEET_LIMITER:
                DAILY_TOTAL += 1
                handleUpdates(api, curr_occupancy, DAILY_TOTAL)
                update_naptime = 0
            handleMentions(api, curr_occupancy, IS_OPEN)
        # If outside of open hours, will not post new updates and
        # responds to mentions with special response
        else:
            closedSetup()
            handleMentions(api, 0, IS_OPEN)
        time.sleep(REST)
    except tweepy.RateLimitError:
        print('Rate Limit Exceeded')
        print('Extended sleep...')
        time.sleep(REST * 60)


