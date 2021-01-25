import tweepy

def handleUpdates(api, curr_occupancy):
    try:
        curr_percent = 'Current Occupancy: ' + str(curr_occupancy) + '%'

        if 90 < curr_occupancy <= 95:
            api.update_status('Close to full, hurry over! \U0001F3C3\n' 
                            + curr_percent) 
        elif 80 < curr_occupancy <= 90:
            api.update_status('There are still some spots left\n' + curr_percent )
        elif 70 < curr_occupancy <= 80:
            api.update_status(curr_percent)
        elif curr_occupancy == 69:
            api.update_status('Nice.\n' + curr_percent)
        elif curr_occupancy <= 70:
            api.update_status('This would be an excellent time to go\n'
                            + curr_percent)   
    except tweepy.TweepError as e:
        print('Error, tweeting updates...')
        print(e.reason)

 