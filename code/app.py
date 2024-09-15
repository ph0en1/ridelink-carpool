import tkinter as tk
from tkinter import messagebox
import webbrowser
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import folium
from data import getColumn
from PRECACHETEST import pre_cache
import time

loginWindow = tk.Tk()
loginWindow.title("Carpool Finder Application Login")
loginWindow.geometry("900x800")
loginWindow.configure(bg="lightgrey")
# Set up the main window

login = ""
error = "false"
count = 0

# Fetch data from external source'
coord_list = getColumn("Coordinates")
"""for i in coord_list:
    i.split(",")
    i=float(i)"""
address_list = getColumn("Address")
name_list = getColumn("Student Name")
id_list = getColumn("Student ID")
filtered_addresses = []
filtered_names = []
filtered_id = []
filtered_coords = []
geolocator = Nominatim(user_agent="heylads")
coordinate_cache = {}

# Function to get coordinates with caching
def returnCoor(address):
    if address not in coordinate_cache:
        location = geolocator.geocode(address)
        if location:
            coordinate_cache[address] = (location.latitude, location.longitude)
        else:
            return None  # Handle geocoding failure
    return coordinate_cache[address]

# Function to find nearby addresses based on distance with batch processing
def findNearbyAddresses(houseAddress, max_distance, batch_size=5):
    global filtered_addresses, filtered_id, filtered_names, filtered_coords
    filtered_addresses.clear()
    filtered_id.clear()
    filtered_names.clear()
    filtered_coords.clear()  # Clear filtered_coords

    houseCoor = returnCoor(houseAddress)
    if not houseCoor:
        messagebox.showerror("Error", "Invalid house address.")
        return

    for i in range(0, len(coord_list), batch_size):
        batch_coords = coord_list[i:i + batch_size]
        batch_addresses = address_list[i:i + batch_size]
        batch_ids = id_list[i:i + batch_size]
        batch_names = name_list[i:i + batch_size]

        for j in range(len(batch_addresses)):
            try:
                # Parse the coordinate string into a tuple of floats
                addressCoor = tuple(map(float, batch_coords[j].split(',')))
                if addressCoor:
                    distance = geodesic(houseCoor, addressCoor).miles
                    if distance < max_distance:
                        filtered_addresses.append(batch_addresses[j])
                        filtered_id.append(batch_ids[j])
                        filtered_names.append(batch_names[j])
                        filtered_coords.append(addressCoor)
                
            except Exception as e:
                print(f"Error processing address '{batch_addresses[j]}': {e}")

            # Optional: Add a delay after processing each batch
            time.sleep(0.1)  # Adjust the sleep time as needed

    if not filtered_addresses:
        messagebox.showinfo("Info", "No nearby addresses found.")

# Function to generate and display the map
def mapFunc():
    houseAddress = answer1.get()
    findNearbyAddresses(houseAddress, 0.5)

    if not filtered_coords:
        messagebox.showinfo("Info", "No nearby addresses found.")
        return

    # Initialize the map centered on the house address
    m = folium.Map(location=returnCoor(houseAddress), zoom_start=13)
    folium.Marker(returnCoor(houseAddress), popup=houseAddress, icon=folium.Icon(color="red", icon="home")).add_to(m)

    # Add markers for nearby addresses
    for i in range(len(filtered_addresses)):
        coord = filtered_coords[i]
        folium.Marker(
            location=coord,
            popup=f"{filtered_names[i]}\nStudent ID: {filtered_id[i]}"
        ).add_to(m)

    # Save or display the map
    m.save("map.html")
    webbrowser.open("map.html")
    """for i in range(len(filtered_addresses)):
        folium.Marker(filtered_coords[i]),
        popup=f"{filtered_names[i]}\nStudent ID: {filtered_id[i]}").add_to(m)"""

# Function to display the list of nearby houses
def listWindow():
    houseAddress = answer1.get()
    findNearbyAddresses(houseAddress, 0.5)

    if not filtered_addresses:
        messagebox.showinfo("Info", "No nearby addresses found.")
        return

    window2 = tk.Toplevel(window)
    window2.title("List of Houses")
    window2.geometry("900x800")
    window2.configure(bg="lightgrey")

    tk.Label(window2, text="Houses near you:", font=("Arial", 23), bg="lightgrey", fg="black").pack(pady=20)
    tk.Label(window2, text="\n".join(filtered_addresses), font=("Arial", 12), bg="lightgrey", fg="black").pack(pady=20)
    tk.Label(window2, text="People near you:", font=("Arial", 23), bg="lightgrey", fg="black").pack(pady=20)
    tk.Label(window2, text="\n".join(filtered_names), font=("Arial", 12), bg="lightgrey", fg="black").pack(pady=20)

def logintest():
    #usernames=getColumn('Student Name')
    #ids = getColumn('Student ID')
    loginuser=userName.get()
    loginID=userid.get()
    for i in range(0,len(name_list)):
        if name_list[i]==loginuser and id_list[i]==loginID:
                global login
                login="splendid"

        else:
                global error
                error="true"

    if error == "true" and login != "splendid":
        messagebox.showerror("Login Invalid","Please check your credentials and try again")

    if login == "splendid":
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
        tk.Button(window, text="Open Map in New Window", font=("Times New Roman", 24), bg="green", fg="white", command=mapFunc).pack(pady=20)
        tk.Button(window, text="Open List of Houses", font=("Times New Roman", 24), bg="red", fg="white", command=listWindow).pack(pady=20)
        

        print(coordinate_cache)


# UI elements



welcome = tk.Label(loginWindow,text="Welcome!", font=("Arial",23),bg="lightgrey",fg="black")
welcome.pack(pady=20)

name = tk.Label(loginWindow,text="Registered Name:", font=("Arial",23),bg="lightgrey",fg="black")
name.pack(pady=20)

userName = tk.Entry(loginWindow,font=("Arial",23),bg="lightgrey",fg="black")
userName.pack(pady=20)

id = tk.Label(loginWindow,text="Student ID:", font=("Arial",23),bg="lightgrey",fg="black")
id.pack(pady=20)

userid = tk.Entry(loginWindow,font=("Arial",23),bg="lightgrey",fg="black")
userid.pack(pady=20)

enterButton = tk.Button(loginWindow,text="Submit",font=("Arial",23),bg="lightgrey",fg="lightgreen",command=logintest)
enterButton.pack()
"""
if login == "splendid":
    loginWindow.quit()
    window = tk.Tk()
    window.title("Carpool Finder Application")
    window.geometry("900x800")
    window.configure(bg="lightgrey")

    title = tk.Label(window, text="Carpool Finder", font=("Arial", 40), bg="white", fg="red")
    title.pack(pady=10)

    tk.Label(window, text="Where is your house?", font=("Arial", 20), bg="white", fg="black").pack(pady=40)

    answer1 = tk.Entry(window, width=15, font=("Times New Roman", 24), bg="lightgrey", fg="red")
    answer1.pack(pady=20)

    tk.Button(window, text="Open Map in New Window", font=("Times New Roman", 24), bg="green", fg="white", command=mapFunc).pack(pady=20)
    tk.Button(window, text="Open List of Houses", font=("Times New Roman", 24), bg="red", fg="white", command=listWindow).pack(pady=20)

    print(coordinate_cache)"""

# Run the application
loginWindow.mainloop()
