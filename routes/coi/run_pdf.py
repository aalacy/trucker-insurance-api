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

from pdf import pdf

BASE_PATH = os.getcwd()
config_path = BASE_PATH + '/config/config.json'
# load json config file
config_data = {}
with open(config_path, "r") as read_file:
    config_data = json.load(read_file)
config = config_data[os.getenv("NODE_ENV") or "development"]

engine = create_engine(config['db_python'])
connection = engine.connect()

def generate_app_pdf(data, args):
	# read company data
	res = connection.execute('SELECT * FROM Companies WHERE uuid="{}"'.format(args.uuid))
	companies = [dict(r) for r in res]
	if len(companies):
		pdf_output = os.path.abspath(os.curdir) + '/public/pdf/app-' + args.uuid + '.pdf'
		with open(os.path.expanduser(pdf_output), "wb+") as output_file:
			shutil.copyfileobj(
				pdf(company=companies[0]),
				output_file,
			)
		print("completed new app pdf")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--uuid', type=str, required=False, help="uuid")
    args = parser.parse_args()

    generate_app_pdf({}, args)
