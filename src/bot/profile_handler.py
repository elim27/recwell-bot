import logging
import tweepy

logging.basicConfig(filename='/var/log/handlers.log', 
                    filemode='a', 
                    datefmt='%H:%M:%S',
                    level=logging.INFO
)
# This function updates the profile of the bot to an 'open' or 'closed'
# status based on if the building is open or not.
# PARAMS:
# api: api object that gives access to Twitter's REST API methods
# IS_OPEN: True if The Nick is open, False otherwise
def handleProfile(api, IS_OPEN):
    try:
        # If The Nick is open, switch the OPEN/CLOSED text and emoji
        if IS_OPEN:
            open_closed_indicator = 'OPEN \U00002600'
            name_emoji = '\U0001F914' # thinking face
        else:
            open_closed_indicator = 'CLOSED \U0001F4A4'
            name_emoji = '\U0001F634' # sleeping face
        
        new_description = ('The Nick is currently ' + open_closed_indicator 
                        + ' I tweet out the current occupancy of The Nick ' 
                        + 'in 25 minute cycles \U000023F0 Mention me with '
                        + '#full for a live response \U0001F60E')
        api.update_profile(name='is the nick full ? ' + name_emoji,
                        description=new_description)
        logging.info('Profile updated successfully!')
    except tweepy.TweepError:
        logging.error('Error, profile update FAILED!')
        

