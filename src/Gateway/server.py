import socket
from datetime import datetime

protocol = 'UDP'
host = '192.168.1.2'
port = 55000
address = (host,port)
buffer = 1024

# convert the string bytes to the hexadecimal string
def getFloat(bytestring, start):

	payload = []

	for c in range(start, start+4, 1):
		if bytestring[c] != 0:
			payload.append(hex(bytestring[c]).replace("0x", ""))

	if len(payload) > 0:

		payload = ''.join(payload)

		return struct.unpack('<f', bytes.fromhex(payload))[0]

	else:
		return 0

# ----------------- Conectando-se -----------------
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(address)

# --------------- Aguarda mensagens ---------------
print ('Aguardando mensagens...')

while True:
# ------------- Leitura das mensagens -------------
    bytesAddressPair = sock.recvfrom(buffer)
    area = getFloat(bytesAddressPair[0],0)
    distancia = getFloat(bytesAddressPair[0],4)
    client_address = bytesAddressPair[1]

# ------------- Salva mensagens em arquivo -------------
    #abre o arquivo de log
    arq = open("data.log", "a")
    # Escreve a hora
    arq.write('[' + str(datetime.today()) + ']')
    # Escreve os dados
    arq.write(" | Area: " + str(area) + " | Distancia: " + str(distancia) + " Client: " + str(client_address) + "\n")
    print ("Area: ", area, " Distancia: ", distancia ," Client: ", client_address)
