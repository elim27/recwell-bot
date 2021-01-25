import tweepy

# UPDATE_BASIC: to avoid violating Twitter's guidelines on duplicate statuses
# the UPDATE_BASIC boolean alternates between True for a basic status update
# and False for a novel status update so no duplicates occur for the same
# percentages
UPDATE_BASIC = False

# This functions handles posting new Tweets based on the current capacity
# of The Nick. Is only called in recwell_bot during open hours and if the
# capacity is at an accetable threshold (<= 95%)
# PARAMS:
# api: api object that gives access to Twitter's REST API methods
# curr_occupancy: current occupancy of The Nick as an integer
def handleUpdates(api, curr_occupancy):
    try:
        curr_percent = 'Current Occupancy: ' + str(curr_occupancy) + '%'
        if UPDATE_BASIC:
            UPDATE_BASIC = False
            basicTweet(api, curr_occupancy, curr_percent)
        else:
            novelTweet(api, curr_occupancy, curr_percent)
            UPDATE_BASIC = True
        print('Tweet posted!') 
    except tweepy.TweepError as e:
        print('Error, tweeting updates...')
        print(e.reason)

# This function posts unique/novel tweets as statuses with different
# messages dependant on the occupancy threshold
# PARAMS:
# api: api object that gives access to Twitter's REST API methods
# curr_occupancy: current occupancy of The Nick as an integer
# curr_percent: current occupancy percentage as a string
def novelTweet(api, curr_occupancy, curr_percent):
    if 90 < curr_occupancy <= 95:
        api.update_status('Nope! But close to full, hurry over! ' 
                        + '\U0001F3C3\n' + curr_percent) 
    elif 80 < curr_occupancy <= 90:
        api.update_status('Nope! There are still some spots left\n'
                        + curr_percent)
    elif 70 < curr_occupancy <= 80:
        api.update_status('Nope! This would be a decent time to go '
                        + '\U0001F440\n' + curr_percent)
    elif curr_occupancy == 69:
        api.update_status('Nice. \U0001F60E\n' + curr_percent)
    elif curr_occupancy <= 70:
        api.update_status('Nope! This would be an excellent time to go '
                        + '\U0001F3C6\n' + curr_percent)  

# This function posts basic tweets as statuses the same message
# independent of occupancy threshold
# PARAMS:
# api: api object that gives access to Twitter's REST API methods
# curr_occupancy: current occupancy of The Nick as an integer
# curr_percent: current occupancy percentage as a string
def basicTweet(api, curr_occupancy, curr_percent):
    if 90 < curr_occupancy <= 95:
        api.update_status('Nope!\n' + curr_percent) 
    elif 80 < curr_occupancy <= 90:
        api.update_status('Nope!\n' + curr_percent)
    elif 70 < curr_occupancy <= 80:
        api.update_status('Nope!\n' + curr_percent)
    elif curr_occupancy == 69:
        api.update_status('\U0001F60E\n' + curr_percent)
    elif curr_occupancy <= 70:
        api.update_status('Nope!\n' + curr_percent)  