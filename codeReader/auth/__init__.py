from flask import Blueprint

bp = Blueprint('auth', __name__)

from codeReader.auth import routes
