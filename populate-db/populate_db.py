import requests
import random
from datetime import timedelta, date
from faker import Faker
import pandas as pd
from collections import defaultdict
from sqlalchemy import create_engine
import urllib.parse
import pymysql
from json.decoder import JSONDecodeError
import sys

BASE_API_URL = 'http://localhost:4000/'

engine = create_engine('mysql+pymysql://root:admin@localhost:3305/magazinedb', echo=False)

faker = Faker('pl_PL')

registered_users = []

argv = sys.argv[1:]


def register_user():
    endpoint = 'magazine/api/user'

    first_name = faker.first_name()
    last_name = faker.last_name()
    email = faker.email()
    password = faker.password()

    user_credentials = {
        'firstName': first_name,
        'lastName': last_name,
        'email': email,
        'password': password
    }

    response = requests.post(BASE_API_URL + endpoint, json=user_credentials)

    if response.status_code >= 200 and response.status_code < 300:
        print(f'REGISTERED USER: {user_credentials}')
        registered_users.append(user_credentials)
    else:
        print(f'REGISTER USER RESPONSE: {response.status_code} {user_credentials}')


def login_user(email, password):
    endpoint = 'auth/api/login'

    user_credentials = {
        'email': email,
        'password': password
    }

    response = requests.post(BASE_API_URL + endpoint, json=user_credentials)

    if response.status_code >= 200 and response.status_code < 300:
        return response.json()['token']
    else:
        print(f'LOGIN USER RESPONSE: {response.status_code} ({user_credentials})')


def add_magazines(number):
    magazines_data = defaultdict(list)

    for _ in range(number):
        owner = random.choice(registered_users)['email']
        start_date = date.today() + timedelta(days=random.uniform(0, 10))
        end_date = start_date + timedelta(days=random.uniform(10, 100))
        min_area = round(random.uniform(5.5, 50.5), 2)
        area = min_area + round(random.uniform(30.5, 200.5), 2)
        country = faker.current_country()
        city = faker.city()
        street = faker.street_name()
        building = faker.building_number()

        address = f'{country} {city} {street} {building}'
        url = 'https://nominatim.openstreetmap.org/search/' + urllib.parse.quote(address) +'?format=json'

        try:
            response = requests.get(url).json()

            latitude = response[0]["lat"]
            longitude = response[0]["lon"]

            magazines_data['owner_id'].append(owner)
            magazines_data['start_date'].append(start_date)
            magazines_data['title'].append('Test magazine')
            magazines_data['end_date'].append(end_date)
            magazines_data['min_area_to_rent'].append(min_area)
            magazines_data['area_in_meters'].append(area)
            magazines_data['price_per_meter'].append(round(random.uniform(5.5, 20.5), 2))
            magazines_data['country'].append(country)
            magazines_data['city'].append(city)
            magazines_data['street'].append(street)
            magazines_data['building'].append(building)
            magazines_data['longitude'].append(longitude)
            magazines_data['latitude'].append(latitude)
            magazines_data['type'].append(random.choice([None, 'GARAGE', 'WAREHOUSE', 'FLAT', 'CELL']))
            magazines_data['heating'].append(random.choice([None, 'ELECTRIC', 'WATER', 'NONE']))
            magazines_data['light'].append(random.choice([None, 'DARK', 'NATURAL', 'NOT_NATURAL']))
            magazines_data['whole'].append(random.choice([None, True, False]))
            magazines_data['monitoring'].append(random.choice([None, True, False]))
            magazines_data['anti_theft_doors'].append(random.choice([None, True, False]))
            magazines_data['ventilation'].append(random.choice([None, True, False]))
            magazines_data['smoke_detectors'].append(random.choice([None, True, False]))
            magazines_data['self_service'].append(random.choice([None, True, False]))
            magazines_data['floor'].append(random.uniform(-2, 20))
            magazines_data['height'].append(round(random.uniform(1.5, 20.5), 2))
            magazines_data['door_height'].append(round(random.uniform(1.5, 3.5), 2))
            magazines_data['door_width'].append(round(random.uniform(0.5, 3.5), 2))
            magazines_data['electricity'].append(random.choice([None, True, False]))
            magazines_data['parking'].append(random.choice([None, True, False]))
            magazines_data['vehicle_manoeuvre_area'].append(random.choice([None, True, False]))
            magazines_data['owner_transport'].append(random.choice([None, True, False]))
            magazines_data['description'].append(faker.paragraph(nb_sentences=random.uniform(1, 4)))

            print('LOADED MAGAZINE TO ADD...')
        except IndexError:
            print("IndexError: Could not get magazine geolocation. Skipping...")
            pass
        except JSONDecodeError:
            print("JSONDecodeError: Could not get magazine geolocation. Skipping...")
            pass

    df_magazines_data = pd.DataFrame(magazines_data)

    df_magazines_data.to_sql('magazine', con=engine, if_exists='append', index=False)

    print('ADDED MAGAZINES')


def get_users_ids():
    return pd.read_sql("SELECT id FROM user", con=engine).values


def add_reservations(users_ids, magazine_ids, magazines_number):
    users_ids = get_users_ids()
    reservations_data = defaultdict(list)

    for i in range(magazines_number):
        id = i + 1
        area_in_meters = round(random.uniform(5.5, 15.5), 2)
        created_date = date.today()
        start_date = date.today() + timedelta(days=random.uniform(0, 2))
        end_date = start_date + timedelta(days=random.uniform(10, 100))
        updated_date = date.today()
        user_id = users_ids[round(random.uniform(0, len(users_ids) - 1))][0]
        magazine_id = round(random.uniform(1, magazine_ids - 1))

        try:
            reservations_data['id'].append(id)
            reservations_data['area_in_meters'].append(area_in_meters)
            reservations_data['created_date'].append(created_date)
            reservations_data['start_date'].append(start_date)
            reservations_data['end_date'].append(end_date)
            reservations_data['updated_date'].append(updated_date)
            reservations_data['user_id'].append(user_id)
            reservations_data['magazine_id'].append(magazine_id)

            print('LOADED RESERVATION TO ADD...')
        except IndexError:
            pass
        except JSONDecodeError:
            pass

    df_reservations_data = pd.DataFrame(reservations_data)

    df_reservations_data.to_sql('reservation', con=engine, if_exists='append', index=False)

    print('ADDED RESERVATIONS')

if __name__ == '__main__':
    for _ in range(int(argv[0])):
        register_user()
    add_magazines(int(argv[1]))
    add_reservations(int(argv[0]), int(argv[1]), int(argv[2]))
        