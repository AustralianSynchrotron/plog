from flask import render_template,session,redirect,url_for,request,current_app,make_response

from sqlalchemy.sql import update,select
from sqlalchemy.sql import extract,and_,or_

from plog import app
from plog.database import db
from plog.models import PssLogData

import requests
from datetime import datetime

@app.route('/')
def plog():
    return 'Plogger!'

@app.route('/rfid',methods=['POST'])
def rfid():
    timestamp = request.form['timestamp']
    cardID = request.form['cardID']
    device = request.form['source']

    mod_time = timestamp.split(" ")[1]
    mod_date = timestamp.split(" ")[0]

    tmp = PssLogData(date=mod_date,time=mod_time,data=cardID,device=device)
    db.session.add(tmp)
    db.session.commit()

    print("Received data: %s : %s : %s" % ( timestamp, device, cardID ))

    return cardID

@app.route('/pv', methods=['POST'])
def pv():
    timestamp = request.form['timestamp']
    pv = request.form['pv']
    pv_val = request.form['pv_val']
    device = request.form['source']

    mod_time = timestamp.split(" ")[1]
    mod_date = timestamp.split(" ")[0]


    return pv

@app.route('/ui', methods=['POST'])
def ui():
    pass

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404