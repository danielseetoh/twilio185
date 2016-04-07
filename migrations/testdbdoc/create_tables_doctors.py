import psycopg2 as db
import sys

try:
    con = db.connect(database="testdbdoc", user="postgres", password="seetoh", host="localhost")
    print 'Success!'
    
    cur = con.cursor()
        
    try:
        # For now address will simply be a zipcode. Will add support for proper addresses soon.
        cur.execute("CREATE TABLE doctors ( \
        username varchar PRIMARY KEY NOT NULL, \
        password varchar NOT NULL, \
        phonenumber varchar NOT NULL, \
        zipcode varchar NOT NULL, \
        active boolean NOT NULL);") 
        
        # For now address will simply be a zipcode. Will add support for proper addresses soon.
        # In the real app, need to get the actual specific gps location and find doctors who 
        # are within the general vicinity and can arrive within 8 minutes or less.
        # Average response time of an ambulance is 11 minutes.
        cur.execute("CREATE TABLE requests ( \
        id bigserial PRIMARY KEY NOT NULL, \
        phonenumber varchar NOT NULL, \
        zipcode varchar NOT NULL, \
        responded boolean NOT NULL );") 
        
        
        print 'Table created successfully!'
    except:
        print 'Failed to create tables.'


    con.commit()
    con.close()
except:
    print 'Failed to connect to database.'