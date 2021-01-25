import requests
import re
from bs4 import BeautifulSoup

URL = 'https://services.recwell.wisc.edu/FacilityOccupancy'

main_content = requests.get(URL).text
soup = BeautifulSoup(main_content, 'html.parser')

def checkOccupancy():
    page_content = soup.find('p', class_='occupancy-count')
    occupancy_percentage = page_content.text.strip()
    occupancy_num = re.search(r'(\d+)', occupancy_percentage).group(0)

    print('curr occupancy: ' + occupancy_num)
    return int(occupancy_num)
