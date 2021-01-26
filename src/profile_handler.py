import tweepy

# This function updates the profile of the bot to an 'open' status
# PARAMS:
# api: api object that gives access to Twitter's REST API methods
def handleOpenProfile(api):
    try:
        new_description = ('The Nick is currently OPEN \U00002600 '
                        + 'I tweet out every 10 minutes if The Nick is NOT full. '
                        + 'Mention me with #full for a live response \U0001F60E ')
        api.update_profile(name='is the nick full ? \U0001F914', 
                        description=new_description)
        print('OPEN profile updated succesfully!')
    except tweepy.TweepError:
        print('Error, profile OPEN FAILED!')

# This function updates the profile of the bot to a 'closed' status
# PARAMS:
# api: api object that gives access to Twitter's REST API methods
def handleClosedProfile(api):
    try:
        new_description = ('The Nick is currently CLOSED \U0001F4A4 '
                        +'I tweet out every 10 minutes if The Nick is NOT full. '
                        + 'Mention me with #full for a live response \U0001F60E ')
        api.update_profile(name='is the nick full ? \U0001F914', 
                        description=new_description)
        print('CLOSED profile updated succesfully!')
    except tweepy.TweepError:
        print('Error, profile CLOSE FAILED!')
