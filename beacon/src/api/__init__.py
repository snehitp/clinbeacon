from flask import Flask, request
import logging
from os import path

import sys
sys.path.append(path.abspath('../lib'))

FORMAT = '%(levelname)-8s %(asctime)-15s %(message)s'
logging.basicConfig(level=logging.INFO, format=FORMAT)

log = logging.getLogger()

# Define a new flask application
app = Flask(__name__)

@app.before_request
def before_request():
  print(request.path)

# Add the Query controllers to the flask application
from api.query_controllers import query_controllers
app.register_blueprint(query_controllers, url_prefix='/api/query')

from api.vcf_controllers import vcf_controllers
app.register_blueprint(vcf_controllers, url_prefix='/api/vcf')

# Add the data import controllers to the flask application
from api.import_controllers import import_controllers
app.register_blueprint(import_controllers, url_prefix='/api/import')

# Authentication controllers to the flask application
from api.auth_controllers import auth_controllers
app.register_blueprint(auth_controllers, url_prefix='/api/auth')

# System information controllers to the flask application
from api.info_controllers import info_controllers
app.register_blueprint(info_controllers, url_prefix='/api/info')

# Data management information controllers to the flask application
from api.manage_controllers import manage_controllers
app.register_blueprint(manage_controllers, url_prefix='/api/manage')

from api.patient_controllers import patient_controllers
app.register_blueprint(patient_controllers, url_prefix='/api/patient')