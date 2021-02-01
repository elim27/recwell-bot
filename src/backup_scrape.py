import requests
from decouple import config
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

URL = 'https://recwell.wisc.edu/liveusage/'
PATH = config('DRIVER_PATH')
CAPACITY = config('CAPACITY', cast=int)

def calculatePercent(total):
    percent = float(total / CAPACITY) * 100
    return int(percent)

def checkBackup():
    try:
        driver = webdriver.Chrome(PATH)
        driver.get(URL) 
        current_counts = WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located((By.XPATH, "//span[@class='tracker-current-count pending']")))
        
        total = 0
        for count in range(5):
            total += int(current_counts[count].text)      
        curr_occupancy = calculatePercent(total)
    except:
        print('Error in checkBackup()')
        curr_occupancy = -1
    print(curr_occupancy)    
    return curr_occupancy

checkBackup()
    