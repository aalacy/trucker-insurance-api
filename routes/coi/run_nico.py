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
from dotenv import load_dotenv
from nico import nico

BASE_PATH = os.getcwd()
load_dotenv(os.path.join(BASE_PATH, '.env'))
config_path = BASE_PATH + '/config/config.json'
# load json config file
config_data = {}
with open(config_path, "r") as read_file:
    config_data = json.load(read_file)
config = config_data[os.getenv("NODE_ENV") or "development"]

engine = create_engine(config['db_python'])
connection = engine.connect()

session = requests.Session()

def generate_nico_pdf(data, args):
	# read company data
	res = connection.execute('SELECT * FROM Companies WHERE uuid="{}"'.format(args.uuid))
	companies = [dict(r) for r in res]
	if len(companies):
		pdf_output = os.path.abspath(os.curdir) + '/public/nico/nico-' + args.uuid + '.pdf'
		with open(os.path.expanduser(pdf_output), "wb+") as output_file:
			shutil.copyfileobj(
				nico(company=companies[0]),
				output_file,
			)
		print("completed new nico coi")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--uuid', type=str, required=False, help="uuid")
    args = parser.parse_args()

    generate_nico_pdf({}, args)

