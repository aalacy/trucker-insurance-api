import os
import shutil
import requests
import json
import argparse
import pdb
from datetime import datetime as date, timedelta
import sqlalchemy as db
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from coi import coi

BASE_PATH = os.path.abspath(os.curdir)
config_path = BASE_PATH + '/config/config.json'

# dotId = 2732221 # test data
# name = 'Test'
# address = 'test'

engine = create_engine('mysql+mysqlconnector://root:12345678@localhost:3306/luckytruck')
connection = engine.connect()

session = requests.Session()

def _escape(val):
    if val:
        return val.replace('###*###', "'")
    else
        return val

def generate_pdf(data, args):
    pdf_output = os.path.abspath(os.curdir) + args.path
    with open(os.path.expanduser(pdf_output), "wb+") as output_file:
        shutil.copyfileobj(
            coi(name=_escape(args.name), address=_escape(args.address), policy=args.policy),
            output_file,
        )
    print("completed")

def read_sf(config, userId):
    # read sf info stored in db and check expired (1 hour)
    res = connection.execute('SELECT * FROM Users WHERE id={}'.format(userId))
    users = [dict(r) for r in res]
    user = None
    if len(users) > 0:
        user = users[0]
    # expired_time = date.strptime(user['sf_token_expired'], '%y-%d-%m %H:%M:%S')
    if user and user['sf_token_expired'] and user['sf_token_expired'] < date.now():
        return (user['sf_token'], user['sf_instance_url'])
    else:
        headers = { 'Content-Type': 'application/'}
        # SF token for COI
        print('[*] Retrieve the access token from SF [*]')
        url = 'https://{}.salesforce.com/services/oauth2/token?grant_type=password&client_id={}&client_secret={}&username={}&password={}'.format(config['sf_server'], config['sf_client_id'], config['sf_client_secret'], config['sf_username'], config['sf_password'])
        res = session.post(url, headers=headers)
        if res.status_code == 200:
            data = res.json()
            expired_time = (date.now() + timedelta(hours=9)).strftime('%y-%d-%m %H:%M:%S')
            connection.execute("UPDATE users SET sf_token='{}', sf_token_expired='{}', sf_instance_url='{}' WHERE id={}".format(data['access_token'], expired_time, data['instance_url'], userId))
            return (data['access_token'], data['instance_url'])
        else:
            return (None, None)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--policy', type=str, required=False, help="policy json")
    parser.add_argument('-n', '--name', type=str, required=False, help="name")
    parser.add_argument('-a', '--address', type=str, required=False, help="address")
    parser.add_argument('-d', '--dotId', type=str, required=False, help="US DOT ID")
    parser.add_argument('-u', '--userId', type=str, required=False, help="User ID")
    parser.add_argument('-p', '--path', type=str, required=False, help="path")

    args = parser.parse_args()

    if args.dotId:
    	# load json config file
        config_data = {}
        with open(config_path, "r") as read_file:
            config_data = json.load(read_file)

        config = config_data['development']
        access_token, instance_url = read_sf(config, args.userId)
      
        if access_token and instance_url:
            # retrieve the coi data
            headers = { 'Content-Type': 'application/'}
            headers['Authorization'] = 'Bearer {}'.format(access_token)
            instance_url = '{}/services/apexrest/account/policy?dotId={}'.format(instance_url, args.dotId)
            res = session.get(instance_url, headers=headers)
            print('[*] Retrieve the data from SF [*]')
            if res.status_code == 200:
                data = res.json()
                # update sf token
                generate_pdf(data, args)
            else:
                print("something wrong with salesforce policy url")
        else:
            print("something wrong with salesforce access_token url")
    else:
        generate_pdf({}, args)
