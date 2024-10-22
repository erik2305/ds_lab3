import pandas as pd
import json

# Load the Excel file
excel_file_path = 'Boarding_pass_merged.xlsx'
df = pd.read_excel(excel_file_path)

# Load the JSON file
with open('bd_and_sirena.json', 'r', encoding='utf-8') as f:
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

    # Print progress after processing each row
    processed_count += 1
    if processed_count % 10 == 0:  # Print progress for every 10 rows processed
        print(f"Processed {processed_count}/{total_rows} rows")

    # Check for an exact match on (BookingCode, TicketNumber)
    if (booking_code, ticket_number) in flight_lookup:
        travel_doc, flight = flight_lookup[(booking_code, ticket_number)]
        details = json_data[travel_doc]
        
        # Check if the full_name already exists in 'FullName+LastName' before appending
        if full_name not in details['PassengerDetails'].get('FullName+LastName', []):
            details['PassengerDetails'].setdefault('FullName+LastName', []).append(full_name)
        
        if pd.notna(bonus_programm):
            current_bonus_programm = details['PassengerDetails'].get('BonusProgramm', '')
            if not isinstance(current_bonus_programm, str) or pd.isna(current_bonus_programm):
                current_bonus_programm = ''  # Reset to an empty string if NaN or not a string
            details['PassengerDetails']['BonusProgramm'] = current_bonus_programm + ', ' + bonus_programm if current_bonus_programm else bonus_programm
        matched = True
        print(f"Matched BookingCode {booking_code} and TicketNumber {ticket_number}, updating JSON")

    # If no match with both BookingCode and TicketNumber, try matching just BookingCode
    elif (booking_code, "Not presented") in flight_lookup:
        travel_doc, flight = flight_lookup[(booking_code, "Not presented")]
        details = json_data[travel_doc]
        flight['TicketNumber'] = ticket_number  # Add the missing TicketNumber

        # Check if the full_name already exists in 'FullName+LastName' before appending
        if full_name not in details['PassengerDetails'].get('FullName+LastName', []):
            details['PassengerDetails'].setdefault('FullName+LastName', []).append(full_name)

        if pd.notna(bonus_programm):
            current_bonus_programm = details['PassengerDetails'].get('BonusProgramm', '')
            if not isinstance(current_bonus_programm, str) or pd.isna(current_bonus_programm):
                current_bonus_programm = ''  # Reset to an empty string if NaN or not a string
            details['PassengerDetails']['BonusProgramm'] = current_bonus_programm + ', ' + bonus_programm if current_bonus_programm else bonus_programm
        matched = True
        print(f"Matched BookingCode {booking_code}, added TicketNumber {ticket_number}, updating JSON")

    # If no match found, log this as a mismatch
    if not matched:
        mismatch_data.append({
            'FlightNumber': flight_number,
            'BookingCode': booking_code,
            'TicketNumber': ticket_number,
            'FirstName+LastName': full_name,
            'BonusProgramm': bonus_programm
        })
        print(f"No match found for Excel row with BookingCode {booking_code}, logging to mismatch data.")

# Write updated JSON back to file
with open('bp_bd_sirena_merge.json', 'w', encoding='utf-8') as f: 
    json.dump(json_data, f, indent=4, ensure_ascii=False)

# Write mismatch data to a separate file for review
if mismatch_data:
    mismatch_df = pd.DataFrame(mismatch_data)
    mismatch_df.to_csv('mismatch_file.csv', index=False)  # Replace with the desired output CSV path

print("JSON update complete. Mismatched entries logged to a separate file.")
