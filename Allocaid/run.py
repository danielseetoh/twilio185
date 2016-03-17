import os
from flask import Flask, request, Response, render_template
from twilio import twiml
from twilio.rest import TwilioRestClient
import imp


#loads account_sid and auth_token from private space
config = imp.load_source('config', '../sensitive_data/config.py')


TWILIO_ACCOUNT_SID = config.TWILIO_ACCOUNT_SID
TWILIO_AUTH_TOKEN = config.TWILIO_AUTH_TOKEN
app = Flask(__name__)

client = TwilioRestClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

recipients = ['+15107100732']

@app.route('/receivemessage', methods = ['POST', 'GET'])
def receivemessage():
    body = request.values.get('Body', None)
    fromnum = request.values.get('From', None)
    r = twiml.Response()
    
    if body == 'YES':
        r.message("Thank you for replying.")
    elif body == 'NO':
        r.message("Sorry to hear this.")
    else:
        r.message("Invalid response.")
    
    #has to be valid twiml
    return str(r)

@app.route('/sendmessage', methods = ['POST', 'GET'])   
def sendmessage():
    for person in recipients:
        client.messages.create(
        body = "Test Message",
        mediaurl = "http://asdf",
        to = person,
        from_ = "+14245438814",
        )
    return('Messages sent')

@app.route('/voice', methods=['GET', 'POST'])
def voice():
    resp = twiml.Response()
    resp.say("Bobie loves Sharmaine")
    return str(resp)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8080)