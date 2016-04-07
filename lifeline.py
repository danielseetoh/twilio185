import psycopg2 as db
import sys
import os
from flask import Flask, request, Response, render_template, session, redirect, json, url_for
from twilio import twiml
from twilio.rest import TwilioRestClient
import imp
import urllib3
import certifi
import urllib3.contrib.pyopenssl
urllib3.contrib.pyopenssl.inject_into_urllib3()
import googlemaps
from datetime import datetime

# To allow python 2.7.6 to send safe http requests
http = urllib3.PoolManager(
    cert_reqs='CERT_REQUIRED', # Force certificate check.
    ca_certs=certifi.where(),  # Path to the Certifi bundle.
)

# print geocode_result[0]['geometry']['location'].values()
# print reverse_geocode_result[0]['formatted_address']

#loads account_sid and auth_token from private space
config = imp.load_source('config', '../sensitive_data/config.py')

TWILIO_ACCOUNT_SID = config.TWILIO_ACCOUNT_SID
TWILIO_AUTH_TOKEN = config.TWILIO_AUTH_TOKEN
app = Flask(__name__, template_folder='templates')
app.secret_key = config.SECRET_KEY
gmaps = googlemaps.Client(key=config.GMAPS_KEY)
client = TwilioRestClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
SEARCH_RADIUS = 400.0
# connect to testdbdoc database
try:
    con = db.connect(database="lifeline", user="postgres", password="seetoh", host="localhost")
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
        # get first letter y/n from the reply
        answer = body[0]
        # request id is the remaining characters
        request_id = body[1:]
        cur.execute("SELECT responded, phonenumber FROM requests WHERE id = '%s' " % (request_id))
        responded, phonenumber = cur.fetchall()[0]
        if answer == 'y':
            # Will add a method to deconflict clashes in requests from the same area
            if responded == False:
                cur.execute("UPDATE requests SET responded = %s WHERE id = '%s'" % (True, request_id))
                con.commit()
                r.message("Thank you for replying. You are the first to accept and other medical personnel will be informed that someone is on the way should they choose to accept as well. A message will be sent to the requester to let him/her know you are on the way. Please contact the requestor at " + str(phonenumber))
                # create a response to the requestor
                acknowledge_requestor(phonenumber)
            elif responded == True:
                r.message("Thank you for replying. Another medical personnel is on the way to the scene already, but we appreciate your prompt response. Have a good day.")
            else:
                r.message("The request is not valid.")
        elif answer == 'n':
            r.message("Thank you for your prompt response, have a good day.")
        else:
            r.message("Invalid response.")
    except:
        r.message("Invalid response.")
        
    # has to be valid twiml
    return str(r)

@app.route('/sendmessage', methods = ['POST', 'GET'])   
def sendmessage():
    
    if request.method == 'POST': 
        # assuming we get lat lng from the user's phone
        _addresspoint = eval(request.form['addresspoint'])
        _phonenumber = str(request.form['phonenumber'])
        # get the current hour in 24hr format from the requestor (workaround for timezones)
        _currenthour = int(request.form['currenthour'])
        print _addresspoint, _phonenumber, _currenthour
        print type(_addresspoint), type(_phonenumber), type(_currenthour)
        # assuming _addresspoint is a tuple
        _address = gmaps.reverse_geocode(_addresspoint)[0]['formatted_address']
        # geocode_result = gmaps.geocode(_address)
        # _addresspoint = geocode_result[0]['geometry']['location'].values()[0], geocode_result[0]['geometry']['location'].values()[1]
        cur.execute("SELECT ST_SetSRID(ST_MakePoint({}, {}), 4326)".format(_addresspoint[1],_addresspoint[0]))
        _geog = cur.fetchall()[0][0]
        try:
            cur.execute("INSERT INTO requests (phonenumber, addresspoint, responded) VALUES ('{}', '{}', False) RETURNING id"\
        .format(_phonenumber,_addresspoint))
            request_id = cur.fetchall()[0][0]
            con.commit()
            username = 'danielseetoh' # just to message only me
            # gets all doctors within the area that are active at this time.
            cur.execute("SELECT DISTINCT ON (medics.phonenumber) medics.phonenumber FROM medics,addresses WHERE medics.username = addresses.username AND medics.active = True AND ST_DWithin(addresses.geog, '{}', '{}') AND addresses.starttime<= '{}' AND addresses.endtime > '{}'".format(_geog, SEARCH_RADIUS, _currenthour, _currenthour))
            # cur.execute("SELECT phonenumber FROM doctors WHERE active = True AND username = 'danielseetoh'")
            medic_phone_numbers = cur.fetchall()
            for number in medic_phone_numbers:
                client.messages.create(
                body = "Request id: %s. There is an emergency at '%s', will you be able to respond in \
                less than 8 minutes?(y%s/n%s)" % (request_id, _address, request_id, request_id),
                to = number[0],
                # can change in the future to check for available lines in the country it is from
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
    error = None
    if request.method == 'POST':
        addresslist = []
        try:
            _username = str(request.form['username'])
            _password = str(request.form['password'])
            _phonenumber = str(request.form['phonenumber'])
        except:
            error = 'There is an error with your personal information.'
            return render_template('signup.html', error=error)
        try:
            _address1 = str(request.form['address1'])
            _starttime1 = int(request.form['starttime1'])
            _endtime1 = int(request.form['endtime1'])
            # parse address into lat lng
            try:
                geocode_result = gmaps.geocode(_address1)
                if len(geocode_result) == 0:
                    raise Exception
                #get the lat,long of the address
                _addresspoint1 = geocode_result[0]['geometry']['location'].values()[0], geocode_result[0]['geometry']['location'].values()[1]
                #the _addresspoint1 tuple is flipped around because PostGIS uses long,lat instead of lat,long
                cur.execute("SELECT ST_SetSRID(ST_MakePoint('{}', '{}'), 4326)".format(_addresspoint1[1],_addresspoint1[0]))
                _geog1 = cur.fetchall()[0][0]
            except:
                error = "First address is invalid.{}".format(_addresspoint1)
                return render_template('signup.html', error=error)
            if _starttime1 >= _endtime1:
                raise Exception
            addresslist.append([_address1, _addresspoint1, _starttime1, _endtime1, _geog1])
        except:
            error = "There is an issue with your first address/timings."
            return render_template('signup.html', error=error)
        if request.form['address2']:
            try:
                _address2 = str(request.form['address2'])
                _starttime2 = int(request.form['starttime2'])
                _endtime2 = int(request.form['endtime2'])
                #parse address into lat long here
                try:
                    geocode_result = gmaps.geocode(_address2)
                    if len(geocode_result) == 0:
                        raise Exception
                    _addresspoint2 = geocode_result[0]['geometry']['location'].values()[0], geocode_result[0]['geometry']['location'].values()[1] 
                    cur.execute("SELECT ST_SetSRID(ST_MakePoint('{}', '{}'), 4326)".format(_addresspoint2[1],_addresspoint2[0]))
                    _geog2 = cur.fetchall()[0][0]
                except:
                    error = "Second address is invalid."
                    return render_template('signup.html', error=error)
                            
                if _starttime2 >= _endtime2:
                    raise Exception
                addresslist.append([_address2, _addresspoint2, _starttime2, _endtime2, _geog2])
            except:
                error = "There is an issue with your second address/timings."
                return render_template('signup.html', error=error)               
        if request.form['address3']:
            try:
                _address3 = str(request.form['address3'])
                _starttime3 = int(request.form['starttime3'])
                _endtime3 = int(request.form['endtime3'])
                #parse address into lat long here
                try:
                    geocode_result = gmaps.geocode(_address3)
                    if len(geocode_result) == 0:
                        raise Exception
                    _addresspoint3 = geocode_result[0]['geometry']['location'].values()[0], geocode_result[0]['geometry']['location'].values()[1]
                    cur.execute("SELECT ST_SetSRID(ST_MakePoint('{}', '{}'), 4326)".format(_addresspoint3[1],_addresspoint3[0]))
                    _geog3 = cur.fetchall()[0][0]
                except:
                    error = "Third address is invalid."
                    return render_template('signup.html', error=error)
                   
                if _starttime3 >= _endtime3:
                    raise Exception
                addresslist.append([_address3, _addresspoint3, _starttime3, _endtime3, _geog3])
            except:
                error = "There is an issue with your third address/timings."
                return render_template('signup.html', error=error)
        try:
            cur.execute("INSERT INTO medics (username, password, phonenumber, active)\
            VALUES ('{}', '{}', '{}', True)".format(_username, _password, _phonenumber))
            for infolist in addresslist:
                cur.execute("INSERT INTO addresses (username, address, addresspoint, starttime, endtime, geog)\
                VALUES('{}', '{}', '{}', '{}', '{}', '{}')".format(_username, infolist[0], infolist[1], infolist[2], infolist[3], infolist[4]))
        except:
            error = 'Unable to insert into database.{}'
            return render_template('signup.html', error=error)
        session['username'] = _username
        con.commit()
        return render_template('index.html', name=_username)
    return render_template('signup.html')

@app.route('/login', methods = ['GET', 'POST'] )
def login():
    error = None
    if request.method == 'POST':
        _username = request.form['username']
        _password = request.form['password']
        cur.execute("SELECT * FROM medics WHERE username = '%s' and password = '%s' " % (_username, _password))
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
            cur.execute("UPDATE medics SET active = %s WHERE username = '%s'" % (session['active'], session['username']))
            con.commit()
            return render_template('user.html', username = username, active = session['active'])
        except:
            #change this soon.
            return render_template('index.html')
    if session['username'] and session['username'] == username:
        cur.execute("SELECT active FROM medics WHERE username = '%s'" % (session['username']))
        result = cur.fetchall()
        active = result[0][0]
        session['active'] = active
        cur.execute("SELECT address, starttime, endtime FROM addresses where username = '%s' ORDER BY address" % (session['username']))
        result = cur.fetchall()
        session['addresses'] = {}
        for i in range(len(result)):
            session['addresses'][i] = result[i]
            print type(i)
            print session['addresses'][i]
        return render_template('user.html', username = username, active = session['active'])
    return render_template('index.html')

@app.route('/edit/<username>', methods = ['GET', 'POST'])
def edit(username = None, error = None):
    error = None
    if session['username'] and session['username'] == username:
        cur.execute("SELECT active FROM medics WHERE username = '%s'" % (session['username']))
        result = cur.fetchall()
        active = result[0][0]
        session['active'] = active
        cur.execute("SELECT address, starttime, endtime FROM addresses where username = '%s' ORDER BY address" % (session['username']))
        result = cur.fetchall()
        session['addresses'] = {}
        for i in range(len(result)):
            session['addresses'][i] = result[i]
        if request.method == 'POST':
            try:
                if request.form['delete']:
                    del_id = request.form['delete'][6:]
                    cur.execute("DELETE from addresses WHERE username = '{}' and address = '{}' and starttime = '{}' and endtime = '{}'".format(session['username'], session['addresses'][del_id][0], session['addresses'][del_id][1], session['addresses'][del_id][2]))
                    con.commit()
                    return redirect('edit/' + session['username'])
            except:
                if str(request.form['active']) == 'act':
                    session['active'] = True
                else:
                    session['active'] = False
                cur.execute("UPDATE medics SET active = %s WHERE username = '%s'" % (session['active'], session['username']))
                for i in session['addresses']:
                    if request.form['address'+str(i)]:
                        _address = str(request.form['address'+str(i)])
                        _starttime = int(request.form['starttime'+str(i)])
                        _endtime = int(request.form['endtime'+str(i)])
                        try:
                            geocode_result = gmaps.geocode(_address)
                            if len(geocode_result) == 0:
                                raise Exception
                            #get the lat,long of the address
                            _addresspoint = geocode_result[0]['geometry']['location'].values()[0], geocode_result[0]['geometry']['location'].values()[1]
                            #the _addresspoint1 tuple is flipped around because PostGIS uses long,lat instead of lat,long
                            cur.execute("SELECT ST_SetSRID(ST_MakePoint('{}', '{}'), 4326)".format(_addresspoint[1],_addresspoint[0]))
                            _geog = cur.fetchall()[0][0]
                            if _starttime >= _endtime:
                                raise Exception
                        except:
                            
                            error = "Address/timing {} is invalid.".format(i+1)
                            # return redirect('edit/' + session['username'])
                            return render_template('edit.html', error = error)
                        else:
                            try:
                                cur.execute("UPDATE addresses SET address = '{}',addresspoint = '{}', starttime = '{}', endtime = '{}', geog = '{}' WHERE username = '{}' and address = '{}' and starttime = '{}' and endtime = '{}' ".format(_address, _addresspoint, _starttime, _endtime, _geog, session['username'], session['addresses'][i][0], session['addresses'][i][1], session['addresses'][i][2]))
                            except:
                                error = "{}".format(session['addresses'])
                                # return redirect('edit/' + session['username'])
                                return render_template('edit.html', error = error)
                    else:
                        cur.execute("DELETE from addresses WHERE username = '{}' and address = '{}' and starttime = '{}' and endtime = '{}'".format(session['username'], session['addresses'][i][0], session['addresses'][i][1], session['addresses'][i][2]))
                con.commit()
                return redirect('user/'+session['username'])
        # if session['username'] and session['username'] == username:
        #     cur.execute("SELECT active FROM medics WHERE username = '%s'" % (session['username']))
        #     result = cur.fetchall()
        #     active = result[0][0]
        #     session['active'] = active
        #     cur.execute("SELECT address, starttime, endtime FROM addresses where username = '%s' ORDER BY address" % (session['username']))
        #     result = cur.fetchall()
        #     session['addresses'] = {}
        #     for i in range(len(result)):
        #         session['addresses'][i] = result[i]
        return render_template('edit.html', username = username)
    return render_template('index.html')

@app.route('/new/<username>', methods = ['GET', 'POST'])
def new(username = None):
    error = None
    if session['username'] and session['username'] == username:
        if request.method == 'POST':
            if request.form['address']:
                _address = str(request.form['address'])
                _starttime = int(request.form['starttime'])
                _endtime = int(request.form['endtime'])
                try:
                    geocode_result = gmaps.geocode(_address)
                    if len(geocode_result) == 0:
                        raise Exception
                    #get the lat,long of the address
                    _addresspoint = geocode_result[0]['geometry']['location'].values()[0], geocode_result[0]['geometry']['location'].values()[1]
                    #the _addresspoint1 tuple is flipped around because PostGIS uses long,lat instead of lat,long
                    cur.execute("SELECT ST_SetSRID(ST_MakePoint('{}', '{}'), 4326)".format(_addresspoint[1],_addresspoint[0]))
                    _geog = cur.fetchall()[0][0]
                    if _starttime >= _endtime:
                        raise Exception
                except:
                    error = "Address/timing is invalid."
                    return render_template('new.html', error = error)
                else:
                    cur.execute("INSERT INTO addresses (username, address, addresspoint, starttime, endtime, geog)\
                    VALUES('{}', '{}', '{}', '{}', '{}', '{}')".format(session['username'], _address, _addresspoint, _starttime, _endtime, _geog))
                    con.commit()
                    return redirect('user/'+ session['username'] )
            return render_template('user.html')
        return render_template('new.html', username = username)
    return render_template('index.html')

def acknowledge_requestor(phonenumber):
    client.messages.create(
    body = "A medically trained personnel is on the way.",
    to = phonenumber,
    from_ = "+14245438814",
    )   

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8080)

