"""
Generate 3D Surfaces reading parameters of .txt FILES

Autor: Jhonatan Da Silva Cruz
Date: 2022-06-18

"""

import matplotlib.pyplot as plt
from matplotlib import cm
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
from datetime import datetime

# 1296 Points/Profile

file_numb = 0
last_lecture_x = 0
last_lecture_z = 0
X = []
Y = []
Z = []

fig = plt.figure()#figsize=(4,4))
ax = fig.add_subplot(111, projection='3d')


##############################################################################
#                                                                            #
#          CALIBRAÇÃO DAS MEDIDAS DE ACORDO COM A ALTURA DA ESTEIRA          #
#                                                                            #
##############################################################################
buf = "esteira.txt"
my_file = open(buf, "r")

content_list = my_file.readlines()
h_esteira_sum = 0
count = 0

for line in content_list:
	content_z = float(line.split(' ')[1].replace("z=",""))

	if (content_z == 0):
		pass

	else:
		h_esteira_sum = h_esteira_sum + (250-content_z)
		count = count + 1

h_esteira_mean = h_esteira_sum/count # Altura média da esteira

##############################################################################
#                                                                            #
#       GERAÇÃO DOS VETORES DO MODELO A PARTIR DA LEITURA DOS ARQUIVOS       #
#                                                                            #
##############################################################################

while file_numb <= 2000:

	buf = "profile_%d.txt" %(file_numb)

	my_file = open(buf, "r")

	content_list = my_file.readlines()
	x = []
	z = []
	count = 0
	aux = 0
	flag_0 = False #Flag de descoberta de um valor NÃO NULO

	for line in content_list:
		if aux == 0:
			date = datetime.strptime(line, "%Y-%m-%d %H:%M:%S.%f\n")
			aux = aux + 1

		elif aux == 1:
			enc_count = int(line)
			aux = aux + 1

		else:
			content_x = float(line.split(' ')[0].replace("x=",""))
			content_z = float(line.split(' ')[1].replace("z=",""))

			if ((content_x == 0 and content_z== 0)):
				if(flag_0 == False):
					x.append(content_x)
					z.append(content_z)

				else: # Flag 0 é True, ou seja, já havia encontrado valor NÃO NULO, mas voltou a ser NULA
					x.append(last_lecture_x)
					z.append(last_lecture_z)
					
			else:
				last_lecture_x = content_x
				last_lecture_z = (250-content_z) - h_esteira_mean
				
				if last_lecture_z < 0:
					last_lecture_z = 0

				x.append(last_lecture_x)
				z.append(last_lecture_z)

				if(flag_0 == False):
					flag_0 = True
					
					for i in range(count-1, -1, -1):
						x[i] = last_lecture_x
						z[i] = last_lecture_z

			count = count + 1

	############ Some configurations ############ 

	x = np.array(x)
	y = np.zeros(count) + (file_numb*0.1)
	z = np.array(z)

	X = np.append(X,x)
	Y = np.append(Y,y)
	Z = np.append(Z,z)

	################### AREA ###################

	#area = np.trapz(zpoints, xpoints)/1000000
	#print("area = %f m²" % (area))

	################# 3D PLOT ###################

	file_numb = file_numb + 1

##############################################################################
#                                                                            #
#              CONVERSÃO DOS VETORES PARA MATRIZES DO MODELO 3D              #
#                                                                            #
##############################################################################

# A = np.reshape(A, (number of profiles, points/profile))
# A = np.reshape(A,(file_numb,1296))

X = np.reshape(X,(file_numb,count))
Y = np.reshape(Y,(file_numb,count))
Z = np.reshape(Z,(file_numb,count))

##############################################################################
#                                                                            #
#                           PLOTAGEM DO MODELO 3D                            #
#                                                                            #
##############################################################################

#ax.plot_wireframe(X, Y, Z)
surf = ax.plot_surface(X, Y, Z, cmap=cm.hot, linewidth=0, antialiased=True)
plt.ylim([105, 112])
ax.set_zlim(0, 100)
plt.show()

# CASO DESEJE SALVAR EM IMAGEM

#buf = "IMG_3D/3d_surface_lim.png"
#plt.savefig(buf)
#plt.close(fig)
