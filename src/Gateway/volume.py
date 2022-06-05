import numpy as np
from scipy.spatial import ConvexHull
import time

velocity = 0.4 # m/s
volume = 0 # volume acumulado
tic = time.perf_counter() # Tempo inicial
timer = 2 # Tempo de leitura
surface0 = [[-2,0,0]]
surface1 = [[-2,1,0]]
surface = 0 # surface number
y = 0 # comprimento do objeto 3D
control = 0 #variável de controle de volume

if __name__ == '__main__':
	while(1):

		tac = time.perf_counter() # Tempo de observação
		delta_t = tac - tic # Variação de tempo

		if(delta_t >= timer):
		
			if(surface == 0):
				if control == 0:
					surface0 = np.append(surface0, np.asarray([[0,y,1]]), axis=0)
					surface0 = np.asarray(surface0)

					surface0 = np.append(surface0, np.asarray([[2,y,0]]), axis=0)
					surface0 = np.asarray(surface0)
				else:
					surface0 = surface1

				# Atualiza valores
				surface = 1
				y = velocity * delta_t # comprimento do objeto 3D

			else:

				surface1 = np.append(surface1, np.asarray([[0,y,1]]), axis=0)
				surface1 = np.asarray(surface1)

				surface1 = np.append(surface1, np.asarray([[2,y,0]]), axis=0)
				surface1 = np.asarray(surface1)

				#Calcula Volume
				volume = volume + ConvexHull(np.append(surface0, surface1, axis=0)).volume
				print("Volume = " + str(volume) + "\n")
			
				# Atualiza valores
				surface = 0
				y = 0 # comprimento do objeto 3D
			
			control += 1
				
			#print("Delta t = " + str(delta_t) + "\n")

			tic = time.perf_counter()


