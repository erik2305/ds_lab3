import pandas as pd
import json
import re


file_path = 'cleaned_boarding_data.xlsx'  
df = pd.read_excel(file_path)

second_name_full_map = {}

def populate_full_names(df):
    for _, row in df.iterrows():
        second_name = row['SecondName']
        travel_doc = row['TravelDoc']
        if not re.match(r'^[A-Z]\.$', second_name):
            second_name_full_map[travel_doc] = second_name

def normalize_second_name(row):
    second_name = row['SecondName']
    travel_doc = row['TravelDoc']
    
    if re.match(r'^[A-Z]\.$', second_name):
        first_letter = second_name[0]
        
        if travel_doc in second_name_full_map:
            full_name = second_name_full_map[travel_doc]
            if full_name.startswith(first_letter):
                return full_name
        else:
            print(f"Problem with SecondName for TravelDoc {travel_doc}: No full name found for initial '{second_name}'")
        
        return second_name
    else:
        return second_name

populate_full_names(df)

df['SecondName'] = df.apply(normalize_second_name, axis=1)


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

flight_data = {}

for _, row in df.iterrows():
    travel_doc = row['TravelDoc']
    
    if travel_doc not in flight_data:
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

    flight_data[travel_doc]['Flights'].append(row_to_flight_data(row))

json_output = json.dumps(flight_data, indent=4, default=str)

output_file = 'cleaned_boarding_data.json'
with open(output_file, 'w') as f:
    f.write(json_output)

print(f"JSON data has been saved to {output_file}")