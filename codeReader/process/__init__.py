from flask import Blueprint


bp = Blueprint('process', __name__,)

from codeReader.process import routes

