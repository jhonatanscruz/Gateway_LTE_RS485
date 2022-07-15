"""
#######################################################
#                                                     #
#   Generates 3D Surfaces reading 2D Profiles         #
#   from RF627 SMART Sensor                           #
#                                                     #
#   Autor: Jhonatan Da Silva Cruz                     #
#   Date: 2022-06-21                                  #
#   Last-Update: 2022-07-08                           #
#                                                     #
#######################################################
"""

#######################################################
#                                                     #
#                      LIBRARIES                      #
#                                                     #
#######################################################
import sys
sys.path.append("../../../RF62X-Wrappers/Python/")
import time
from datetime import datetime
from PYSDK_SMART import *
import matplotlib.pyplot as plt
from matplotlib import cm
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
#from scipy.spatial import ConvexHull
#from mpl_toolkits.mplot3d.art3d import Poly3DCollection

#######################################################
#                                                     #
#                  GLOBAL FUNCTIONS                   #
#                                                     #
#######################################################
"""
#################################################################################
#                                                                               #
#   Calculates the mean height of a conveyor reading the "conveyor.txt" file    #
#   The .txt file can be generated using the "Conveyor_Calibrating.py" program	#
#   The mean height of conveyor is returned as a float value                    #
#                                                                               #
#################################################################################
"""
def getConveyorHeight():
    my_file = open("conveyor.txt", "r")

    content_list = my_file.readlines()
    h_conveyor_sum = 0
    count = 0

    for line in content_list:
        content_z = float(line)

        if (content_z == 0):
            pass

        else:
            h_conveyor_sum = h_conveyor_sum + content_z
            count = count + 1

    h_conveyor_mean = h_conveyor_sum/count

    return h_conveyor_mean

"""
#################################################################################
#                                                                               #
#                      Functions to manipulate Postgres DB                      #
#                                                                               #
#################################################################################
"""
def startDB(_host, _db, _user, _pass):
    db = psycopg2.connect(host=_host, database=_db, user=_user, password=_pass)
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

#######################################################
#                                                     #
#                        MAIN                         #
#                                                     #
#######################################################
if __name__ == '__main__':

    #################################################
    #                                               #
    #                     SETUP                     #
    #                                               #
    #################################################

    ############### Main Variables ################
    zero_points=True
    realtime=True
    numb = 0                            # Number of each profile points
    profile_numb = 0                    # Number of current profile
    point_numb = 0                      # Number of current point
    h_conveyor = getConveyorHeight()    # Conveyor Height to calibrate measures
    last_lecture_x = 0                  # Last x coordinate stored
    last_lecture_z = 0                  # Last z coordinate stored
    y = 0                               # Initial y coordinate value
    delta_y = 0.005                     # Difference between 2 profiles in milimeters
    flag_0 = False                      # Returns True when a non zero height value is found
    X = []	                            # Matrice X for 3D Surface
    Y = []	                            # Matrice Y for 3D Surface
    Z = []	                            # Matrice Z for 3D Surface
    dump = []                           # Stores profile readings
    timestamp = []                      # Stores timestamp
    teste = 20

    ############# Initialize sdk library ############
    sdk_init()

    ######### Get scanner from scanners list ########
    list_scanners=search()

    #################################################
    #                                               #
    #              SENSOR INFORMATION               #
    #                                               #
    #################################################

    #info = get_info(scanner, kSERVICE)

    #################################################
    #                                               #
    #           VERIFY SENSOR CONNECTION            #
    #                                               #
    #################################################
    for scanner in list_scanners:

        ##### Establish connection to the RF627 device by Service Protocol #####
        is_connected = connect(scanner)
        if (not is_connected):
            print("Failed to connect to scanner!")
            continue

	    #################################################
	    #                                               #
	    #           GET PROFILES FROM SENSOR            #
	    #                                               #
	    #################################################

        ###### Get profile from scanner's data stream by Service Protocol ######
        init = datetime.today()
        while profile_numb <= 10000: # GETTING 6000 PROFILES FROM SENSOR
            start = datetime.today() # Starts Profile Reading
            profile = get_profile2D(scanner,zero_points,realtime,kSERVICE)
            if (profile is not None):
                profile_numb = profile_numb + 1
                dump.append(profile) # Get 2D Profile from Sensor
                timestamp.append(start)
                timestamp.append(datetime.today())
        end = datetime.today()
        diff = end - init
        about = open("TESTES/%d/about.txt" % (teste), "a")
        about.write("Leitura Terminada! Demorou: %f segundos para a leitura de %d perfis\n" % (diff.total_seconds(),profile_numb))
        init = datetime.today()
	    #################################################
	    #                                               #
	    #             PROFILES PROCESSING               #
	    #                                               #
	    #################################################
        for profile in dump:
            if (profile is not None):
                profile_data_type=profile['header']['data_type']

                if profile_data_type == PROFILE_DATA_TYPES.PROFILE:
                    numb = profile['points_count']

                if 'points' in profile:
                    for j in range(numb):
                        content_x = float(profile['points'][j].x)
                        content_z = float(profile['points'][j].z)

                        if ((content_x == 0 and content_z== 0)):
                            if(flag_0 == False):
                                X.append(content_x)
                                Z.append(content_z)

                            else: # Flag 0 is True, it means there is a non NULL height value stored in last_lecture variables
                                X.append(last_lecture_x)
                                Z.append(last_lecture_z)

                        else:
                            last_lecture_x = content_x/10
                            last_lecture_z = (content_z - h_conveyor)/10

                            if last_lecture_z < 0:
                                last_lecture_z = 0

                            X.append(last_lecture_x)
                            Z.append(last_lecture_z)

                            if(flag_0 == False):
                                flag_0 = True

                                for i in range(j-1, -1, -1):
                                    X[i] = last_lecture_x
                                    Z[i] = last_lecture_z

                        Y.append(y)

                    y = y + delta_y

        #################################################
        #                                               #
        #   CONVERTING VECTORS TO MATRICES OF 3D MODEL  #
        #                                               #
        #################################################
        end = datetime.today()
        diff = end - init
        about.write("Primeiro processamento Terminado!! Demorou: %f segundos\n" % (diff.total_seconds()))

        init = datetime.today()
        # Armazenando valores lidos para X
        arq = open("TESTES/%d/X.txt" % (teste), "a")
        for i in X:
            arq.write(str(i) + "\n")
        arq.close
        end = datetime.today()
        diff = end - init
        about.write("Salvou arq X!! Demorou: %f segundos\n" % (diff.total_seconds()))

        init = datetime.today()
        # Armazenando valores lidos para Y
        arq = open("TESTES/%d/Y.txt" % (teste), "a")
        for i in Y:
            arq.write(str(i) + "\n")
        arq.close
        end = datetime.today()
        diff = end - init
        about.write("Salvou arq Y!! Demorou: %f segundos\n" % (diff.total_seconds()))

        init = datetime.today()
        # Armazenando valores lidos para Z
        arq = open("TESTES/%d/Z.txt" % (teste), "a")
        for i in Z:
            arq.write(str(i) + "\n")
        arq.close
        end = datetime.today()
        diff = end - init
        about.write("Salvou arq Z!! Demorou: %f segundos\n" % (diff.total_seconds()))

        init = datetime.today()
        # Armazenando valores lidos para timestamp
        arq = open("TESTES/%d/timestamp.txt" % (teste), "a")
        aux = 0
        last_datetime = datetime.today()
        for i in timestamp:
            if aux == 0:
                last_datetime = i
                arq.write(str(i) + "\n")
                aux = aux + 1

            else:
                diff = i - last_datetime
                arq.write(str(i) + " | Diferença para o anterior: " + str(diff.total_seconds() * 1000) + " msec\n")
                last_datetime = i
                arq.write("\n")
                aux = 0

        arq.close
        end = datetime.today()
        diff = end - init
        about.write("Salvou arq Timestamp!! Demorou: %f segundos\n" % (diff.total_seconds()))

        init = datetime.today()
        X = np.reshape(X,(profile_numb, numb))
        end = datetime.today()
        diff = end - init
        about.write("Processou Numpy X!! Demorou: %f segundos\n" % (diff.total_seconds()))

        init = datetime.today()
        Y = np.reshape(Y,(profile_numb, numb))
        end = datetime.today()
        diff = end - init
        about.write("Processou Numpy Y!! Demorou: %f segundos\n" % (diff.total_seconds()))

        init = datetime.today()
        Z = np.reshape(Z,(profile_numb, numb))
        end = datetime.today()
        diff = end - init
        about.write("Processou Numpy Z!! Demorou: %f segundos\n" % (diff.total_seconds()))

        ##############################################################################
        #                                                                            #
        #                           PLOTAGEM DO MODELO 3D                            #
        #                                                                            #
        ##############################################################################
        fig = plt.figure(figsize=(10, 6))#figsize=(4,4))
        ax = fig.add_subplot(111, projection='3d')
        #ax.plot_wireframe(X, Y, Z,cmap=cm.hot)
        surf = ax.plot_surface(X, Y, Z, cmap=cm.hot, linewidth=5, antialiased=True)
        #plt.ylim([100, 125])
        plt.xlim([-10, 10])
        ax.set_zlim(0, 25)
        #ax.view_init(0, 0)
        #plt.axis('off')
        plt.show()

        # CASO DESEJE SALVAR EM IMAGEM
        #init = datetime.today()
        #buf = "IMG_3D_10x6.png"
        #plt.savefig(buf)
        #plt.close(fig)
        #end = datetime.today()
        #diff = end - init
        #about.write("Salvou a imagem .PNG!! Demorou: %f segundos \n" % (diff.total_seconds()))
        #################################################
        #                                               #
        #           DISCONNECT SENSOR AND SDK           #
        #                                               #
        #################################################

        ######### Disconnect from scanner #########
        disconnect(scanner)

    ######### Cleanup resources allocated with sdk_init() #########
    sdk_cleanup()
