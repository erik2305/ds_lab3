from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['airlines']

old_collection = db['SkyTeam_Exchange']
new_collection = db['user_flights']

def transform_data(flight_data):
    return {
        'FlightNumber': flight_data.get('flight'),
        'DepartDate': flight_data.get('date'),
        'TrvCls': flight_data.get('FF', {}).get('CLASS'),
        'DepartCode': flight_data.get('FROM'),
        'ArrivalCode': flight_data.get('TO')
    }

for flight in old_collection.find():
    card_num = flight.get('FF', {}).get('card')

    if card_num:
        existing_record = new_collection.find_one({
            'BonusProgram': {
                '$elemMatch': {'CardNumber': card_num}
            }
        })

        new_flight = transform_data(flight)

        if existing_record:
            print("found existing")
            new_collection.update_one(
                {'BonusProgram.CardNumber': card_num},
                {'$push': {'Flights': new_flight}}
            )
        else:
            new_object = {
                'FirstName': None,
                'LastName': None,
                'BonusProgram': [{
                    'Status': None,
                    'CardNumber': card_num
                }],
                'Flights': [new_flight]
            }
            new_collection.insert_one(new_object)

client.close()
