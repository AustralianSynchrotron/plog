from plog import app
import json

json_data = open('plog/config.json')

data = json.load(json_data)
json_data.close()

facility_code = data['facility_code']

username = data['dbuser']
password = data['password']
host = data['host']
db_name = data['database']

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://%s:%s@%s/%s' % (username,password,host,db_name)

app.secret_key = data['session_key']
