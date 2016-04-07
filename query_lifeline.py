import psycopg2 as db
import sys
import googlemaps
import imp
from datetime import datetime
import urllib3
import certifi
import urllib3.contrib.pyopenssl
urllib3.contrib.pyopenssl.inject_into_urllib3()
# To allow python 2.7.6 to send safe http requests
http = urllib3.PoolManager(
    cert_reqs='CERT_REQUIRED', # Force certificate check.
    ca_certs=certifi.where(),  # Path to the Certifi bundle.
)
con = db.connect(database="lifeline", user="postgres", password="seetoh", host="localhost")
print 'Success!'
cur = con.cursor()
# phonenumber = '412341234'
# zipcode = '94720'
# request_id = '1'
# _username = 'asdfa'
# infolist = ['Singapore', (1.352083, 103.819836), 4, 9, '0101000020E610000057056A3178F459401EA4A7C821A2F53F']
# cur.execute("INSERT INTO addresses (username, address, addresspoint, starttime, endtime, geom)\
# VALUES('{}', '{}', '{}', '{}', '{}', '{}')".format(_username, infolist[0], infolist[1], infolist[2], infolist[3], infolist[4]))

config = imp.load_source('config', '../sensitive_data/config.py')
gmaps = googlemaps.Client(key=config.GMAPS_KEY)
ses = {}
_username = 'danielseetoh'
cur.execute("SELECT address, starttime, endtime FROM addresses where username = '%s'" % (_username))
result = cur.fetchall()
ses = {}
for i in range(len(result)):
    ses[i] = result[i]
    
print ses
for i in ses:
    print type(i)
# geocode_result = gmaps.geocode('Oakland, California')
# _addresspoint = geocode_result[0]['geometry']['location'].values()[0], geocode_result[0]['geometry']['location'].values()[1]
# print _addresspoint

# cur.execute("SELECT ST_SetSRID(ST_MakePoint('{}', '{}'), 4326)".format(_addresspoint[1],_addresspoint[0]))
# _geom = cur.fetchall()[0][0]
# print _geom
# print datetime.astimezone.now().hour
# SEARCH_RADIUS = 400.0

# cur.execute("SELECT DISTINCT ON (medics.username) medics.username FROM medics,addresses WHERE medics.username = addresses.username AND medics.active = True AND ST_DWithin(addresses.geog, '{}', '{}') AND addresses.starttime<= '{}' AND addresses.endtime > '{}'".format(_geom, SEARCH_RADIUS, datetime.now().hour, datetime.now().hour))
# print datetime.now().hour
# doctor_phone_numbers = cur.fetchall()
# print doctor_phone_numbers
# maybe save the addresses as geographies instead of geometries
# cur.execute("SELECT DISTINCT ON (username) username FROM addresses WHERE ST_DWithin(addresses.geog, '{}', {})".format(_geom, SEARCH_RADIUS))
# doctor_phone_numbers = cur.fetchall()
# print doctor_phone_numbers
# cur.execute("INSERT INTO addresses (geom) VALUES ('{}')".format(testcoord))
# responded = cur.fetchall()[0][1]
# print responded

# cur.execute("SELECT * FROM doctors WHERE username = 'danielseetoh' and password = 'password123' ")
# request_fields = cur.fetchall()
# if request_fields:
#     print 'logged in'
# else:
#     print 'Wrong username/password'
# numbers = map(str, request_fields)
# for num in request_fields:
#     print num[0]
    


# con.commit()
# con.close()