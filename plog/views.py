from flask import render_template,session,redirect,url_for,request,current_app,make_response,flash,jsonify

from sqlalchemy.sql import update,select
from sqlalchemy.sql import extract,and_,or_,func
from wtforms import Form,StringField,SelectField,SubmitField,validators
import ldap

from plog import app
from plog.database import db
from plog.models import PssLogData,registeredUsers
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

def decode_card_id(cardID):
    # convert to binary and pad with zeros
    bin_rep = bin(int(str(cardID), base=16))[2:].zfill(28)
    bin_strip = bin_rep[3:-1]  # strip off the parity bits

    # extract the facility and code id's
    facility = int(bin_strip[:8], 2)
    card_id = int(bin_strip[9:], 2)

    return facility,card_id



@app.route('/')
def plog():
    # get the latest card data from db...
    # last_event_id = PssLogData.query.with_entities(func.max(PssLogData.event_id).label('max_event_id')).first()
    # last_events = PssLogData.query.filter_by(event_id=last_event_id.max_event_id).all()
    last_events = PssLogData.query.filter_by(event_id=None).all()

    # sort last events into users and remaining events
    # user events have a len(data) == 8 and pv_name == None
    user_events = []
    pss_events = []
    for event in last_events:
        if ((len(event.data) == 8) and (event.pv_name == None)):
            # fetch the username based on the card id
            try:
                event.user_name = registeredUsers.query.filter_by(card_id=event.data).first().user_name
            except:
            # some error handling if user not in database
                event.user_name = "ID Not <a href='/register/"+ event.data +"'>Registered</a>"

            user_events.append(event)
        else:
            #print("PSS Event found")
            pss_events.append(event)


    return render_template("main.html",e_user=user_events,e_pss=pss_events)

@app.route('/rfid/',methods=['POST'])
def rfid():
    # get the posted data
    timestamp = request.form['timestamp']
    cardID = request.form['cardID'].strip() # remove trailing white space (\r)
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
    # eid = find_cluster_num(timestamp)
    eid = None

    shorty = pv.split(":")[1].rsplit("_",1)[0]

    # create the database entry and commit to file
    tmp = PssLogData(date=mod_date, time=mod_time, event_id=eid, data=pv_val, pv_name=pv, pv_name_short=shorty,device=device)
    db.session.add(tmp)
    db.session.commit()

    print("Received data: %s : %s : %s" % (timestamp, device, pv_val))

    return pv

@app.route('/ui/', methods=['POST'])
def ui():
    if 'rfid' in request.form:

        # get the latest card data from db...
        last_id = PssLogData.query.order_by(PssLogData.date.desc(), PssLogData.time.desc()).first()

        # check if user is already assigned a card id
        current_id = registeredUsers.query.filter_by(card_id=last_id.data).first()

        facility,card_id = decode_card_id(last_id.data)

        # return user_name if found in db
        if current_id:
            var = [str(last_id.data).strip(), facility, card_id, current_id.user_name]
        else:
            # just return the decoded values otherwise
            var = [str(last_id.data).strip(), facility, card_id, ""]

        #var = [str(last_id.data).strip(),facility,card_id]

        return jsonify(result=var)

    if 'check' in request.form:
        # print(request.form)
        if request.form['card_id']:
            this_card_id = request.form['card_id']
        else:
            # return empty strings if no card_id entered into form
            var = ["","","",""]
            return jsonify(result=var)

        # get the card data from db...
        current_id = registeredUsers.query.filter_by(card_id=this_card_id).first()

        facility,card_id = decode_card_id(this_card_id)

        # return user_name if found in db
        if current_id:
            var = [this_card_id, facility, card_id, current_id.user_name]
        else:
            # just return the decoded values otherwise
            var = [this_card_id, facility, card_id, ""]

        return jsonify(result=var)

    return 'true'

@app.route('/register/', methods=['GET', 'POST'])
@app.route('/register/<string:new_card_id>')
def register(new_card_id=""):
    error = None
    if request.method == 'POST':
        # do some form validation
        # seems to always be available, just empty if nothing entered
        if request.form['user_name']:
            user_name = request.form['user_name'].strip()
        else:
            flash('No User has been selected',"warning")
            error = 'No User has been selected'


        # seems to always be available, just empty if nothing entered
        if request.form['access_id']:
            access_id = request.form['access_id'].strip()
        else:
            flash('No Card ID has been selected',"warning")
            error = 'No Card ID has been selected'


        if error:
            return redirect(url_for('register'))

        print(user_name, access_id)

        # check if the card_id is already assigned then update as required
        check = registeredUsers.query.filter_by(card_id=access_id).first()
        if check:
            print("Card ID already assigned to a User in the database, Updating...")
            check.user_name = user_name
            db.session.commit()
            return redirect(url_for('register'))

        # do some processing on the data...
        tmp = registeredUsers(card_id=access_id,user_name=user_name)
        db.session.add(tmp)
        db.session.commit()

        flash("Registered User data has been saved","success")

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
            flash('An error occured, unable to bind: %s' % e,"danger")
            connect.unbind_s()
            return render_template("register.html",ldap=None)

        # create a friendly list
        for j in range(len(result)):
            user_name.append( result[j][1]['displayName'][0] )
            #print(result[j][1]['displayName'][0])

        if new_card_id:
            return render_template("register.html",ldap=sorted(user_name),card_id=new_card_id)

        #print(user_name)
        return render_template("register.html",ldap=sorted(user_name),card_id="")

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404