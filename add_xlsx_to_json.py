import pandas as pd
import json

json_file_path = 'cleaned_boarding_data.json'
with open(json_file_path, 'r') as f:
    flights_data = json.load(f)

second_table_path = 'Sirena-export-fixed.xlsx'
df_second_table = pd.read_excel(second_table_path)

def update_flights_data(row, flights_data):
    travel_doc = row['TravelDoc']
    
    if travel_doc in flights_data:
        if 'FullName(rus)' not in flights_data[travel_doc]['PassengerDetails']:
            flights_data[travel_doc]['PassengerDetails']['FullName(rus)'] = row['FullName']
        
        flight_exists = False
        for flight in flights_data[travel_doc]['Flights']:
            if row['BookingCode'] != "Not presented":
                if flight['BookingCode'] == row['BookingCode']:
                    flight_exists = True
                    break
            else:
                if flight['FlightNumber'] == row['FlightNumber']:
                    flight_exists = True
                    break
        
        if not flight_exists:
            new_flight = {
                'BookingCode': row['BookingCode'],
                'Baggage': row.get('Baggage', 'N/A'),
                'DepartDate': row['DepartDate'],
                'DepartTime': row['DepartTime'],
                'FlightNumber': row['FlightNumber'],
                'CodeShare': row.get('CodeShare', 'N/A'),
                'ArrivalCity': row['ArrivalCity']
            }
            if 'TicketNumber' in row:
                new_flight['TicketNumber'] = row['TicketNumber']
            flights_data[travel_doc]['Flights'].append(new_flight)
    else:
        print(f"TravelDoc {travel_doc} not found in JSON data.")

df_second_table.apply(update_flights_data, axis=1, flights_data=flights_data)

with open(json_file_path, 'w') as f:
    json.dump(flights_data, f, indent=4)

print(f"Updated flights data saved to {json_file_path}")
