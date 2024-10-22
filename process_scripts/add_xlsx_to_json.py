import pandas as pd
from pandas import Timestamp
from datetime import time
import json

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Timestamp):
            return obj.strftime('%d/%m/%Y')
        if isinstance(obj, time):
            return obj.strftime('%H:%M')
        return super().default(obj)

json_file_path = 'cleaned_boarding_data.json'
with open(json_file_path, 'r') as f:
    flights_data = json.load(f)

second_table_path = 'Sirena-export-fixed.xlsx'
df_second_table = pd.read_excel(second_table_path, dtype={'e-Ticket': str})

def update_flights_data(row, flights_data):
    travel_doc = row['TravelDoc']
    
    if travel_doc in flights_data:
        if 'FullName(rus)' not in flights_data[travel_doc]['PassengerDetails']:
            flights_data[travel_doc]['PassengerDetails']['FullName(rus)'] = row['FullName']
        
        if 'BonusProgramm' not in flights_data[travel_doc]['PassengerDetails']:
            flights_data[travel_doc]['PassengerDetails']['BonusProgramm'] = row.get('BonusProgramm', 'Not provided')

        flight_exists = False
        for flight in flights_data[travel_doc]['Flights']:
            if flight['FlightNumber'] == row['FlightNumber']:
                flight_exists = True

                if 'e-Ticket' not in flight:
                    flight['e-Ticket'] = str(row.get('e-Ticket', 'Not provided'))
                if 'Fare' not in flight:
                    flight['Fare'] = row.get('Fare', 'Not provided')

                if flight['BookingCode'] == "Not presented" and row['BookingCode'] != "Not presented":
                    flight['BookingCode'] = row['BookingCode']

                break
        
        if not flight_exists:
            new_flight = {
                'BookingCode': row['BookingCode'],
                'Baggage': row['Baggage'],
                'DepartDate': row['DepartDate'],
                'DepartTime': row['DepartTime'],
                'FlightNumber': row['FlightNumber'],
                'CodeShare': row['CodeShare'],
                'ArrivalCity': row.get('ArrivalCity', 'Unknown'),
                'e-Ticket': str(row.get('e-Ticket', 'Not provided')),
                'Fare': row['Fare']
            }
            if 'TicketNumber' in row:
                new_flight['TicketNumber'] = row['TicketNumber']
            flights_data[travel_doc]['Flights'].append(new_flight)

df_second_table.apply(update_flights_data, axis=1, flights_data=flights_data)

json_new_file = 'bd_and_sirena.json'
with open(json_new_file, 'w', encoding='utf-8') as f:
    json.dump(flights_data, f, indent=4, cls=CustomJSONEncoder, ensure_ascii=False)

print(f"Updated flights data saved to {json_new_file}")