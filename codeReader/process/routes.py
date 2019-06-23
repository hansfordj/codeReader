from flask import render_template, flash, redirect, url_for, request, jsonify
from codeReader import db, app, role_required, login
from codeReader.process import bp
from codeReader.process.code_reader import Camera
from codeReader.process.email import send_lead_notification_email
from codeReader.models import Code, Log
from datetime import datetime
from flask_login import current_user, login_required
from json import dumps
from time import sleep

cam = Camera()




def get_code():
    cam.enable_camera()
    code = cam.triggerScan()
    return code
    
@app.route('/_get_json_logs')
def get_json_logs():
    logs  = Log.query.order_by(Log.id.desc()).all()
    logList=[e.serialize() for e in logs]
    
    return jsonify(logList)

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
        


@app.route('/', methods = ['GET', 'POST'])
@login_required
def index():
    query  = Code.query.filter_by(selection = True).first()
    print(query.codeData)
    if query: 
        selection = query.codeData
    else:
        selection = "No Selection"
    codes  = Code.query.all()
    codeList=[e.serialize() for e in codes]
    return render_template('index.html', selection=selection, codeList=codeList)

@app.route('/logs',methods=['GET', 'POST'])
@login_required
def logs():
    logs  = Log.query.order_by(Log.id.desc()).all()
    logList=[e.serialize() for e in logs]
    return render_template('logs.html', logList=logList)
    
@app.route('/add')
@role_required(roles=["MANAGER", "ADMIN"])
def add_code():
    code = get_code()
    newCode = Code(codeData=code['codeData'], codeType=code['codeType'])
    db.session.add(newCode)
    db.session.commit()
    print("[SUCCESS] CODE ADDED")
    flash('Success: {} Code Added '.format(newCode.codeData), 'success')
    
    return redirect(url_for('index'))
    
@app.route('/select')
@login_required
def select_code_from_image():
    code = get_code()
    oldSelection = Code.query.filter_by(selection = True).first()
    if oldSelection:
        oldSelection.selection = False
    codeObject = Code.query.filter_by(codeData = code['codeData']).first()
    codeObject.selection = True
    db.session.commit()
    flash('{} Code Selected '.format(codeObject.codeData), 'success')
    return redirect(url_for('index'))
    


@app.route('/trigger_process')
@login_required
def trigger_process():
    selection = Code.query.filter_by(selection = True).first_or_404()
    code = get_code()
    if code:
        
        if selection.codeData == code['codeData']:
            flash("Success: Correct Code!", 'success')
            print("[INFO]  MATCH")
            return redirect(url_for('index'))
            
        else:
            print("[ERROR]  WRONG CODE!")
            flash("Error: Wrong Code!", 'warning')
            return redirect(url_for('index'))

    return '', 204

@app.route('/start_process')
@login_required
def start_process():
    print("[INFO]  PROCESS STARTING")
    selection = Code.query.filter_by(selection = True).first_or_404()
    cam.enable_camera()
    while cam.release == False:
        print("[INFO]  TRIGGERING PROCESS SCAN...")
        code = cam.triggerScan()
        if code:
            query = Code.query.filter_by(codeData = code['codeData']).first()
            if query:
                code_id = query.id
                if selection.codeData == code['codeData']:
                    print("[INFO]  MATCH")
                    log = Log(codeid = code_id, match = True)
                    print("[INFO]  LOGGING MATCH")
                    db.session.add(log)
                    db.session.commit()
                    print("[SUCCESS]  LOGGED. CONTINUING PROCESS...")
                    sleep(0.2)
                    
                else:
                    print("WRONG CODE")
                    log = Log(codeid = code_id, match = False)
                    db.session.add(log)
                    db.session.commit()
                    print("[ALERT]  LOGGED FALSE MATCH... PLEASE RESTART PROCESS")
                    sleep(0.2)
                    return redirect(url_for('index'))
            else:
                print("[ERROR]  SCANNED CODE NOT IN DATABASE, RESTART REQUIRED")
                flash("Error: Scanned Code not in Database, restart required")
                return redirect(url_for('index'))
            
  
    return '', 204
    
@app.route('/stop_process')
@login_required
def stop_process():
    cam.release_camera()
    return '', 204