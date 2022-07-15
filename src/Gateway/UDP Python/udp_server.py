# UDP SERVER to receive messages sending by CAPICOM Laser RF627SMART SERIES
# Created April 2022
# By FTTech Developer Jhonatan Cruz

import socketserver, threading, time, struct, serial, psycopg2, math
from datetime import datetime

# -------------------------------------------------------------- #
				###### VARIÁVEIS GLOBAIS ######
# -------------------------------------------------------------- #
debug = 0

# ----------------- IP, PORTA ----------------- #
HOST, PORT = "192.168.1.2", 55000

# DB SENDING INFORMATION
send_to_DB = 3 #seconds
last_time_sent = 0

# DATABASE CONNECTION CREDENTIALS
_host='localhost'
_port='5432'
_db='measures'
_user='fttech'
_pass='Qcn@ZNiq1Q2Cv1LXJ$EQ'

# DATA INFORMATION
volume_accumulated = 0

# -------------------------------------------------------------- #
	###### Functions to decode data recieved ######
# ---------------------------------------------------------------
def getFloat(bytestring, start):
    payload = b''

    for c in range(start, start+4, 1):
        payload += bytestring[c].to_bytes(1,'big')

    return struct.unpack('<f', payload)[0]

def getInt(bytestring, start):
    payload = b''

    for c in range(start, start+4, 1):
        payload += bytestring[c].to_bytes(1,'big')

    return int.from_bytes(payload, byteorder='little')


"""
#################################################################################
#                                                                               #
#                      Functions to manipulate Postgres DB                      #
#                                                                               #
#################################################################################
"""
def startDB(_host, _port, _db, _user, _pass):
    db = psycopg2.connect(host=_host, port=_port, database=_db, user=_user, password=_pass)
    return db

def createInsertDB(db, sql):
    cur = db.cursor()
    cur.execute(sql)
    db.commit()

def getFromDB(db, sql):
    cur = db.cursor()
    cur.execute(sql)
    recset = cur.fetchall()
    return recset

def closeDB(db):
    db.close()

# -------------------------------------------------------------- #
			############ FUNÇÕES THREAD ############
# -------------------------------------------------------------- #
class ThreadedUDPRequestHandler(socketserver.BaseRequestHandler):

    def handle(self):
        data = self.request[0].strip()
        socket = self.request[1]
        current_thread = threading.current_thread()
        area = getFloat(data, 0)
        volume = getFloat(data, 4)
        align_r = getFloat(data, 8)
        align_l = getFloat(data, 12)
        pulsos = getInt(data, 16)

        if fabs(149.5 - align_r) < 0.5:
            align_r = 0
        if fabs(149.5 - align_l) < 0.5:
            align_l = 0

        db = startDB(_host, _port, _db, _user, _pass)
        sql = f"insert into metrics values (default, '{volume}', '{align_r}', '{align_l}', '{datetime.today()}')"
        createInsertDB(db, sql)
        closeDB(db)

        if debug == 1:
            # ------------- Salva mensagens em arquivo -------------
            if area!='' and volume!='' and pulsos!='':
                # ------------- abre o arquivo de log -------------
                arq = open("data.log", "a")

                # ------------- Escreve a hora -------------
                arq.write('[' + str(datetime.today()) + ']')

                # ------------- Escreve os dados -------------
                arq.write(" | Area: " + str(area) + " | Volume: " + str(volume) + " | Rigth: " + str(align_r) + " | Left: " + str(align_l) + " | Pulsos: " + str(pulsos) + " | Client: " + str(self.client_address) + "\n")

class ThreadedUDPServer(socketserver.ThreadingMixIn, socketserver.UDPServer):
    pass

# -------------------------------------------------------------- #
				############ MAIN ############
# -------------------------------------------------------------- #
if __name__ == "__main__":
# ----------------- Wait for Ethernet connection ----------------- #
    #time.sleep(90) # wait 90 seconds before initialize

    #######################################################
    #                                                     #
    #                 START TABLE METRICS                 #
    #                                                     #
    #######################################################
    try:
        db = startDB(_host, _port, _db, _user, _pass)
        sql = 'SELECT id FROM metrics ORDER BY ID DESC LIMIT 1'
        db.cursor().execute(sql)
        closeDB(db)

    except:
        closeDB(db)
        db = startDB(_host, _port, _db, _user, _pass)
        sql = 'create table metrics(id SERIAL primary key, volume REAL, rigth_align REAL, left_align REAL, timestamp TIMESTAMP WITHOUT TIME ZONE);'
        createInsertDB(db, sql)
        closeDB(db)

    #######################################################
    #                                                     #
    #                UDP CONNECTION THREAD                #
    #                                                     #
    #######################################################

    server = ThreadedUDPServer((HOST, PORT), ThreadedUDPRequestHandler)
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True

    try:
        server_thread.start()
        if debug == 1:
            print("Server started at {} port {}".format(HOST, PORT))
        while True: time.sleep(100)
    except (KeyboardInterrupt, SystemExit):
        server.shutdown()
        server.server_close()
        exit()
