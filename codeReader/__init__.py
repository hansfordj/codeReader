from flask import Flask, render_template, redirect, url_for, jsonify, request, flash
#from flask_socketio import SocketIO
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import os
from os.path import abspath, dirname
import time
from flask_login import LoginManager, current_user
from flask_mail import Mail
from functools import wraps




app = Flask(__name__)
basedir = abspath(dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = 'False'
app.secret_key='45j3b45khjb34k5bsffaSFSDFSDVSDBVsfsvbvavFE34h5b3hj4x'



db = SQLAlchemy(app) 

mail = Mail(app)

#socketio = SocketIO(app, message_queue='redis://')  
#socketio = SocketIO(message_queue='redis://')

login = LoginManager(app)
login.login_view = 'auth.login'
login.login_message_category = "warning"



@login.unauthorized_handler
def unauthorized_callback():
    print("Unauthorized Role Test")
    flash('Warning, Elevated Permission Required', 'warning')
    return redirect(url_for('auth.logout'))




def role_required(roles=["ANY"]):
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if not current_user.is_authenticated:
               return login.unauthorized()
            urole = current_user.get_roles()
            if ( ( roles[0] not in urole) and (roles[0] != "ANY") and ( roles[1] not in urole) and (roles[0] != "ANY")):
                print("Error!!!")
                return login.unauthorized_callback()      
            return fn(*args, **kwargs)
        return decorated_view
    return wrapper


from codeReader.process import bp as process_bp
#from codeReader.api import bp as api_bp
from codeReader.auth import bp as auth_bp
#from codeReader.admin import bp as admin_bp





app.register_blueprint(process_bp)
#app.register_blueprint(api_bp, url_prefix='/api')
app.register_blueprint(auth_bp, url_prefix='/auth')
#app.register_blueprint(admin_bp, url_prefix='/admin')
