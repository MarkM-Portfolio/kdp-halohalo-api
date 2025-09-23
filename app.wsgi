# flake8: noqa
#! /var/www/html/kdp-halohalo-api/venv/bin/python3.6

activate_this = "/home/ubuntu/kdp-halohalo-api/venv/bin/activate_this.py"
with open(activate_this) as f:
    exec(f.read(), dict(__file__=activate_this))

import sys
import logging

logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, "/var/www/html/kdp-halohalo-api/")

from flask_app import application
