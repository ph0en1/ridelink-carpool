import gspread
from oauth2client.service_account import ServiceAccountCredentials

def getColumn(column_name):
    sheet_name = 'Sample Data Sheet'
    worksheet_name = 'Sheet1'  # Replace with your worksheet name if different

    def import_column_from_google_sheets(sheet_name, worksheet_name, column_name):
        # Define the scope
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

        # Add your service account JSON file here
        creds = ServiceAccountCredentials.from_json_keyfile_name('appdata/credentials.json', scope)

        # Authorize the clientsheet 
        client = gspread.authorize(creds)

        # Get the sheet
        sheet = client.open(sheet_name).worksheet(worksheet_name)

        # Get all values in the worksheet
        data = sheet.get_all_values()

        # Find the index of the column with the header 'Address'
        header = data[0]
        try:
            column_index = header.index(column_name)
        except ValueError:
            raise Exception(f"Column '{column_name}' not found in the sheet.")

        # Extract the values in the column 'Address'
        column_values = [row[column_index] for row in data[1:]]  # Exclude the header row

        return column_values

    # Get the column values and return them
    column_values = import_column_from_google_sheets(sheet_name, worksheet_name, column_name)
    return column_values


