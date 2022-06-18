"""
Generate 3D Surfaces reading parameters of .txt FILES

Autor: Jhonatan Da Silva Cruz
Date: 2022-06-18

"""

import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
from scipy.spatial import ConvexHull
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
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

while file_numb < 1000:

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
				last_lecture_z = 250-content_z
				
				x.append(last_lecture_x)
				z.append(last_lecture_z)

				if(flag_0 == False):
					flag_0 = True
					
					for i in range(count-1, -1, -1):
						x[i] = last_lecture_x
						z[i] = last_lecture_z

			count = count + 1

	############ Some configurations ############

	xpoints = np.array(x)
	ypoints = np.zeros(count) + (file_numb*2)
	zpoints = np.array(z)

	X = np.append(X,xpoints)
	Y = np.append(Y,ypoints)
	Z = np.append(Z,zpoints)
	################### AREA ###################

	#area = np.trapz(zpoints, xpoints)/1000000
	#print("area = %f m²" % (area))

	################# 3D PLOT ###################

	file_numb = file_numb + 1

# A = np.reshape(A, (number of profiles, points/profile))
# A = np.reshape(A,(file_numb,1296))

X = np.reshape(X,(file_numb,1296))
Y = np.reshape(Y,(file_numb,1296))
Z = np.reshape(Z,(file_numb,1296))

#ax.plot_wireframe(X, Y, Z)
ax.plot_surface(X, Y, Z)
#plt.ylim([400, 600])
plt.show()
#buf = "IMG_3D/3d_surface_lim.png"
#plt.savefig(buf)
#plt.close(fig)
