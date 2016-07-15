from flask import render_template,session,redirect,url_for,request,current_app,make_response

from sqlalchemy.sql import update,select
from sqlalchemy.sql import extract,and_,or_

from plog import app
from plog.database import db
from plog.models import PssLogData

import requests
from datetime import datetime,timedelta

date_format = "%Y-%m-%d %H:%M:%S"
DEBUG = False

def find_cluster_num(timestamp):
    delta_t = timedelta(minutes=20)
    cluster_search = PssLogData.query.order_by(PssLogData.date.desc(),PssLogData.time.desc()).first()

    cluster_string = cluster_search.date + " " + cluster_search.time
    cluster_dt = datetime.strptime(cluster_string, date_format)
    current_dt = datetime.strptime(timestamp, date_format)
    diff_dt = current_dt - cluster_dt
    if DEBUG:
        print(cluster_string,cluster_dt,current_dt,delta_t,diff_dt)

    if diff_dt < delta_t:
        print("Same cluster detected!")
        return cluster_search.event_id
    else:
        print("Creating new cluster!")
        if cluster_search.event_id == None:
            if DEBUG:
                print("event_id: 1")
            return 1
        else:
            if DEBUG:
                print("event_id: " + str(cluster_search.event_id + 1))
            return cluster_search.event_id + 1

@app.route('/')
def plog():
    return render_template("main.html")

@app.route('/rfid',methods=['POST'])
def rfid():
    # get the posted data
    timestamp = request.form['timestamp']
    cardID = request.form['cardID']
    device = request.form['source']
    if DEBUG:
        print(timestamp,cardID,device)

    mod_time = timestamp.split(" ")[1]
    mod_date = timestamp.split(" ")[0]

    # determine event_id
    eid = find_cluster_num(timestamp)

    # create the database entry and commit to file
    tmp = PssLogData(date=mod_date,time=mod_time,event_id=eid,data=cardID,device=device)
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

    if DEBUG:
        print(timestamp, pv, pv_val, device)

    mod_time = timestamp.split(" ")[1]
    mod_date = timestamp.split(" ")[0]

    # determine event_id
    eid = find_cluster_num(timestamp)

    # create the database entry and commit to file
    tmp = PssLogData(date=mod_date, time=mod_time, event_id=eid, data=pv_val, pv_name=pv, device=device)
    db.session.add(tmp)
    db.session.commit()

    print("Received data: %s : %s : %s" % (timestamp, device, pv_val))

    return pv

@app.route('/ui', methods=['POST'])
def ui():
    pass

@app.route('/register', methods=['GET', 'POST'])
def register():
    return render_template("register.html")

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404