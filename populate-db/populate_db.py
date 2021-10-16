import requests
import random
from datetime import timedelta, date
from faker import Faker
import pandas as pd
from collections import defaultdict
from sqlalchemy import create_engine
import urllib.parse
import pymysql

BASE_API_URL = 'http://localhost:4000/'

faker = Faker('pl_PL')

registered_users = []

def register_user():
    endpoint = 'auth/api/register'

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

            magazines_data['owner'].append(owner)
            magazines_data['start_date'].append(start_date)
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
            pass

    df_magazines_data = pd.DataFrame(magazines_data)

    engine = create_engine('mysql+pymysql://root:admin@localhost:3305/magazinedb', echo=False)

    df_magazines_data.to_sql('magazine', con=engine, if_exists='append', index=False)

    print('ADDED MAGAZINES')


if __name__ == '__main__':
    for _ in range(30):
        register_user()
    add_magazines(200)
        