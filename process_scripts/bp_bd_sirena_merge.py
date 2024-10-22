import pandas as pd
import json

# Load the Excel file
excel_file_path = 'path_to_excel_file.xlsx'  # Replace with your actual Excel file path
df = pd.read_excel(excel_file_path)

# Load the JSON file
with open('path_to_json_file.json', 'r', encoding='utf-8') as f:  # Replace with your JSON file path
    json_data = json.load(f)

# Normalize Excel data to ensure correct format
df['FirstName+LastName'] = df['FirstName+LastName'].str.strip()
df['TicketNumber'] = df['TicketNumber'].astype(str)
df['BookingCode'] = df['BookingCode'].astype(str)

# Create a lookup dictionary for JSON flights: {(BookingCode, TicketNumber): (travel_doc, flight)}
flight_lookup = {}

for travel_doc, details in json_data.items():
    for flight in details['Flights']:
        booking_code = flight.get('BookingCode', None)
        ticket_number = flight.get('TicketNumber', "Not presented")
        
        # Store the reference to the flight entry in the lookup dictionary
        flight_lookup[(booking_code, ticket_number)] = (travel_doc, flight)

# Prepare to track non-matching data
mismatch_data = []

# Progress counter
total_rows = len(df)
processed_count = 0

# Iterate through the Excel rows
for index, row in df.iterrows():
    flight_number = row['FlightNumber']
    booking_code = row['BookingCode']
    ticket_number = row['TicketNumber']
    full_name = row['FirstName+LastName']
    bonus_programm = row['BonusProgramm']

    matched = False

    processed_count += 1
    if processed_count % 10 == 0:
        print(f"Processed {processed_count}/{total_rows} rows")

    # Check for an exact match on (BookingCode, TicketNumber)
    if (booking_code, ticket_number) in flight_lookup:
        travel_doc, flight = flight_lookup[(booking_code, ticket_number)]
        details = json_data[travel_doc]
        details['PassengerDetails'].setdefault('FullName+LastName', []).append(full_name)
        if pd.notna(bonus_programm):
            current_bonus_programm = details['PassengerDetails'].get('BonusProgramm', '')
            if not isinstance(current_bonus_programm, str) or pd.isna(current_bonus_programm):
                current_bonus_programm = ''  # Reset to an empty string if NaN or not a string
            details['PassengerDetails']['BonusProgramm'] = current_bonus_programm + ', ' + bonus_programm if current_bonus_programm else bonus_programm
        matched = True

    # If no match with both BookingCode and TicketNumber, try matching just BookingCode
    elif (booking_code, "Not presented") in flight_lookup:
        travel_doc, flight = flight_lookup[(booking_code, "Not presented")]
        details = json_data[travel_doc]
        flight['TicketNumber'] = ticket_number  # Add the missing TicketNumber
        details['PassengerDetails'].setdefault('FullName+LastName', []).append(full_name)
        if pd.notna(bonus_programm):
            current_bonus_programm = details['PassengerDetails'].get('BonusProgramm', '')
            if not isinstance(current_bonus_programm, str) or pd.isna(current_bonus_programm):
                current_bonus_programm = ''  # Reset to an empty string if NaN or not a string
            details['PassengerDetails']['BonusProgramm'] = current_bonus_programm + ', ' + bonus_programm if current_bonus_programm else bonus_programm
        matched = True

    # If no match found, log this as a mismatch
    if not matched:
        mismatch_data.append({
            'FlightNumber': flight_number,
            'BookingCode': booking_code,
            'TicketNumber': ticket_number,
            'FirstName+LastName': full_name,
            'BonusProgramm': bonus_programm
        })

# Write updated JSON back to file
with open('path_to_updated_json_file.json', 'w', encoding='utf-8') as f:  # Replace with the desired output path
    json.dump(json_data, f, indent=4)

# Write mismatch data to a separate file for review
if mismatch_data:
    mismatch_df = pd.DataFrame(mismatch_data)
    mismatch_df.to_csv('mismatch_file.csv', index=False)  # Replace with the desired output CSV path

print("JSON update complete. Mismatched entries logged to a separate file.")
