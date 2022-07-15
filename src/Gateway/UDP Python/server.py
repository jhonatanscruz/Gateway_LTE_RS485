#!/usr/bin/env python3
# UDP SERVER to receive messages sending by CAPICOM Laser RF627SMART SERIES
# Created April 2022
# Last Update: July 15th, 2022
# By Jhonatan Cruz from Fttech Software Team

import socket, threading, time, struct, serial, psycopg2, math
from datetime import datetime, timezone

"""
#################################################################
#                                                               #
#               Functions to decode received data               #
#                                                               #
#################################################################
"""
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
#################################################################
#                                                               #
#              Functions to manipulate Postgres DB              #
#                                                               #
#################################################################
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

"""
#################################################################
#                                                               #
#                       General Functions                       #
#                                                               #
#################################################################
"""

def now():
    return datetime.now(timezone.utc).replace(tzinfo=None)

def InitalSetup(sock, buffer):
    data = []
    read = sock.recvfrom(buffer)
    area = getFloat(read[0],0)
    pulse = getInt(read[0],12)
    time = now()

    data.append(area)
    data.append(pulse)
    data.append(time)

    return data

def calcVolume(last_area, current_area, last_pulse, current_pulse):
    mm2_to_m2 = 0.0000005 # Converts mm2 to m2
    pulse_to_m = 0.0001 # Converts each pulse to value in meters
    volume_aprox = 0.94 # Approximation from volume calculated to real value

    delta_pulse = current_pulse - last_pulse
    mean_area = ((current_area + last_area)/2) * mm2_to_m2 # m²
    volume = (mean_area * delta_pulse * pulse_to_m) * volume_aprox # Volume in m³

    return volume

def calcVelocity(delta_pulse, delta_time):
    pulse_to_m = 0.00005 # Converts each pulse to value in meters

    mean_pulse = sum(delta_pulse)/len(delta_pulse)
    mean_time = sum(delta_time)/len(delta_time)

    velocity = (mean_pulse * pulse_to_m) / mean_time # m/s

    return velocity
"""
##############################################
#                                            #
#                    MAIN                    #
#                                            #
##############################################
"""
if __name__ == "__main__":

    ##################################
    #                                #
    #        GLOBAL VARIABLES        #
    #                                #
    ##################################
    debug_0 = 0 # Print Debug
    debug_1 = 0 # TXT Debug
    send_to_DB = 4 #seconds
    volume_accumulated = 0
    pulse_accumulated = []
    delta_time_accumulated = []
    velocity = 0
    last_pulse_count = 0
    last_time_received = 0
    last_area_received = 0

    ############################################
    #                                          #
    #        UDP CONNECTION CREDENTIALS        #
    #                                          #
    ############################################
    HOST = ""
    PORT = 
    address = (HOST,PORT)
    buffer = 1024

    ###########################################
    #                                         #
    #        DB CONNECTION CREDENTIALS        #
    #                                         #
    ###########################################
    _host=''
    _port=''
    _db='measures'
    _user='fttech'
    _pass=''

    # ----------------- Wait for Ethernet connection ----------------- #
    #time.sleep(90) # wait 90 seconds before initialize

    #######################################################
    #                                                     #
    #                 START TABLE METRICS                 #
    #                                                     #
    #######################################################
    db = startDB(_host, _port, _db, _user, _pass)
    try:
        sql = 'SELECT id FROM metrics ORDER BY ID DESC LIMIT 1'
        db.cursor().execute(sql)
        closeDB(db)

    except:
        closeDB(db)
        db = startDB(_host, _port, _db, _user, _pass)
        sql = 'create table metrics(id SERIAL primary key, volume REAL, velocity REAL, right_align REAL, left_align REAL, timestamp TIMESTAMP WITHOUT TIME ZONE);'
        createInsertDB(db, sql)
        closeDB(db)

    #######################################################
    #                                                     #
    #                    UDP CONNECTION                   #
    #                                                     #
    #######################################################
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(address)

    # --------------- Aguarda mensagens ---------------
    if debug_0:
        print ('Aguardando mensagens...')

    # ------------- Initial Required Setup -------------
    setup = InitalSetup(sock, buffer)
    last_area_received = setup[0]
    last_pulse_count = setup[1]
    last_time_received = setup[2]

    init = now()

    while True:
        # ------------- Leitura das mensagens -------------
        data = sock.recvfrom(buffer)
        current_time = now()

        area = getFloat(data[0],0)
        right_align = getFloat(data[0],4)
        left_align = getFloat(data[0],8)
        pulse_count = getInt(data[0],12)
        client_address = data[1]

        ##### Metrics #####
        if pulse_count != last_pulse_count:
            # Volume Calculation and accumulate
            volume_accumulated = volume_accumulated + calcVolume(last_area_received, area, last_pulse_count, pulse_count)

            # Accumulate values in vectors of pulse and time to calculate mean velocity
            pulse_accumulated.append(pulse_count - last_pulse_count)
            delta_time_accumulated.append((current_time - last_time_received).total_seconds())

            ##### REFRESH VALUES #####
            last_area_received = area
            last_pulse_count = pulse_count
            last_time_received = current_time

            # Verify if time to send data to DB has been reached
            diff = current_time - init
            if (diff.total_seconds() >= send_to_DB):
                # Velocity Calculation
                velocity = calcVelocity(pulse_accumulated, delta_time_accumulated)

                # Converts from mm to cm
                right_align = right_align/10
                left_align = left_align/10

                # Some considerations
                if right_align <= 5:
                    left_align = -left_align

                if left_align <= -5:
                    right_align = -right_align
                    if left_align > 0:
                        left_align = -left_align

                ##### SEND TO DB #####
                db = startDB(_host, _port, _db, _user, _pass)
                sql = f"insert into metrics values (default, '{volume_accumulated}','{velocity}', '{right_align}', '{left_align}', '{now()}')"
                createInsertDB(db, sql)
                closeDB(db)

                ##### REFRESH VALUES #####
                init = now()
                pulse_accumulated = []
                delta_time_accumulated = []
                volume_accumulated = 0

            if debug_0:
                print(f"Client: {client_address} | Area: {area} | r_align: {right_align} | l_align: {left_align} | Pulse: {pulse_count}")

            if debug_1:
                # ------------- Salva mensagens em arquivo -------------
                if area!='' or distancia!='':
                    #abre o arquivo de log
                    arq = open("data.log", "a")
                    # Escreve a payload
                    arq.write(str(data[0]) + "\n")
                    # Escreve a hora
                    arq.write('[' + str(now()) + ']')
                    # Escreve os dados
                    arq.write(f" Client: {client_address} | Area: {area} | r_align: {right_align} | l_align: {left_align} | Pulse: {pulse_count}\n")
                    arq.close()
