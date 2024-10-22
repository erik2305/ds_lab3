import pandas as pd
import json
import re

# Load the xlsx file into a DataFrame
file_path = 'cleaned_boarding_data.xlsx'  # Replace with the path to your file
df = pd.read_excel(file_path)

# Dictionary to store full second names for each person (indexed by TravelDoc)
second_name_full_map = {}

# Function to populate the second_name_full_map with full names
def populate_full_names(df):
    for _, row in df.iterrows():
        second_name = row['SecondName']
        travel_doc = row['TravelDoc']
        # If SecondName is not an initial (e.g., M.), store it
        if not re.match(r'^[A-Z]\.$', second_name):
            second_name_full_map[travel_doc] = second_name

# Function to normalize SecondName after the full dataset has been processed
def normalize_second_name(row):
    second_name = row['SecondName']
    travel_doc = row['TravelDoc']
    
    # Check if second_name is just a first letter followed by a period (e.g., M.)
    if re.match(r'^[A-Z]\.$', second_name):
        first_letter = second_name[0]
        
        # Try to find a full name that starts with the same letter for the same person (TravelDoc)
        if travel_doc in second_name_full_map:
            full_name = second_name_full_map[travel_doc]
            if full_name.startswith(first_letter):
                return full_name
        else:
            # Log the TravelDoc where no full name is found in the map
            print(f"Problem with SecondName for TravelDoc {travel_doc}: No full name found for initial '{second_name}'")
        
        # If no full name is found, return the initial (unchanged)
        return second_name
    else:
        return second_name

# First pass: Populate the second_name_full_map with the full second names
populate_full_names(df)

# Second pass: Apply the normalization function to the DataFrame
df['SecondName'] = df.apply(normalize_second_name, axis=1)

# Function to convert DataFrame row to a dictionary (for flight details, excluding personal info)
def row_to_flight_data(row):
    return {
        'BookingCode': row['BookingCode'],
        'TicketNumber': row['TicketNumber'],
        'Baggage': row['Baggage'],
        'DepartDate': row['DepartDate'],
        'DepartTime': row['DepartTime'],
        'FlightNumber': row['FlightNumber'],
        'CodeShare': row['CodeShare'],
        'ArrivalCity': row['ArrivalCity']
    }

# Create the JSON structure with TravelDoc as the top-level key
flight_data = {}

for _, row in df.iterrows():
    travel_doc = row['TravelDoc']
    
    if travel_doc not in flight_data:
        # Add PassengerDetails when processing a TravelDoc for the first time
        flight_data[travel_doc] = {
            'PassengerDetails': {
                'FirstName': row['FirstName'],
                'SecondName': row['SecondName'],
                'LastName': row['LastName'],
                'PassengerSex': row['PassengerSex'],
                'PassengerBirthDate': row['PassengerBirthDate']
            },
            'Flights': []
        }

    # Append the flight data (excluding personal info) to the Flights list
    flight_data[travel_doc]['Flights'].append(row_to_flight_data(row))

# Convert the dictionary to JSON
json_output = json.dumps(flight_data, indent=4, default=str)

# Save the JSON output to a file
output_file = 'cleaned_boarding_data.json'
with open(output_file, 'w') as f:
    f.write(json_output)

print(f"JSON data has been saved to {output_file}")