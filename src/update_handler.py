import tweepy
import random
import pytz
from datetime import datetime
from decouple import config

FILE_NAME = config('FILE_NAME_DAY')
FILE_PATH_CLOSED = config('CLOSED_PATH')
FILE_PATH_OPEN = config('OPEN_PATH')
CLOSED_NAMES = []
OPEN_NAMES = []

# Function that reads from curr_day.txt file to retrieve the
# current day # and avoid Twitter duplicate status violations
# PARAMS:
# file_name: path to file where day # is stored
# RETURN: day #
def getDay(file_name):
    last_id = 0
    try:
        fr = open(file_name, 'r')
        last_id = int(fr.read().strip())           
        fr.close()
    except ValueError:
        last_id = 0
    except FileNotFoundError:
        print('Error in getDay')
        print('FileNotFoundError :(')

    return last_id

# Funciton that writes to curr_day.txt file to save the
# incremented day @
# PARAMS:
# file_name: path to file where day # is stored
# last_id: day #
def storeDay(file_name, last_id):
    try:
        fw = open(file_name, 'w')
        fw.write(str(last_id))
        fw.close()
    except FileNotFoundError:
        print('Error in storeDay')
        print(FILE_NAME + ' not found :(')

# Function that gets the current time (in CST)
# and returns it so it can't be used in status
# updates.
# RETURN: the current time
def getTime():
    CST = pytz.timezone('US/Central')
    curr_time = datetime.today().astimezone(CST).strftime('%I:%M %p').lstrip('0')
    print('Current Time: ' + curr_time)
    return curr_time
 
# This functions handles posting new Tweets based on the current capacity
# of The Nick. Is only called in recwell_bot during open hours and if the
# capacity is at an accetable threshold (<= 95%)
# PARAMS:
# api: api object that gives access to Twitter's REST API methods
# curr_occupancy: current occupancy of The Nick as an integer
# DAILY_UPDATE: keeps track of how many updates were given on the day and
#               appends to Tweet. This circumvents duplicate statuses
def handleUpdates(api, curr_occupancy):
    curr_time = getTime()
    curr_percent = ('Current Occupancy: ' + str(curr_occupancy) + '%\n'
                    + '[ ' + curr_time + ' CST]')
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


# Function selects a gif to post with daily close tweet
# Populates OPEN_NAMES list with names of files (names stored
# in environment variables in the format: name1,name2,name3,...)
#  Uses random generator to select a gif from the list.
# RETURN: filename of gif to use
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
        api.update_with_media(filename=path_to_file, 
                        status='The Nick is open! Day #' 
                        + str(getDay(FILE_NAME)) + ' \U0001F64C')
        print('Open Tweet successful!')
    except tweepy.TweepError as e:
        print('Error with open Tweet')
        print(e.reason)

# Function selects a gif to post with daily close tweet
# Populates CLOSED_NAMES list with names of files (names stored
# in environment variables in the format: name1,name2,name3,...)
#  Uses random generator to select a gif from the list.
# RETURN: filename of gif to use
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
        # increment the day counter at close and store
        # into the the file
        storeDay(FILE_NAME, getDay(FILE_NAME) + 1)
        print('Closed Tweet successful!')
    except tweepy.TweepError as e:
        print('Error with closed Tweet')
        print(e.reason)