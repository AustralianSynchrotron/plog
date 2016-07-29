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

    @property
    def serialise(self):
        """ Return object data in easily serialisable format """
        return {
            'id':           self.id,
            'date':         self.date,
            'time':         self.time,
            'event_id':     self.event_id,
            'data':         self.data,
            'pv_name':      self.pv_name,
            'pv_name_short':self.pv_name_short,
            'device':       self.device,
            'position':     self.position,
            'comments':     self.comments
        }

class registeredUsers(db.Model):
    __tablename__ = 'registered_users'

    register_id = db.Column(db.Integer, primary_key=True)
    card_id = db.Column(db.String(16))
    user_id = db.Column(db.Integer)
    user_name = db.Column(db.String(128))