import hashlib

import psycopg2
import requests


def combined_generator():
    while s := (yield 'Send 1 for weather, 2 for MD5, or None to exit'):
        if s == 1:
            yield from city_generator()
        elif s == 2:  # noqa: PLR2004
            yield from md5_generator()
        else:
            output = 'Unknown choice; try again'
            return output


def people_api():
    conn = psycopg2.connect('dbname=test')
    output = 'Send a query, or None to quit'

    while d := (yield output):
        cur = conn.cursor()
        query = """SELECT id, first_name, last_name, birthdate, gender FROM people"""
        args = ()

        for field in ['first_name', 'last_name', 'birthdate', 'gender']:
            if field in d:
                query += f' WHERE {field} = %s '
                args += (d[field],)

        print(query)

        cur.execute(query, args)

        yield from cur.fetchall()


# people_api


"""
>>> g = people_api()
>>> next(g)
'Send a query, or None to quit'
>>> g.send({'last_name': 'John'})
SELECT ...
(1, ...)
>>> g.send('whatever')
'Send a query, or None to quit'
>>> g.send({'last_name': 'Joh2n'})
SELECT ...
(2, ...)
"""


class DifferentCityException(Exception):  # noqa: N818
    pass


def city_generator():
    while city_id := (yield 'Send a city number or None'):
        weather = requests.get(  # noqa: S113
            f'https://worldweather.wmo.int/en/json/{city_id}_en.json',
        ).json()

        try:
            yield from weather['city']['forecast']['forecastDay']
        except DifferentCityException:
            continue


"""
>>> g = get_forecasts()
>>> next(g)
'Send a city number or None'
>>> g.send(44)
{...}
>>> g.send(44)
{...}
>>> g.throw(DifferentCityException)
'Send a city number or None'
"""


def md5_generator():
    output = 'Enter test to hash, or None'

    while s := (yield output):
        m = hashlib.md5()  # noqa: S324
        m.update(s.encode('utf-8'))
        output = m.hexdigest()
