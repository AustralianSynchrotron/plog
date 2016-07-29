from plog.database import db

class PssLogData(db.Model):
    __tablename__ = 'psslog_data'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(32))
    time = db.Column(db.String(32))
    event_id = db.Column(db.Integer)
    data = db.Column(db.String)
    pv_name = db.Column(db.String(128))
    pv_name_short = db.Column(db.String(64))
    device = db.Column(db.String(8))
    position = db.Column(db.Integer)
    comments = db.Column(db.String)

class registeredUsers(db.Model):
    __tablename__ = 'registered_users'

    register_id = db.Column(db.Integer, primary_key=True)
    card_id = db.Column(db.String(16))
    user_id = db.Column(db.Integer)
    user_name = db.Column(db.String(128))