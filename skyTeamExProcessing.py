from pymongo import MongoClient
import re

client = MongoClient('mongodb://localhost:27017/')
db = client['airlines']
collection = db['SkyTeam_Exchange']

date_pattern = re.compile(r"^'(\d{4}-\d{2}-\d{2})':")
flight_pattern = re.compile(r"^(\w+\d+):")
card_pattern = re.compile(r"^(\w+ \d+): \{CLASS: (\w), FARE: (\w+)\}")
field_pattern = re.compile(r"^(FROM|STATUS|TO): (\w+)")


def insert_into_db(data):
    collection.insert_one(data)


def process_file(filename):
    current_date = None
    current_flight = None
    current_ff = {}
    flight_data = {}

    with open(filename, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            # Поиск даты
            date_match = date_pattern.match(line)
            if date_match:
                # Если новая дата, сохраняем предыдущие данные
                if current_flight:
                    flight_data['FF'] = current_ff
                    insert_into_db(flight_data)
                    current_ff = {}
                    flight_data = {}

                # Обновляем дату
                current_date = date_match.group(1)
                continue

            # Поиск номера рейса
            flight_match = flight_pattern.match(line)
            if flight_match:
                if current_flight:
                    flight_data['FF'] = current_ff
                    insert_into_db(flight_data)
                    current_ff = {}
                    flight_data = {}

                # Обновляем номер рейса
                current_flight = flight_match.group(1)
                flight_data = {
                    'date': current_date,
                    'flight': current_flight
                }
                continue

            # Поиск карты и информации о FF
            card_match = card_pattern.match(line)
            if card_match:
                card, flight_class, fare = card_match.groups()
                current_ff = {
                    'card': card,
                    'CLASS': flight_class,
                    'FARE': fare
                }
                continue

            # Поиск полей FROM, STATUS и TO
            field_match = field_pattern.match(line)
            if field_match:
                field, value = field_match.groups()
                flight_data[field] = value

        # Вставка последнего блока данных
        if current_flight:
            flight_data['FF'] = current_ff
            insert_into_db(flight_data)


process_file("SkyTeam-Exchange.yaml")
