import gspread
from oauth2client.service_account import ServiceAccountCredentials
from geopy.geocoders import Nominatim
import time
import tkinter as tk
from tkinter import messagebox
import webbrowser
from geopy.distance import geodesic
import folium
import smtplib
import ssl
import math
from email.message import EmailMessage

#---------------------------------------------FUNCTIONS---------------------------------------
import random
from gspread_formatting import CellFormat, Color

import random
from gspread_formatting import format_cell_range, CellFormat, Color

def pre_cache():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)

    sheet = client.open("Sample Data Sheet").sheet1
    geolocator = Nominatim(user_agent="your_app_name")
    addressListPC = getColumn("Address")

    coordsListPC = []
    countPC = 0
    for address in addressListPC:
        try:
            location = geolocator.geocode(address)
            if location:
                coordsListPC.append(f"{location.latitude}, {location.longitude}")
            else:
                coordsListPC.append("Not found")
        except Exception as e:
            coordsListPC.append("Error")
            print(f"Error geocoding address {address}: {e}")
        countPC += 1
        print(countPC)
        time.sleep(0)

    start_row = 2
    coords_column = 'M'
    ids_column = 'L'

    coords_cell_list = sheet.range(f'{coords_column}{start_row}:{coords_column}{start_row + len(coordsListPC) - 1}')
    ids_cell_list = sheet.range(f'{ids_column}{start_row}:{ids_column}{start_row + len(coordsListPC) - 1}')

    for i, (coords_cell, ids_cell) in enumerate(zip(coords_cell_list, ids_cell_list)):
        coords_cell.value = coordsListPC[i]
        ids_cell.value = str(random.randint(100000, 999999))  # Generate a random 6-digit number

        # Highlight rows with "Error" in the `M` column
        if coords_cell.value in ["Error", "Not found"]:
            row_index = start_row + i
            error_format = CellFormat(
                backgroundColor=Color(1, 0, 0)  # Red background
            )
            format_cell_range(sheet, f'A{row_index}:Z{row_index}', error_format)

    sheet.update_cells(coords_cell_list)
    sheet.update_cells(ids_cell_list)
    print("Coordinates and User IDs added successfully!")


    
def getColumn(column_name):
    sheet_name = 'Sample Data Sheet'
    worksheet_name = 'Sheet1'

    def import_column_from_google_sheets(sheet_name, worksheet_name, column_name):
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
        client = gspread.authorize(creds)
        sheet = client.open(sheet_name).worksheet(worksheet_name)
        data = sheet.get_all_values()
        header = data[0]
        try:
            column_index = header.index(column_name)
        except ValueError:
            raise Exception(f"Column '{column_name}' not found in the sheet.")
        return [row[column_index] for row in data[1:]]  

    return import_column_from_google_sheets(sheet_name, worksheet_name, column_name)

#---------------------------------------------CODE--------------------------------------------
loginWindow = tk.Tk()
loginWindow.title("Carpool Finder Application Login")
loginWindow.geometry("900x800")
loginWindow.configure(bg="lightgrey")

login = ""
error = "false"
count = 0

coord_list = getColumn("Coordinates")
randomid_list = getColumn("UserID")
address_list = getColumn("Address")
name_list = getColumn("Student Name")
id_list = getColumn("Student ID")
email_list = getColumn("Parent Email")
filtered_addresses = []
filtered_coords = []
filtered_userids = []
filtered_emails = []
geolocator = Nominatim(user_agent="heylads")
coordinate_cache = {}

def returnCoor(address):
    if address not in coordinate_cache:
        location = geolocator.geocode(address)
        if location:
            coordinate_cache[address] = (location.latitude, location.longitude)
        else:
            return None
    return coordinate_cache[address]

def findNearbyAddresses(houseAddress, max_distance):
    global filtered_addresses, filtered_coords, filtered_userids, filtered_emails
    filtered_addresses.clear()
    filtered_coords.clear()
    filtered_userids.clear()
    filtered_emails.clear()

    houseCoor = returnCoor(houseAddress)
    if not houseCoor:
        messagebox.showerror("Error", "Invalid house address.")
        return

    for i in range(len(coord_list)):
        try:
            addressCoor = tuple(map(float, coord_list[i].split(',')))
            if addressCoor:
                distance = geodesic(houseCoor, addressCoor).miles
                if distance < max_distance:
                    filtered_addresses.append(address_list[i])
                    filtered_coords.append(addressCoor)
                    filtered_userids.append(randomid_list[i])
                    filtered_emails.append(email_list[i])
        except Exception as e:
            print(f"Error processing address '{address_list[i]}': {e}")

    if not filtered_addresses:
        messagebox.showinfo("Info", "No nearby addresses found.")

import random

def displace_coordinates(coord, max_displacement=0.2):
    """
    Displaces a coordinate by a random amount within the given maximum displacement in miles.
    """
    # Convert miles to degrees (approximation: 1 mile ≈ 0.0145 degrees latitude/longitude)
    max_deg = max_displacement * 0.0145

    lat_offset = random.uniform(-max_deg, max_deg)
    lon_offset = random.uniform(-max_deg, max_deg)

    # Adjust for longitude scaling based on latitude
    lon_offset /= abs(math.cos(math.radians(coord[0])))

    return coord[0] + lat_offset, coord[1] + lon_offset


def mapFunc():
    houseAddress = answer1.get()
    findNearbyAddresses(houseAddress, 0.5)

    if not filtered_coords:
        messagebox.showinfo("Info", "No nearby addresses found.")
        return

    m = folium.Map(location=returnCoor(houseAddress), zoom_start=13)

    # Add a marker for the user's house
    folium.Marker(
        returnCoor(houseAddress),
        popup=houseAddress,
        icon=folium.Icon(color="red", icon="home")
    ).add_to(m)

    # Add markers for nearby addresses with displaced coordinates
    for i in range(len(filtered_addresses)):
        coord = filtered_coords[i]
        displaced_coord = displace_coordinates(coord)  # Apply displacement
        folium.Marker(
            location=displaced_coord,
            popup=f"User ID: {filtered_userids[i]}"
        ).add_to(m)

    # Save and open the map
    m.save("map.html")
    webbrowser.open("map.html")


def emailSend(u_id, contact):
    receiving_email = None
    for i in range(len(filtered_userids)):
        if int(filtered_userids[i]) == int(u_id):
            receiving_email = filtered_emails[i]
            break

    if not receiving_email:
        messagebox.showerror("Error", "No email found for the given User ID.")
        return

    sender = "noreply.ridelink"
    password = "xixj wsgw fgup zzmf"
    port = 465
    domain = "smtp.gmail.com"

    message = EmailMessage()
    message["From"] = sender
    message["To"] = receiving_email
    message["Subject"] = "RideLink Message Request"
    message.set_content(f"Hello! I have a student that goes to the same school as yours. I am interested in a carpool! If you would like to contact me, here is my info: {contact} \n \n \n THIS IS AN AUTOMATED MESSAGE FROM RIDELINK \n no reply, contact number/email specified above instead")

    context = ssl.create_default_context()
    try:
        with smtplib.SMTP_SSL(domain, port, context=context) as server:
            server.login(sender, password)
            server.send_message(message)
        messagebox.showinfo("Email Status", "Email Sent.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to send email: {e}")

def emailWindow():
    window2 = tk.Toplevel(window)
    window2.title("Send Carpool Request")
    window2.geometry("900x800")
    window2.configure(bg="lightgrey")

    tk.Label(window2, text="Enter User ID to send carpool request via email!", font=("Arial", 23), bg="lightgrey", fg="black").pack(pady=8)
    userid_entry = tk.Entry(window2, font=("Arial", 23), bg="lightgrey", fg="black")
    userid_entry.pack(pady=5)

    tk.Label(window2, text="Where can the receiver of your request contact you?", font=("Arial", 23), bg="lightgrey", fg="black").pack(pady=5)
    contact_info = tk.Entry(window2, font=("Arial", 23), bg="lightgrey", fg="black")
    contact_info.pack(pady=58)

    def handle_email_send():
        u_id = userid_entry.get()
        contact = contact_info.get()
        if not u_id or not contact:
            messagebox.showerror("Error", "User ID and contact information are required.")
            return
        emailSend(u_id, contact)

    tk.Button(window2, text="Send Email", font=("Times New Roman", 24), bg="blue", fg="white", command=handle_email_send).pack(pady=20)

def logintest():
    loginuser = userName.get()
    loginID = userid.get()
    for i in range(len(name_list)):
        if name_list[i] == loginuser and id_list[i] == loginID:
            global login
            login = "splendid"

    if login != "splendid":
        messagebox.showerror("Login Invalid", "Please check your credentials and try again")
    else:
        global window
        window = tk.Toplevel(loginWindow)
        window.title("Carpool Finder Application")
        window.geometry("900x800")
        window.configure(bg="lightgrey")

        title = tk.Label(window, text="Carpool Finder", font=("Arial", 40), bg="white", fg="red")
        title.pack(pady=10)

        tk.Label(window, text="Where is your house?", font=("Arial", 20), bg="white", fg="black").pack(pady=40)

        global answer1
        answer1 = tk.Entry(window, width=15, font=("Times New Roman", 24), bg="lightgrey", fg="red")
        answer1.pack(pady=20)

        tk.Button(window, text="Set up Data", font=("Times New Roman", 24), bg="blue", fg="white", command=pre_cache).pack(pady=20)
        tk.Button(window, text="Find Nearby Addresses", font=("Times New Roman", 24), bg="blue", fg="white", command=mapFunc).pack(pady=20)
        tk.Button(window, text="Send Email", font=("Times New Roman", 24), bg="blue", fg="white", command=emailWindow).pack(pady=20)

tk.Label(loginWindow, text="Login Below!", font=("Arial", 23), bg="lightgrey", fg="black").pack(pady=8)
tk.Label(loginWindow, text="Student Name", font=("Arial", 23), bg="lightgrey", fg="black").pack()
userName = tk.Entry(loginWindow, font=("Arial", 23), bg="lightgrey", fg="black")
userName.pack()

tk.Label(loginWindow, text="Student ID", font=("Arial", 23), bg="lightgrey", fg="black").pack()
userid = tk.Entry(loginWindow, font=("Arial", 23), bg="lightgrey", fg="black")
userid.pack()

tk.Button(loginWindow, text="Login", font=("Arial", 23), bg="blue", fg="white", command=logintest).pack(pady=20)
loginWindow.mainloop()
