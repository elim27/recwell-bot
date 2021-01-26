import tweepy
import random
from decouple import config

FILE_PATH_CLOSED = config('CLOSED_PATH')
FILE_PATH_OPEN = config('OPEN_PATH')
CLOSED_NAMES = []
OPEN_NAMES = []
# This functions handles posting new Tweets based on the current capacity
# of The Nick. Is only called in recwell_bot during open hours and if the
# capacity is at an accetable threshold (<= 95%)
# PARAMS:
# api: api object that gives access to Twitter's REST API methods
# curr_occupancy: current occupancy of The Nick as an integer
# DAILY_TOTAL: keeps track of how many updates were given on the day and
#               appends to Tweet. This circumvents duplicate statuses
def handleUpdates(api, curr_occupancy, DAILY_TOTAL):
    curr_percent = ('Current Occupancy: ' + str(curr_occupancy) + '%\n'
                    + 'Daily Update #' + str(DAILY_TOTAL))
    try:
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
    except tweepy.TweepError as e:
        print('Error, tweeting updates...')
        print(e.reason)


# Function selects a gif to post with daily open tweet
# RETURN: Path to file (gif) in string format
def openFileName():
    name_list = config('OPEN_NAMES').split(',')
    for name in name_list:
        OPEN_NAMES.append(name)
    rand_num = random.randint(0, len(OPEN_NAMES) - 1)
    return OPEN_NAMES[rand_num] + '.gif'

def handleOpenUpdate(api):
    file_name = openFileName()
    try:
        path_to_file = FILE_PATH_OPEN + file_name
        print(path_to_file)
        api.update_with_media(filename=path_to_file, 
                        status='The Nick is open! \U0001F64C')
        print('Open update successful!')
    except tweepy.TweepError:
        print('Error with open update')

# Function selects a gif to post with daily close tweet
# RETURN: Path to file (gif) in string format
def closedFileName():
    name_list = config('CLOSED_NAMES').split(',')
    for name in name_list:
        CLOSED_NAMES.append(name)
    rand_num = random.randint(0, len(CLOSED_NAMES) - 1)
    return CLOSED_NAMES[rand_num] + '.gif'

    
def handleClosedUpdate(api):
    file_name = closedFileName()
    try:
        path_to_file = FILE_PATH_CLOSED + file_name
        api.update_with_media(filename=path_to_file, 
                        status='The Nick is now closed. \U0000270C')
        print('Closed update successful!')
    except tweepy.TweepError:
        print('Error with closed update')

 