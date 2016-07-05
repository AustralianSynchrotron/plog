from plog.database import db

class PssLogData(db.Model):
    __tablename__ = 'psslog_data'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(32))
    time = db.Column(db.String(32))
    event_id = db.Column(db.Integer)
    data = db.Column(db.String)
    device = db.Column(db.String(8))
    comments = db.Column(db.String)
