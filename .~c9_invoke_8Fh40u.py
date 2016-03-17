import psycopg2 as db
import sys
import os
from flask import Flask, request, Response, render_template, session, redirect, json
from twilio import twiml
from twilio.rest import TwilioRestClient
import imp


#loads account_sid and auth_token from private space
config = imp.load_source('config', '../sensitive_data/config.py')


TWILIO_ACCOUNT_SID = config.TWILIO_ACCOUNT_SID
TWILIO_AUTH_TOKEN = config.TWILIO_AUTH_TOKEN
app = Flask(__name__, template_folder='templates')
app.secret_key = config.SECRET_KEY

client = TwilioRestClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

requests = {}

# connect to doctor database
try:
    con = db.connect(database="testdbdoc", user="postgres", password="seetoh", host="localhost")
    print 'Successfully connected to databases!'
    
    cur = con.cursor()
except:
    print 'Failed to connect to database.'
    


@app.route('/receivemessage', methods = ['GET', 'POST'])
def receivemessage():

    body = request.values.get('Body', None)
    fromnum = request.values.get('From', None)
    r = twiml.Response()
    body = body.lower()
    
    try:
        answer = body[0]
        request_id = body[1:]
        if answer == 'y':
            # This does prevent us from tracking multiple requests to a doctor, and requires him to respond only to the newest one.
            # Will add a method to deconflict clashes in requests from the same area
            if requests[request_id] == False:
                requests[request_id] = True
                r.message("Thank you for replying. You are the first to accept and other doctors will not be able to accept this request \
                already. A message will be sent to the requester to let him know you are on the way.")
                # create a response to the requestor
                
            elif requests[request_id] == True:
                r.message("Thank you for replying. Another doctor is on the way to the scene already, but we appreciate your prompt \
                response. Have a good day.")
            else:
                r.message("The request is no longer valid, thank you for replying.")
        elif answer == 'n':
            r.message("Sorry to hear that, thank you for your prompt response, have a good day.")
        else:
            r.message("Invalid response.")
    except:
        r.message("Invalid response.")
        
    # has to be valid twiml
    return str(r)

@app.route('/sendmessage', methods = ['POST', 'GET'])   
def sendmessage():
    # Test values
    # Need to add either a request database or a function that carries the request values in. I prefer database.
    zipcode = '94720' # requester zipcode
    username = 'danielseetoh' # just to message only me
    request_id = '1' # retrieve request id in table request
    requests[request_id] = False

    # will add the ability to track gps location of requester to match locally with doctors nearby
    # for now just testing by matching zipcode
    cur.execute("SELECT phonenumber FROM doctors WHERE zipcode = '%s' AND username = '%s'" % (zipcode, username))
    doctor_phone_numbers = cur.fetchall()
    
    for number in doctor_phone_numbers:
        client.messages.create(
        body = "Request id: %s. There is an emergency at '%s', will you be able to respond in \
        less than 8 minutes?(y%s/n%s)" % (request_id, zipcode, request_id, request_id),
        to = number[0],
        from_ = "+14245438814",
        )
    print session['requestor'] 
    return('Messages sent')

@app.route('/')
def index(name = None):
    return render_template('index.html', name=name)


@app.route('/signup', methods = ['POST', 'GET'])
def signup():
    error = None;
    if request.method == 'POST':
        # insert into database
        _username = request.form['username']
        _password = request.form['password']
        _phonenumber = request.form['phonenumber']
        _zipcode = request.form['zipcode']
        try:
            cur.execute("INSERT INTO doctors (username, password, phonenumber, zipcode, active) \
            VALUES ('%s', '%s', '%s', '%s', True ) " % (_username, _password, _phonenumber, _zipcode)) 
            con.commit()
            return render_template('/', name=_username)
        except:
            error = 'Unable to insert into database. {} {} {} {}'.format(_username,_password,_phonenumber,_zipcode)
            return render_template('signup.html', error=error)
    return render_template('signup.html', error=error)

@app.route('/login', methods = ['GET', 'POST'] )
def login():
    error = None
    if request.method == 'POST':
        _username = request.form['username']
        _password = request.form['password']
        cur.execute("SELECT * FROM doctors WHERE username = '%s' and password = '%s' " % (_username, _password))
        result
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)
    
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8080)

