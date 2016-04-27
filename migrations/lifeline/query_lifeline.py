import psycopg2 as db
import sys
import googlemaps
import imp
from datetime import datetime
import urllib3
import certifi
import urllib3.contrib.pyopenssl
from base64 import b64encode


urllib3.contrib.pyopenssl.inject_into_urllib3()
# To allow python 2.7.6 to send safe http requests
http = urllib3.PoolManager(
    cert_reqs='CERT_REQUIRED', # Force certificate check.
    ca_certs=certifi.where(),  # Path to the Certifi bundle.
)
con = db.connect(database="lifeline", user="postgres", password="seetoh", host="localhost")
print 'Success!'
cur = con.cursor()


# config = imp.load_source('config', '../sensitive_data/config.py')
# gmaps = googlemaps.Client(key=config.GMAPS_KEY)
ses = {}
_username = 'admin'
request_id = 88
number = '+15107100732'
cur.execute("SELECT lastrequest FROM medics WHERE phonenumber = '{}'".format(number))
print 'success'
result = cur.fetchall()[0][0]
print result
# print int(result)
# result = cur.fetchall()
# for i in range(len(result)):
#     # encode all images
#     result[i] = (result[i][0], b64encode(result[i][1]))
# print type(result[0][0])
# ses = {}
# for i in range(len(result)):
#     ses[i] = result[i]
    
# print ses
# for i in ses:
#     print type(i)
# con.commit()
# con.close()