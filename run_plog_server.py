from plog import app
from plog.config import rfid_port

app.debug = True # remove for production
app.run(host="0.0.0.0", port=int(rfid_port))