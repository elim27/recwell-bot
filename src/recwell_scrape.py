import requests
import time
import re
from bs4 import BeautifulSoup

URL = 'https://services.recwell.wisc.edu/FacilityOccupancy'

# This functions checks The Nick's live building usage
# RETURN: The percent of occupancy as an integer, returns -1
# if an exception occurs.
def checkOccupancy():
    main_content = requests.get(URL).text
    soup = BeautifulSoup(main_content, 'html.parser')
    try:
        page_content = soup.find('p', class_='occupancy-count')
        print(page_content)
        if page_content is None:
            # if for some reason the percent is not available,
            # check the chart's data ratio
            occupancy_num = checkChart(soup)
        else: 
            occupancy_percentage = page_content.text.strip()
            occupancy_num = re.search(r'(\d+)', occupancy_percentage).group(0)
            print('checkOccupancy(): ' + str(occupancy_num) + '%')
    except:
        print('Error in checkOccupancy()')
        occupancy_num = -1
    return int(occupancy_num)

# This function is the "back up" to checkOccupancy
# Sometimes the source website tweaks and the percentage
# disappears. However, to get the percentage, there is an
# HTML attribute called 'data-ratio' for the graph
#  which holds the percentage as a ratio (decimal).
# Simply type casting as a float and multiplying a 100 and 
# then type cast to int solves the problem
# RETURN: the occupancy percntage as an integer from
# 'data-ratio', if the whole site is down (it happens)
# will return -1
def checkChart(soup):
    try:
        chart_content = soup.find('canvas', class_='occupancy-chart').attrs
        print(chart_content)
        data_ratio = chart_content['data-ratio']
        ratio_num = float(data_ratio) * 100  
        occupancy_num = int(ratio_num)
        print('checkChart(): ' + str(occupancy_num) + '%')
    except:
        print('Error in checkChart()')
        occupancy_num = -1
    return occupancy_num