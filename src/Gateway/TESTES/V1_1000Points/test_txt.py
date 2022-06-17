import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
from scipy.spatial import ConvexHull
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from datetime import datetime

file_numb = 0

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
				pass
			else:
				x.append(content_x)
				z.append(250-content_z)
				count = count + 1

	############ Some configurations ############

	#z[0] = 0
	#z[count-1] = 0

	xpoints = np.array(x)
	ypoints = np.zeros(count)
	zpoints = np.array(z)

	################### AREA ###################

	#area = np.trapz(zpoints, xpoints)/1000000
	#print("area = %f m²" % (area))

	################# 3D PLOT ###################

	ax.plot(xpoints,ypoints+(file_numb*2),zpoints,c="blue")
	file_numb = file_numb + 1
#plt.ylim([400, 600])
#plt.show()
buf = "IMG_3D/3d.png"
plt.savefig(buf)
plt.close(fig)

