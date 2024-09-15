import gspread
from oauth2client.service_account import ServiceAccountCredentials
from data import getColumn
from geopy.geocoders import Nominatim
import time

def pre_cache():
    # Authenticate and connect to the Google Sheets API
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)

    # Open the Google Sheet by name
    sheet = client.open("Sample Data Sheet").sheet1  # Open the first sheet

    # Geolocator setup
    geolocator = Nominatim(user_agent="your_app_name")  # Replace with a meaningful user agent

    # Example: Get the list of addresses
    addressList = getColumn("Address")

    # List to store coordinates
    coordsList = []
    count = 0
    # Convert addresses to coordinates and store them in coordsList
    for address in addressList:
        try:
            location = geolocator.geocode(address)
            if location:
                coordsList.append(f"{location.latitude}, {location.longitude}")
            else:
                coordsList.append("Not found")  # Handle addresses that can't be geocoded
        except Exception as e:
            coordsList.append("Error")  # Handle errors and continue
            print(f"Error geocoding address {address}: {e}")
        count += 1
        print(count)
        
        time.sleep(0)  # Add a small delay to avoid overloading the geocoding service

    # Start inserting values from row 1 in column M using batch update
    start_row = 2
    column = 'M'

    # Prepare a list of cell updates (batch processing)
    cell_list = sheet.range(f'{column}{start_row}:{column}{start_row + len(coordsList) - 1}')

    count2 = 0
    # Assign the coordinates to the corresponding cells
    for i, cell in enumerate(cell_list):
        cell.value = coordsList[i]

    # Perform a batch update to reduce the number of API requests
    sheet.update_cells(cell_list)

    print("Coordinates added to column M successfully!")

