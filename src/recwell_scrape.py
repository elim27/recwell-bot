import requests
import re
from bs4 import BeautifulSoup

URL = 'https://services.recwell.wisc.edu/FacilityOccupancy'

main_content = requests.get(URL).text
soup = BeautifulSoup(main_content, 'html.parser')

# This functions checks The Nick's live building usage
# RETURN: The percent of occupancy as an integer, returns -1
# if an exception occurs.
def checkOccupancy():
    try:
        page_content = soup.find('p', class_='occupancy-count')
        occupancy_percentage = page_content.text.strip()
        occupancy_num = re.search(r'(\d+)', occupancy_percentage).group(0)
    except:
        print('Error in checkOccupancy.')
        occupancy_num = -1

    print('curr occupancy: ' + str(occupancy_num))
    return int(occupancy_num)
