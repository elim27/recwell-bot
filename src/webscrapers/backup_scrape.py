import logging
import requests
from bs4 import BeautifulSoup
from decouple import config
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

URL = 'https://recwell.wisc.edu/liveusage/'
CAPACITY = config('CAPACITY', cast=int)

logging.basicConfig(filename='/var/log/scrapes.log', 
                    filemode='a', 
                    datefmt='%H:%M:%S',
                    level=logging.INFO
)

def calculatePercent(total):
    percent = float(total / CAPACITY) * 100
    return int(percent)

# This function accesses a backup website
# with "live" but less reliable data (since it's updated less
# frequently ~25-50min) however it is better than giving no
# data at all
def checkBackup():
    try:
        # Chrome options
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox') 
        # Remotely use chrome that is hosted in separate container 
        # (hostname: chrome, port: 4444)
        # https://stackoverflow.com/questions/45323271/
        # how-to-run-selenium-with-chrome-in-docker
        driver = webdriver.Remote(
                        command_executor='http://chrome:4444/wd/hub',
                        options=options
        )
        driver.get(URL) 

        # https://stackoverflow.com/questions/59130200/selenium-wait-until-element-
        #               is-present-visible-and-interactable
        current_counts = (WebDriverWait(driver, 20).until
                        (EC.visibility_of_all_elements_located(
                        (By.XPATH, 
                        "//span[@class='tracker-current-count pending']"))))

        # Adds live counts at The Nick together (five seperate counts total)
        # (Only access first 5 since last 3 is info about The Shell)
        total = 0
        for count in range(5):
            total += int(current_counts[count].text) 

        logging.info('checkBackup: ' + str(total))
        return calculatePercent(total)
    except Exception as e:
        logging.info('Error in checkBackup()')
        logging.info(e)
        return -1  
    finally:
        driver.close()
