import logging
import re
import requests
import time
from bs4 import BeautifulSoup
from backup_scrape import checkBackup

# Global Vars
# URL: source for web scraping
# BACKUP_DATA: If using backup data from less accurate reserve
#               BACKUP_DATA -> True
URL = 'https://services.recwell.wisc.edu/FacilityOccupancy'
BACKUP_DATA = False

logging.basicConfig(filename='/var/log/scrapes.log', 
                    filemode='a', 
                    datefmt='%H:%M:%S',
                    level=logging.INFO
)
# This functions checks The Nick's live building usage
# RETURN: Dictionary that contains
#  percent of occupancy as an integer, returns -1
# if an exception occurs. And the boolean BACKUP_DATA
# which is True if checkBackup() was used
def checkOccupancy():
    global BACKUP_DATA
    main_content = requests.get(URL).text
    soup = BeautifulSoup(main_content, 'html.parser')
    try:
        page_content = soup.find('p', class_='occupancy-count')
        if page_content is None:
            # if for some reason the percent is not available,
            # check the chart's data ratio
            occupancy_num = checkChart(soup)
        else: 
            occupancy_percentage = page_content.text.strip()
            occupancy_num = re.search(r'(\d+)', occupancy_percentage).group(0)
            BACKUP_DATA = False

        data = {'occupancy_num': int(occupancy_num), 'BACKUP_DATA': BACKUP_DATA} 
        # logging.info('Occupancy num: '+ str(occupancy_num))
        return data
    except:
        logging.info('Error in checkOccupancy()')


# This function is the "back up" to checkOccupancy
# Sometimes the source website tweaks and the percentage
# disappears. However, to get the percentage, there is an
# HTML attribute called 'data-ratio' for the graph
# which holds the percentage as a ratio (decimal).
# Simply type casting as a float and multiplying a 100 and 
# then type cast to int solves the problem
# RETURN: the occupancy percntage as an integer from
# 'data-ratio'
def checkChart(soup):
    global BACKUP_DATA
    BACKUP_DATA = False
    try:
        chart_content = soup.find('canvas', class_='occupancy-chart').attrs
        data_ratio = chart_content['data-ratio']
        ratio_num = float(data_ratio) * 100  
        occupancy_num = int(ratio_num)
    except:
        logging.error('Error in checkChart()')
        # If the whole website is down,
        # It will access the backup backup
        # website with live but less reliable data
        # BACKUP_DATA set to False since the data is not as reliable
        BACKUP_DATA = True
        occupancy_num = checkBackup()    
    return occupancy_num

