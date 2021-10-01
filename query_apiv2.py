#!/usr/bin/env python3

"""
Only tested in Python 3.
You may need to install the 'requests' Python3 module.
"""

import argparse
import os 
import requests


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--username', help="Your WattTime username", default="YOUR USERNAME HERE")
    parser.add_argument(
        '--password', help="Your WattTime password, or set variable WATTTIME_PASS in your env", required=False
    )
    parser.add_argument('--email', help="Your WattTime email address", default="some_email@gmail.com")
    parser.add_argument('--org', help="Your WattTime org", default="some org name")
    parser.add_argument('--region', help="Your grid reguion", default="CAISO_ZP26")
    parser.add_argument('--start', help="Start Time, UTC offset of 0", default="'2020-03-01T00:00:00-0000'")
    parser.add_argument('--end', help="End Time, UTC offset of 0", default="2020-03-01T00:45:00-0000")

    return parser.parse_args()


def register(username, password, email, org):
    url = 'https://api2.watttime.org/register'
    params = {
        'username': username, 'password': password, 'email': email, 'org': org
    }
    rsp = requests.post(url, json=params)
    print(rsp.text)


def login(username, password):
    url = 'https://api2.watttime.org/login'
    try:
        rsp = requests.get(url, auth=requests.auth.HTTPBasicAuth(username, password))
    except BaseException as e:
        print('There was an error making your login request: {}'.format(e))
        return None

    try:
        token = rsp.json()['token']
    except BaseException:
        print('There was an error logging in. The message returned from the '
              'api is {}'.format(rsp.text))
        return None

    return token


def data(token, ba, starttime, endtime):
    url = 'https://api2.watttime.org/data'
    headers = {'Authorization': 'Bearer {}'.format(token)}
    params = {'ba': ba, 'starttime': starttime, 'endtime': endtime}

    rsp = requests.get(url, headers=headers, params=params)
    # print(rsp.text)  # uncomment to see raw response
    return rsp.json()


def index(token, ba):
    url = 'https://api2.watttime.org/index'
    headers = {'Authorization': 'Bearer {}'.format(token)}
    params = {'ba': ba}

    rsp = requests.get(url, headers=headers, params=params)
    # print(rsp.text)  # uncomment to see raw response
    return rsp.json()


def forecast(token, ba, starttime=None, endtime=None):
    url = 'https://api2.watttime.org/forecast'
    headers = {'Authorization': 'Bearer {}'.format(token)}
    params = {'ba': ba}
    if starttime:
        params.update({'starttime': starttime, 'endtime': endtime})

    rsp = requests.get(url, headers=headers, params=params)
    # print(rsp.text)  # uncomment to see raw response
    return rsp.json()


def historical(token, ba):
    url = 'https://api2.watttime.org/historical'
    headers = {'Authorization': 'Bearer {}'.format(token)}
    params = {'ba': ba}
    rsp = requests.get(url, headers=headers, params=params)
    cur_dir = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(cur_dir, '{}_historical.zip'.format(ba))
    with open(file_path, 'wb') as fp:
        fp.write(rsp.content)

    print('Wrote historical data for {} to {}'.format(ba, file_path))


# Only register once!!
# register(USERNAME, PASSWORD, EMAIL, ORG)
if __name__ == "__main__":
    args = parse_args()

    token = login(args.username, args.password or os.getenv("WATTTIME_PASS"))
    if not token:
        print('You will need to fix your login credentials (username and password '
            'at the start of this file) before you can query other endpoints. '
            'Make sure that you have registered at least once by uncommenting '
            'the register(username, password, email, org) line near the bottom '
            'of this file.')
        exit()

    realtime_index = index(token, args.region)
    print(realtime_index)

    print('Please note: the following endpoints require a WattTime subscription')
    historical_moer = data(token, args.region, args.start, args.end)
    print(historical_moer)

    forecast_moer = forecast(token, args.region)
    print(forecast_moer)

    forecast_moer = forecast(token, args.region, args.start, args.end)
    print(forecast_moer)

    historical(token, args.region)  # Writes zip file to current ditectory
