from flask import render_template,session,redirect,url_for,request,current_app,make_response,flash

from sqlalchemy.sql import update,select
from sqlalchemy.sql import extract,and_,or_
from wtforms import Form,StringField,SelectField,SubmitField,validators
import ldap

from plog import app
from plog.database import db
from plog.models import PssLogData
from plog.config import ldap_server,ldap_dn,ldap_sx,ldap_user,ldap_passw

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

@app.route('/rfid/',methods=['POST'])
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

@app.route('/pv/', methods=['POST'])
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

@app.route('/ui/', methods=['POST'])
def ui():
    if 'rfid' in request.form:
        # get the latest card data from db...
        last_id = PssLogData.query.order_by(PssLogData.date.desc(), PssLogData.time.desc()).first()
        return last_id.data

    return 'true'

@app.route('/register/', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        # do some form validation
        if 'user_name' in request.form:
            user_name = request.form['user_name'].strip()
        else:
            flash('No User has been selected', 'error')
            error = 'No User has been selected'
            return redirect(url_for('register'))

        if 'access_id' in request.form:
            access_id = request.form['access_id'].strip()
        else:
            flash('No Card ID has been selected', 'error')
            error = 'No Card ID has been selected'
            return redirect(url_for('register'))

        print(user_name, access_id)

        # do some processing on the data...

        return redirect(url_for('register'))

    else:
        # initialise ldap server each time (seems to prevent timeout errors)
        connect = ldap.initialize(ldap_server)
        connect.protocol_version = ldap.VERSION3
        connect.set_option(ldap.OPT_REFERRALS, 0)

        user_name = []

        try:
            connect.simple_bind_s(ldap_user + ldap_sx, ldap_passw)

            result = connect.search_s(ldap_dn, ldap.SCOPE_SUBTREE,'(&(objectclass=user)(sAMAccountName=*))',['displayName'])

            connect.unbind_s()

        except ldap.LDAPError, e:
            print('An error occured, unable to bind: %s' % e)
            connect.unbind_s()
            return render_template("register.html",ldap=None)

        # create a friendly list
        for j in range(len(result)):
            user_name.append( result[j][1]['displayName'][0] )
            #print(result[j][1]['displayName'][0])


        #print(user_name)
        return render_template("register.html",ldap=sorted(user_name))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404