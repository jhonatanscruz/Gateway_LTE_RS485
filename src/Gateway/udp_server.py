# UDP SERVER to receive messages sending by CAPICOM Laser RF627SMART SERIES
# Created April 2022
# By FTTech Developer Jhonatan Cruz

import socketserver, threading, time, struct, serial
from datetime import datetime

# -------------------------------------------------------------- #
				###### VARIÁVEIS GLOBAIS ######
# -------------------------------------------------------------- #
debug = 0
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

# -------------------------------------------------------------- #
			############ FUNÇÕES THREAD ############
# -------------------------------------------------------------- #
class ThreadedUDPRequestHandler(socketserver.BaseRequestHandler):
    area, distancia, pulsos = '', '', ''

    def handle(self):
        data = self.request[0].strip()
        socket = self.request[1]
        current_thread = threading.current_thread()
        area = getFloat(data, 0)
        volume = getFloat(data, 4)
        pulsos = getInt(data, 8)
        if debug == 1:
            print("[{}] : client : {}, wrote : {}, area : {}, volume : {}, pulsos : {}".format(datetime.today(), self.client_address, data, getFloat(data, 0), getFloat(data, 4), getInt(data, 8)))

        # ------------- Salva mensagens em arquivo -------------
        if area!='' and volume!='' and pulsos!='':
            # ------------- abre o arquivo de log -------------
            arq = open("data.log", "a")

            # ------------- Escreve a payload -------------
            arq.write(str(data) + "\n")

            # ------------- Escreve a hora -------------
            arq.write('[' + str(datetime.today()) + ']')

            # ------------- Escreve os dados -------------
            arq.write(" | Area: " + str(area) + " | Volume: " + str(volume) + " | Pulsos: " + str(pulsos) + " | Client: " + str(self.client_address) + "\n")

class ThreadedUDPServer(socketserver.ThreadingMixIn, socketserver.UDPServer):
    pass

# -------------------------------------------------------------- #
				############ MAIN ############
# -------------------------------------------------------------- #
if __name__ == "__main__":
# ----------------- Wait for Ethernet connection ----------------- #
    time.sleep(90) # wait 90 seconds before initialize

# ----------------- IP, PORTA ----------------- #
    HOST, PORT = "192.168.1.2", 55000

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
