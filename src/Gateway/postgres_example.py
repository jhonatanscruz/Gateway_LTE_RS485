import psycopg2
import json
from datetime import datetime, timezone

con = psycopg2.connect(host='', port='',database='measures',
user='fttech', password='')
cur = con.cursor()
sql = 'create table teste (id serial primary key)'
cur.execute(sql)
dt = datetime.now(timezone.utc)
sql = "insert into sensor values (default,'%s','28.68')" % (dt)
cur.execute(sql)
con.commit()
cur.execute('SELECT curr_volume FROM metrics ORDER BY ID DESC LIMIT 1')
recset = cur.fetchall()

for rec in recset:
    print (rec[0])
    print (type(rec[0]))

con.close()
