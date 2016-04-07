import psycopg2 as db
import sys

# try:
con = db.connect(database="lifeline", user="postgres", password="seetoh", host="localhost")
print 'Success!'

cur = con.cursor()
        
    # try:
# addresses of medics are stored in a address table, with foreign key username.
cur.execute("CREATE TABLE medics ( \
username varchar PRIMARY KEY NOT NULL, \
password varchar NOT NULL, \
phonenumber varchar NOT NULL, \
active boolean NOT NULL);") 

# For now address will simply be a zipcode. Will add support for proper addresses soon.
# In the real app, need to get the actual specific gps location and find doctors who 
# are within the general vicinity and can arrive within 8 minutes or less.
# Average response time of an ambulance is 11 minutes.
cur.execute("CREATE TABLE requests ( \
id bigserial PRIMARY KEY NOT NULL, \
phonenumber varchar NOT NULL, \
addresspoint point NOT NULL, \
responded boolean NOT NULL,\
geog GEOGRAPHY(POINT,4326));") 

# Static addresses of medical personnel. Each medical personnel can have more than 1 static address. 
# Stores active time from starttime to endtime in 24hr format.
cur.execute("CREATE TABLE addresses (\
username varchar REFERENCES medics(username),\
address varchar NOT NULL,\
addresspoint point NOT NULL,\
starttime integer NOT NULL,\
endtime integer NOT NULL,\
geog GEOGRAPHY(POINT,4326));") 

# Add a PostGIS column into the addresses and requests table for easy querying 
# cur.execute("SELECT AddGeometryColumn('addresses', 'geom', 4326, 'POINT', 2);")
# cur.execute("SELECT AddGeometryColumn('requests', 'geom', 4326, 'POINT', 2);")
        
#         print 'Table created successfully!'
#     except:
#         print 'Failed to create tables.'


con.commit()
con.close()
# except:
#     print 'Failed to connect to database.'