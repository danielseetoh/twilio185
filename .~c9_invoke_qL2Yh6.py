import psycopg2 as db
import sys
import os
from flask import Flask, request, Response, render_template, session, redirect, json, url_for
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
        cur.execute("SELECT responded, phonenumber FROM requests WHERE id = '%s' " % (request_id))
        responded, phonenumber = cur.fetchall()[0]
        if answer == 'y':
            # This does prevent us from tracking multiple requests to a doctor, and requires him to respond only to the newest one.
            # Will add a method to deconflict clashes in requests from the same area
            if responded == False:
                cur.execute("UPDATE requests SET responded = %s WHERE id = '%s'" % (True, request_id))
                con.commit()
                r.message("Thank you for replying. You are the first to accept and other doctors will not be able to accept this request already. A message will be sent to the requester to let him know you are on the way. Please contact the requestor at " + str(phonenumber))
                # create a response to the requestor
                acknowledge(phonenumber)
            elif responded == True:
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
    
    # Need to add either a request database or a function that carries the request values in. I prefer database.
    if request.method == 'POST': 
        _zipcode = request.form['zipcode']
        _phonenumber = request.form['phonenumber']
        
        try:
            cur.execute("INSERT INTO requests (phonenumber, zipcode, responded) VALUES ('%s', '%s', False) RETURNING id"\
            %(_phonenumber,_zipcode))
            request_id = cur.fetchall()[0][0]
            con.commit()
            username = 'danielseetoh' # just to message only me
            # will add the ability to track gps location of requester to match locally with doctors nearby
            # for now just testing by matching zipcode
            cur.execute("SELECT phonenumber FROM doctors WHERE zipcode = '%s' AND active = True" % (_zipcode))
            doctor_phone_numbers = cur.fetchall()
            
            for number in doctor_phone_numbers:
                client.messages.create(
                body = "Request id: %s. There is an emergency at '%s', will you be able to respond in \
                less than 8 minutes?(y%s/n%s)" % (request_id, _zipcode, request_id, request_id),
                to = number[0],
                from_ = "+14245438814",
                )
        except:
            return('Could not create request')
        
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
            session['username'] = _username
            return render_template('index.html', name=_username)
        except:
            error = 'Unable to insert into database.'
            return render_template('signup.html', error=error)
    return render_template('signup.html')

@app.route('/login', methods = ['GET', 'POST'] )
def login():
    error = None
    if request.method == 'POST':
        _username = request.form['username']
        _password = request.form['password']
        cur.execute("SELECT * FROM doctors WHERE username = '%s' and password = '%s' " % (_username, _password))
        result = cur.fetchall()
        if result:
            session['username'] = _username
            return render_template('index.html', name=_username)
        else:
            error = "Invalid Username/Password combination"
            return render_template('login.html', error = error)

    return render_template('login.html', error=error)
    
@app.route('/logout', methods = ['GET', 'POST'])
def logout():
    # remove the username from the session if it's there
    if request.method == 'POST':
        session.clear()
        return render_template('index.html')
    return render_template('index.html')
    
@app.route('/user/<username>', methods = ['GET', 'POST'])
def user(username = None):
    if request.method == 'POST':
        #change the db
        if session['active'] == True:
            session['active'] = False
        else:
            session['active'] = True
        try:
            cur.execute("UPDATE doctors SET active = %s WHERE username = '%s'" % (session['active'], session['username']))
            con.commit()
            return render_template('user.html', username = username, active = session['active'])
        except:
            #change this soon.
            return render_template('index.html')
    if session['username'] and session['username'] == username:
        cur.execute("SELECT active FROM doctors WHERE username = '%s'" % (session['username']))
        result = cur.fetchall()
        active = result[0][0]
        session['active'] = active
        return render_template('user.html', username = username, active = session['active'])
    return render_template('index.html')

def acknowledge(phonenumber):
    client.messages.create(
    body = "A doctor is on the way.",
    to = phonenumber,
    from_ = "+14245438814",
    )   



if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8080)

