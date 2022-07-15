import psycopg2
import json
from datetime import datetime, timezone

id = 1
# DATABASE CONNECTION CREDENTIALS
_host='proxy19.rt3.io'
_port='30390'
_db='measures'
_user='fttech'
_pass='Qcn@ZNiq1Q2Cv1LXJ$EQ'

con = psycopg2.connect(host=_host, port=_port, database=_db, user=_user, password=_pass)
cur = con.cursor()

try:
    cur.execute('SELECT id FROM plot ORDER BY ID DESC LIMIT 1')
    recset = cur.fetchall()
    if len(recset) != 0:
        id = recset[0][0] + 1
except:
    con.close()
    con = psycopg2.connect(host=_host, port=_port, database=_db, user=_user, password=_pass)
    cur = con.cursor()
    sql = 'create table plot(id serial primary key, data JSON, points_numb INTEGER, profiles_numb INTEGER, standard_view varchar(100), front_view varchar(100), side_view varchar(100));'
    cur.execute(sql)

x = [0,1,2,3,4]
y = [0,1,2,3,4]

data = '{"x": %s,"y": %s,"type": "scatter"}' % (x,y)
#data = json.loads(data)
points_numb = 1296
profiles_numb = 12500
standard_img = '<img width="100%c" src="/public/img/3D/standard%d.png">' % ('%',id)
front_img = '<img width="100%c" src="/public/img/3D/front%d.png">' % ('%',id)
side_img = '<img width="100%c" src="/public/img/3D/side%d.png">' % ('%',id)
sql = "insert into plot values (default,'%s','%s','%s','%s','%s','%s')" % (data, points_numb, profiles_numb, standard_img, front_img, side_img)
cur.execute(sql)
con.commit()

cur.execute('SELECT * FROM plot')
recset = cur.fetchall()

for rec in recset:
    print (rec)

con.close()
