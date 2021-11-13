import requests
import random
from datetime import timedelta, date
from faker import Faker
import pandas as pd
from collections import defaultdict
from sqlalchemy import create_engine
import urllib.parse
import pymysql
import os
import shutil
import time
import json
from json.decoder import JSONDecodeError

BASE_API_URL = 'http://localhost:4000/'

faker = Faker('pl_PL')

registered_users = []
added_magazines = []
added_reservations = []
added_reviews = []
added_reports = []
added_messages = []

def random_date(start, end):
    return start + timedelta(
        seconds=random.randint(0, int((end - start).total_seconds())),
    )


def register_user():
    endpoint = 'magazine/api/user'

    first_name = faker.first_name()
    last_name = faker.last_name()
    email = faker.email()
    password = faker.password()
    address = faker.current_country() + ' ' + faker.city() + ' ' + faker.street_name()
    phone_number = faker.phone_number()
    birth_date = random_date(date(1950, 1, 1), date(2003, 1, 1)).strftime("%Y-%m-%d")

    user_credentials = {
        'firstName': first_name,
        'lastName': last_name,
        'email': email,
        'password': password,
        'address': address,
        'phoneNumber': phone_number,
        'birthDate': birth_date
    }

    img_data = requests.get('https://thispersondoesnotexist.com/image').content
    os.makedirs(os.path.dirname(f'avatars/avatar.jpeg'), exist_ok=True)
    with open(f'avatars/avatar.jpeg', 'wb') as handler:
        handler.write(img_data)

    files = {"files": (f'{email}.jpeg', open(f'avatars/avatar.jpeg', "rb"), 'application-type')}

    session = requests.Session()
    response = session.post(BASE_API_URL + endpoint, data=user_credentials, files=files)

    if response.status_code >= 200 and response.status_code < 300:
        print(f'REGISTERED USER: {user_credentials}')
        registered_users.append(user_credentials)
    else:
        print(f'REGISTER USER RESPONSE: {response.status_code} {user_credentials}')

    shutil.rmtree('avatars')


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


def add_magazine(owner, city = None):
    endpoint = 'magazine/api/add'

    auth_token = login_user(owner['email'], owner['password'])

    country = faker.current_country()
    city = faker.city() if city == None else city
    street = faker.street_name()
    building = faker.building_number()

    titles = [
        'SUPER space to rent!',
        'CHEAP!!!',
        'Good location',
        'Perfect place for you',
        'Warm and bright space',
        'click and see!',
    ]

    title = random.choice(titles) + ' ' + street

    start_date = date.today() + timedelta(days=random.uniform(0, 10))
    end_date = start_date + timedelta(days=random.uniform(10, 100))

    min_area = round(random.uniform(5.5, 50.5), 2)
    area = min_area + round(random.uniform(30.5, 200.5), 2)

    magazine_data = {
        'title': title,
        'country': country,
        'city': city,
        'street': street,
        'building': building,
        'startDate': start_date,
        'endDate': end_date,
        'areaInMeters': area,
        'pricePerMeter': round(random.uniform(5.5, 20.5), 2),
        'type': random.choice(['GARAGE', 'WAREHOUSE', 'FLAT', 'CELL']),
        'heating': random.choice(['ELECTRIC', 'WATER', 'NONE']),
        'light': random.choice([True, False]),
        'whole': random.choice([True, False]),
        'monitoring': random.choice([True, False]),
        'antiTheftDoors': random.choice([True, False]),
        'ventilation': random.choice([True, False]),
        'smokeDetectors': random.choice([True, False]),
        'selfService': random.choice([True, False]),
        'floor': random.randint(-2, 20),
        'height': round(random.uniform(1.5, 20.5), 2),
        'doorHeight': round(random.uniform(1.5, 3.5), 2),
        'doorWidth': round(random.uniform(0.5, 3.5), 2),
        'electricity': random.choice([True, False]),
        'parking': random.choice([True, False]),
        'elevator': random.choice([True, False]),
        'vehicleManoeuvreArea': random.choice([True, False]),
        'minAreaToRent': min_area,
        'ownerTransport': random.choice([True, False]),
        'description': faker.paragraph(nb_sentences=random.uniform(3, 6)),
        'minTemperature': round(random.uniform(-10.5, 5.5), 1),
        'maxTemperature': round(random.uniform(6.5, 35.5), 1)
    }

    images_urls = [
        'https://www.thetrafalgargroup.co.uk/wp-content/uploads/2019/06/Office31_IMG.jpg',
        'https://sunizo.com/wp-content/uploads/2020/08/Lease-a-small-warehouse-space-1024x576.jpg',
        'https://upullit.jksalvageco.com/wp-content/uploads/2019/11/IMG_1490.jpg',
        'https://www.oldfield-smith.co.uk/wp-content/uploads/SAM_2796-1024x768.jpg',
        'https://photos.gilmartinley.co.uk/13829/13829-21610-102473-007-ss.jpg',
        'https://www.peerspace.com/resources/wp-content/uploads/Los-Angeles-Historic-Event-Center-la-rental-1178x600.jpg',
        'https://www.renderhub.com/renderhub/large-warehouse-space/large-warehouse-space-01.jpg',
        'https://static.carthrottle.com/workspace/uploads/posts/2016/03/924ee62bcd0949c5bfa5b7b2fdfa21c5.jpg'
    ]

    for i in range(1, 6):
        img_data = requests.get(random.choice(images_urls)).content
        os.makedirs(os.path.dirname(f'magazine_photos/magazine{i}.jpg'), exist_ok=True)
        with open(f'magazine_photos/magazine{i}.jpg', 'wb') as handler:
            handler.write(img_data)

    files = [
        ("files", (f'{country}{city}{street}{building}1.jpg', open(f'magazine_photos/magazine1.jpg', "rb"), 'application-type')),
        ("files", (f'{country}{city}{street}{building}2.jpg', open(f'magazine_photos/magazine2.jpg', "rb"), 'application-type')),
        ("files", (f'{country}{city}{street}{building}3.jpg', open(f'magazine_photos/magazine3.jpg', "rb"), 'application-type')),
        ("files", (f'{country}{city}{street}{building}4.jpg', open(f'magazine_photos/magazine4.jpg', "rb"), 'application-type')),
        ("files", (f'{country}{city}{street}{building}5.jpg', open(f'magazine_photos/magazine5.jpg', "rb"), 'application-type'))
    ]

    headers = {'authorization': f'Bearer {auth_token}'}

    session = requests.Session()
    response = session.post(BASE_API_URL + endpoint, data=magazine_data, files=files, headers=headers)

    if response.status_code >= 200 and response.status_code < 300:
        print(f'ADDED MAGAZINE: {magazine_data}')
        magazine_data['id'] = json.loads(response.text)['id']
        magazine_data['owner_id'] = owner['email']
        added_magazines.append(magazine_data)
        time.sleep(2) # it needs to stay here because free version of locationIq only allows requests every 2 secs
    else:
        print(f'ADD MAGAZINE RESPONSE: {response.status_code} {magazine_data}')

    shutil.rmtree('magazine_photos')


def add_reservation(magazine, user, area, start_date, end_date):
    endpoint = 'magazine/api/reservation/add'

    auth_token = login_user(user['email'], user['password'])

    reservation_data = {
        'areaInMeters': area,
        'startDate': date.strftime(start_date, "%Y-%m-%d"),
        'endDate': date.strftime(end_date, "%Y-%m-%d"),
        'magazineId': magazine['id']
    }

    headers = {'authorization': f'Bearer {auth_token}'}
    response = requests.post(BASE_API_URL + endpoint, json=reservation_data, headers=headers)

    if response.status_code >= 200 and response.status_code < 300:
        print(f'ADDED RESERVATION: {reservation_data}')
        reservation_data['id'] = json.loads(response.text)['id']
        reservation_data['user_id'] = user['email']
        added_reservations.append(reservation_data)
    else:
        print(f'ADD RESERVATION_RESPONSE: {response.status_code} {reservation_data}')


def add_reservations(quantity):
    for _ in range(quantity):
        magazine = random.choice(added_magazines)
        user = random.choice(registered_users)
        area = round(random.uniform(magazine['minAreaToRent'], magazine['areaInMeters']), 1)
        start_date = random_date(magazine['startDate'], magazine['endDate'])
        end_date = random_date(start_date, magazine['endDate'])

        add_reservation(magazine, user, area, start_date, end_date)


if __name__ == '__main__':
    for _ in range(70):
        register_user()
    for _ in range(30):
        user = random.choice(registered_users)
        add_magazine(user)
    for _ in range(20):
        user = random.choice(registered_users)
        add_magazine(user, 'Kraków')
    add_reservations(100)
        
        
# def add_magazines(number):
#     magazines_data = defaultdict(list)

#     for _ in range(number):
#         owner = random.choice(registered_users)['email']
#         start_date = date.today() + timedelta(days=random.uniform(0, 10))
#         end_date = start_date + timedelta(days=random.uniform(10, 100))
#         min_area = round(random.uniform(5.5, 50.5), 2)
#         area = min_area + round(random.uniform(30.5, 200.5), 2)
#         country = faker.current_country()
#         city = faker.city()
#         street = faker.street_name()
#         building = faker.building_number()

#         address = f'{country} {city} {street} {building}'
#         url = 'https://nominatim.openstreetmap.org/search/' + urllib.parse.quote(address) +'?format=json'

#         try:
#             response = requests.get(url).json()

#             latitude = response[0]["lat"]
#             longitude = response[0]["lon"]

#             magazines_data['owner_id'].append(owner)
#             magazines_data['start_date'].append(start_date)
#             magazines_data['title'].append('Test magazine')
#             magazines_data['end_date'].append(end_date)
#             magazines_data['min_area_to_rent'].append(min_area)
#             magazines_data['area_in_meters'].append(area)
#             magazines_data['price_per_meter'].append(round(random.uniform(5.5, 20.5), 2))
#             magazines_data['country'].append(country)
#             magazines_data['city'].append(city)
#             magazines_data['street'].append(street)
#             magazines_data['building'].append(building)
#             magazines_data['longitude'].append(longitude)
#             magazines_data['latitude'].append(latitude)
#             magazines_data['type'].append(random.choice([None, 'GARAGE', 'WAREHOUSE', 'FLAT', 'CELL']))
#             magazines_data['heating'].append(random.choice([None, 'ELECTRIC', 'WATER', 'NONE']))
#             magazines_data['light'].append(random.choice([None, 'DARK', 'NATURAL', 'NOT_NATURAL']))
#             magazines_data['whole'].append(random.choice([None, True, False]))
#             magazines_data['monitoring'].append(random.choice([None, True, False]))
#             magazines_data['anti_theft_doors'].append(random.choice([None, True, False]))
#             magazines_data['ventilation'].append(random.choice([None, True, False]))
#             magazines_data['smoke_detectors'].append(random.choice([None, True, False]))
#             magazines_data['self_service'].append(random.choice([None, True, False]))
#             magazines_data['floor'].append(random.uniform(-2, 20))
#             magazines_data['height'].append(round(random.uniform(1.5, 20.5), 2))
#             magazines_data['door_height'].append(round(random.uniform(1.5, 3.5), 2))
#             magazines_data['door_width'].append(round(random.uniform(0.5, 3.5), 2))
#             magazines_data['electricity'].append(random.choice([None, True, False]))
#             magazines_data['parking'].append(random.choice([None, True, False]))
#             magazines_data['vehicle_manoeuvre_area'].append(random.choice([None, True, False]))
#             magazines_data['owner_transport'].append(random.choice([None, True, False]))
#             magazines_data['description'].append(faker.paragraph(nb_sentences=random.uniform(1, 4)))

#             print('LOADED MAGAZINE TO ADD...')
#         except IndexError:
#             print("IndexError: Could not get magazine geolocation. Skipping...")
#             pass
#         except JSONDecodeError:
#             print("JSONDecodeError: Could not get magazine geolocation. Skipping...")
#             pass

#     df_magazines_data = pd.DataFrame(magazines_data)

#     engine = create_engine('mysql+pymysql://root:admin@localhost:3305/magazinedb', echo=False)

#     df_magazines_data.to_sql('magazine', con=engine, if_exists='append', index=False)

#     print('ADDED MAGAZINES')