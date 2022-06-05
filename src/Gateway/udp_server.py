import socketserver, threading, time, struct, serial
from datetime import datetime

# -------------------------------------------------------------- #
				###### VARIÁVEIS GLOBAIS ######
# -------------------------------------------------------------- #
debug = 0
# -------------------------------------------------------------- #
	###### Função de decodificação dos dados recebidos ######
# -------------------------------------------------------------- #
def getFloat(bytestring, start):
	payload = []

	for c in range(start, start+4, 1):
		if bytestring[c] > 15:
			payload.append(hex(bytestring[c]).replace("0x", ""))

	if len(payload) == 4:

		payload = ''.join(payload)

		return struct.unpack('<f', bytes.fromhex(payload))[0]

	else:
		return 0

# -------------------------------------------------------------- #
			############ FUNÇÕES THREAD ############
# -------------------------------------------------------------- #
class ThreadedUDPRequestHandler(socketserver.BaseRequestHandler):
    area, distancia = '', ''

    def handle(self):
        data = self.request[0].strip()
        socket = self.request[1]
        current_thread = threading.current_thread()
        area = getFloat(data, 0)
        distancia = getFloat(data, 4)
        if debug == 1:
            print("[{}] : client : {}, wrote : {}, area : {}, distancia : {}".format(datetime.today(), self.client_address, data, getFloat(data, 0), getFloat(data, 4)))

        # ------------- Salva mensagens em arquivo -------------
        if area!='' or distancia!='':
            # ------------- abre o arquivo de log -------------
            arq = open("data.log", "a")

            # ------------- Escreve a payload -------------
            arq.write(str(data) + "\n")

            # ------------- Escreve a hora -------------
            arq.write('[' + str(datetime.today()) + ']')

            # ------------- Escreve os dados -------------
            arq.write(" | Area: " + str(area) + " | Distancia: " + str(distancia) + " | Client: " + str(self.client_address) + "\n")

class ThreadedUDPServer(socketserver.ThreadingMixIn, socketserver.UDPServer):
    pass

# -------------------------------------------------------------- #
				############ MAIN ############
# -------------------------------------------------------------- #
if __name__ == "__main__":

# ----------------- IP, PORTA ----------------- #
    HOST, PORT = "192.168.100.9", 9090

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
