import logging
import pytz
import random
import tweepy
from datetime import datetime
from decouple import config
from recwell_scrape import checkOccupancy


FILE_NAME = config('FILE_PATH_DAY')
FILE_PATH_CLOSED = config('FILE_PATH_CLOSED')
FILE_PATH_OPEN = config('FILE_PATH_OPEN')
LAST_PERCENT = 0
CLOSED_NAMES = []
OPEN_NAMES = []

logging.basicConfig(filename='/var/log/handlers.log', 
                    filemode='a', 
                    datefmt='%H:%M:%S',
                    level=logging.INFO
)
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
        logging.info('Error in getDay')
        logging.info('FileNotFoundError :(')

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
        logging.info('Error in storeDay')
        logging.info(FILE_NAME + ' not found :(')

# Function that gets the current time (in CST)
# and returns it so it can't be used in status
# updates.
# RETURN: the current time
def getTime():
    CST = pytz.timezone('US/Central')
    curr_time = datetime.today().astimezone(CST).strftime('%I:%M %p').lstrip('0')
    logging.info('Current Time: ' + curr_time)
    return curr_time
 
# This functions handles posting new Tweets based on the current capacity
# of The Nick. Is only called in recwell_bot during open hours and if the
# there is no error in curr_occupancy
# PARAMS:
# api: api object that gives access to Twitter's REST API methods
# curr_occupancy: Dictionary with current occupancy of The Nick as an integer
#               and a boolean signifying if resulting data is valid
# DAILY_UPDATE: keeps track of how many updates were given on the day and
#               appends to Tweet. This circumvents duplicate statuses
def handleUpdates(api):
    global LAST_PERCENT
    try:
        # Get relevant information
        curr_time = getTime()
        curr_occupancy = int(checkOccupancy()['occupancy_num'])
        backup_data = checkOccupancy()['BACKUP_DATA']
        curr_percent = ('Current Occupancy: ' + str(curr_occupancy) + '%\n'
                        + '[' + curr_time + ' CST]')
    
        # Notify users the data may not be completely accurate
        if backup_data:
            curr_percent += ('\n NOTE: Recwell Services down, using backup '
                            + 'data... Results may not be up to date!')
        # Handle error case (where curr_occupancy is -1)
        # Notifies followers that the bot encountered an issue when
        # scraping for data and will "sleep" until the sites are back up
        if curr_occupancy == -1 and LAST_PERCENT != -1:
             api.update_status('Uh oh, looks like my source\'s server '
                            + 'is down... \U0001F6A7 I\'ll Tweet out again '
                            + 'when the issue is resolved. \n'
                            + '[' + curr_time + ' CST]')
        elif curr_occupancy != -1: 
            # Tweets out when The Nick reaches capacity, and "sleeps"
            # until the capacity dips under the 95% threshold (i.e. if LAST_PERCENT
            # stays at 100 or above 95, it won't Tweet out again until reaching
            # acceptable levels, this way we avoid spamming the same "full" tweets 
            if curr_occupancy == 100 and LAST_PERCENT <= 95:
                api.update_status('Yes. The Nick is full. \U0001F6A8\n' 
                                + curr_percent)
            # Extreme occupancy
            elif 90 < curr_occupancy <= 95:
                api.update_status('Nope! But close to full, hurry over! ' 
                                + '\U0001F3C3\n' + curr_percent)
            # High occupancy
            elif 80 < curr_occupancy <= 90:
                api.update_status('Nope! There are still some spots left\n'
                                + curr_percent)
            # Medium occupancy
            elif 70 < curr_occupancy <= 80:
                api.update_status('Nope! This would be a decent time to go '
                                + '\U0001F440\n' + curr_percent)
            # Nice occupancy
            elif curr_occupancy == 69:
                api.update_status('Nice. \U0001F60E\n' + curr_percent)
            # Moderate to Low occupancy
            elif curr_occupancy <= 70:
                api.update_status('Nope! This would be an excellent time to go '
                                + '\U0001F3C6\n' + curr_percent)
        LAST_PERCENT = curr_occupancy
        logging.info("Status update successful! " + curr_percent)  
    except Exception as e:
        logging.error('Error, tweeting updates...')
        logging.error(e)

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

# Function handles the daily opening/closing updates
# that must be Tweeted out at open/close hours.
def handleDailyUpdates(api, IS_OPEN):
    try:
        if IS_OPEN:
            file_name = openFileName()
            path_to_file = FILE_PATH_OPEN + file_name
            api.update_with_media(filename=path_to_file, 
                            status='The Nick is open! Day #' 
                            + str(getDay(FILE_NAME)) + ' \U0001F64C')
        else:
            file_name = closedFileName()
            path_to_file = FILE_PATH_CLOSED + file_name
            api.update_with_media(filename=path_to_file, 
                        status='The Nick is now closed. Day #' 
                        + str(getDay(FILE_NAME)) + ' over! \U0000270C')
            # increment the day counter at close and store
            # into the the file
            storeDay(FILE_NAME, getDay(FILE_NAME) + 1)
        logging.info('Daily Tweet Successful!')
    except Exception as e:
        logging.error('Error posting Daily Tweet.')
        logging.error(e)
