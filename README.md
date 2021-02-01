# IsTheNickFull

IsTheNickFull is a Twitter bot that informs users on the current occupancy of The Nick (a recwell center at UW-Madison).
Due to the building's 25% capacity rule, the building's occupancy usually hovers around 100% with lines out the dorr
and it can be frustrating to constantly check the facility's live usage since it's always at 100% (so it seems). 
This bot aims to automate that process of checking the facility's usage and notify users when the building has an acceptable
amount of users.

It is built with [Python](https://www.python.org/) and uses the
[Tweepy](https://www.tweepy.org/) library to access the Twitter API and the [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
library for web scraping. [Selenium]https://selenium-python.readthedocs.io/ is also used to drive a back up site and scrape info to calculate occupancy
but isn't used unless the main source site is down (which happens somewhat frequently) becuase the data is not always up to date.

Check it out on Twitter: [@IsTheNickFull](https://twitter.com/IsTheNickFull)

## Current Features
* Tweets out an opening/closing status at the open/close hours
* Only operates during open/close hours (special response for mentions outside
  of operating hours)
* Tweets the current occupancy (percentage) every 25 minutes with a time stamp in CST
  * SPECIAL CASES: 
  * If the building is consitently at capacity, the bot will not tweet
    out again until the capacity is at least under 95%
  * Notifies users of an issue if both source sites for scraping are down
    and will not Tweet out again until a valid response is received
* Handles mentions from Twitter users that utilize #full and responds
  with the current capacity of The Nick
  * SPECIAL RESPONSES:
   * Notify users that The Nick is closed if mentioned outside of open hours
   * Notify users that the service is down if mentioned and source sites are down

## Environment Variables
How the .env file is structured

```
consumer_key=[TWITTER_API_KEY]
consumer_secret=[TWITTER_API_KEY_SECRET]
access_token=[TWITTER_ACCESS_TOKEN]
access_token_secret=[TWITTER_ACCESS_TOKEN_SECRET]

other variables...
```

## Deploying to Azure

```
docker run --env-file .env --restart=on-failure --name="[NAME_OF_CONTAINER]" IMAGE
```
For more info: [Deploying Docker Containers on Azure](https://docs.docker.com/cloud/aci-integration/)

## Author
[Ethan Lim](http://www.ethan-lim.com)
