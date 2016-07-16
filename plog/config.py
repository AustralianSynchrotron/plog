from plog import app
import json

json_data = open('plog/config.json')

data = json.load(json_data)
json_data.close()

ldap_server = data['ldap']['ldap_server']
ldap_sx = data['ldap']['ldap_sx']
ldap_dn = data['ldap']['ldap_dn']
ldap_user = data['ldap']['ldap_user']
ldap_passw = data['ldap']['ldap_passw']

facility_code = int(data['rfid']['facility_code'])
rfid_host = data['rfid']['rfid_host']
rfid_port = data['rfid']['rfid_port']

username = data['dbuser']
password = data['password']
host = data['host']
db_name = data['database']

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://%s:%s@%s/%s' % (username,password,host,db_name)

app.secret_key = data['session_key']