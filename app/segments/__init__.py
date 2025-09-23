from flask import Blueprint

segments_api = Blueprint("segments", __name__)

from . import segments
