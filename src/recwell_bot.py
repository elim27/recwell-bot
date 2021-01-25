import tweepy
import time
from decouple import config
from update_handler import handleUpdates
from mentions_handler import handleMentions
from recwell_scrape import checkOccupancy

########## Authentication ##########
auth = tweepy.OAuthHandler(config('consumer_key', default='cricket_sunday'), config('consumer_secret', default='yello_cactus'))
auth.set_access_token(config('access_token', default='blonde_penguin'), config('access_token_secret', default='happy_harpy'))

api = tweepy.API(auth)

REST = 15
TWEET_LIMITER =  4 * 10

update_naptime = 0

while True:
    try:
        curr_occupancy = checkOccupancy()
        update_naptime += 1

        if curr_occupancy <= 95 and update_naptime == TWEET_LIMITER:
            handleUpdates(api, curr_occupancy)
            update_naptime = 0
        
        handleMentions(api, curr_occupancy)
        print('sleeping...')
        time.sleep(REST)
    except tweepy.RateLimitError:
        time.sleep(REST * 60)