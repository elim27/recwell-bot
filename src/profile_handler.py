import tweepy


def handleOpenProfile(api):
    try:
        new_description = ('The Nick is currently OPEN \U00002600 '
                        + 'I tweet out every 10 minutes if The Nick is NOT full. '
                        + 'Mention me with #full for a live response \U0001F60E ')
        api.update_profile(name='is the nick full ? \U0001F914', 
                        description=new_description)
        print('OPEN profile updated succesfully! New description: ' 
                        + new_description) 
    except tweepy.TweepError:
        print('Error, profile OPEN FAILED!')

def handleClosedProfile(api):
    try:
        new_description = ('The Nick is currently CLOSED \U0001F4A4 '
                        +'I tweet out every 10 minutes if The Nick is NOT full. '
                        + 'Mention me with #full for a live response \U0001F60E ')
        api.update_profile(name='is the nick full ? \U0001F914', 
                        description=new_description)
        print('CLOSED profile updated succesfully! New description: '
                        + new_description) 
    except tweepy.TweepError:
        print('Error, profile CLOSE FAILED!')
