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
from scipy.spatial import ConvexHull

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
    profiles_numb = 0                   # Number of profiles received
    points_numb = 0                     # Number of points in each profile
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
    align0 = []
    align1 = []
    id = 1
    path = "TESTES/01-07-2021/16"
    teste = 20

    # DATABASE CONNECTION CREDENTIALS
    _host='proxy17.rt3.io'
    _port='38835'
    _db='measures'
    _user='fttech'
    _pass='Qcn@ZNiq1Q2Cv1LXJ$EQ'

    #######################################################
    #                                                     #
    #                  START TABLE PLOT                   #
    #                                                     #
    #######################################################
    try:
        db = startDB(_host, _port, _db, _user, _pass)
        sql = 'SELECT id FROM plot ORDER BY ID DESC LIMIT 1'
        recset = getFromDB(db, sql)
        if len(recset) != 0:
            id = recset[0][0] + 1
        closeDB(db)

    except:
        closeDB(db)
        db = startDB(_host, _port, _db, _user, _pass)
        sql = 'create table plot(id SERIAL primary key, standard_view VARCHAR(100), side_view VARCHAR(100), front_view VARCHAR(100));'
        createInsertDB(db, sql)
        closeDB(db)

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
        sql = 'create table metrics(id SERIAL primary key, volume REAL, alignment REAL, profiles_numb INTEGER, points_numb INTEGER, timestamp TIMESTAMP WITHOUT TIME ZONE);'
        createInsertDB(db, sql)
        closeDB(db)

    #######################################################
    #                                                     #
    #                 START TABLE POINTS                  #
    #                                                     #
    #######################################################
    try:
        db = startDB(_host, _port, _db, _user, _pass)
        sql = 'SELECT id FROM points ORDER BY ID DESC LIMIT 1'
        db.cursor().execute(sql)
        closeDB(db)

    except:
        closeDB(db)
        db = startDB(_host, _port, _db, _user, _pass)
        sql = 'create table points(id serial primary key, X REAL, Y REAL, Z REAL);'
        createInsertDB(db, sql)
        closeDB(db)

    # Salva os pontos no Table Points
    #db = startDB(_host, _db, _user, _pass)
    #PointCloudToDB(path, db)
    #closeDB(db)
    
    end = datetime.today()
    diff = end - init
    print(diff.total_seconds())

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

        while profiles_numb <= 10000: # GETTING PROFILES FROM SENSOR
            profile = get_profile2D(scanner,zero_points,realtime,kSERVICE)
            if (profile is not None):
                profiles_numb = profiles_numb + 1
                dump.append(profile) # Get 2D Profile from Sensor

	    #################################################
	    #                                               #
	    #             PROFILES PROCESSING               #
	    #                                               #
	    #################################################
        for profile in dump:
            profile_data_type=profile['header']['data_type']

            if profile_data_type == PROFILE_DATA_TYPES.PROFILE:
                points_numb = profile['points_count']

            if 'points' in profile:
                for j in range(points_numb):
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
	    #             ALIGNMENT PROCESSING              #
	    #                                               #
	    #################################################
	    profile = dump[profiles_numb-1]
        for i in range(12960000,12960025,1):
            align0.append(float(profile['points'][i].z))

        for i in range(12961271,12961296,1):
            align1.append(float(profile['points'][i].z))

        point0 = sum(align0)/len(align0)
        point1 = sum(align1)/len(align1)

        print("Média no ponto 0: {point0}")
        print("Média no ponto 1: {point1}")

        #######################################################
        #                                                     #
        #              RESHAPING VECTORS TO PLOT              #
        #                                                     #
        #######################################################

        X = np.reshape(X,(profiles_numb, points_numb))
        Y = np.reshape(Y,(profiles_numb, points_numb))
        Z = np.reshape(Z,(profiles_numb, points_numb))

        #######################################################
        #                                                     #
        #              SAVING STANDARD .PNG IMAGE             #
        #                                                     #
        #######################################################
        print("Iniciou PLOT")
        fig1 = plt.figure(figsize=(16, 9))#figsize=(4,4))
        ax1 = fig1.add_subplot(111, projection='3d')
        #ax.plot_wireframe(X, Y, Z,cmap=cm.hot)
        surf = ax1.plot_surface(X, Y, Z, cmap=cm.hot, linewidth=3, antialiased=True)
        ax1.set_xlim(-10, 10)
        #ax1.set_ylim(100, 125)
        ax1.set_zlim(0, 30)
        ax1.view_init(30,-60)
        #plt.axis('off')
        save_path = "/usr/share/grafana/public/img/3D/standard%d.png" % (id)
        db_path = "public/img/3D/standard%d.png" % (id)
        plt.savefig(save_path, dpi=300, bbox_inches="tight", pad_inches=0)
        standard_img = '<img width="100%c" src="%s">' % ('%', db_path)
        plt.close(fig1)

        #######################################################
        #                                                     #
        #                SAVING SIDE .PNG IMAGE               #
        #                                                     #
        #######################################################
        fig1 = plt.figure(figsize=(16, 9))#figsize=(4,4))
        ax1 = fig1.add_subplot(111, projection='3d')
        #ax.plot_wireframe(X, Y, Z,cmap=cm.hot)
        surf = ax1.plot_surface(X, Y, Z, cmap=cm.hot, linewidth=3, antialiased=True)
        ax1.set_xlim(-10, 10)
        #ax1.set_ylim(100, 125)
        ax1.set_zlim(0, 30)
        ax1.view_init(30, 60)
        #plt.axis('off')
        save_path = "/usr/share/grafana/public/img/3D/side%d.png" % (id)
        db_path = "public/img/3D/side%d.png" % (id)
        plt.savefig(save_path, dpi=300, bbox_inches="tight", pad_inches=0)
        side_img = '<img width="100%c" src="%s">' % ('%', db_path)
        plt.close(fig1)

        #######################################################
        #                                                     #
        #              SAVING FRONT .PNG IMAGE                #
        #                                                     #
        #######################################################
        fig1 = plt.figure(figsize=(16, 9))#figsize=(4,4))
        ax1 = fig1.add_subplot(111, projection='3d')
        #ax.plot_wireframe(X, Y, Z,cmap=cm.hot)
        surf = ax1.plot_surface(X, Y, Z, cmap=cm.hot, linewidth=3, antialiased=True)
        ax1.set_xlim(-10, 10)
        #ax1.set_ylim(100, 125)
        ax1.set_zlim(0, 30)
        #plt.axis('off')
        ax1.view_init(0, 0)
        save_path = "/usr/share/grafana/public/img/3D/front%d.png" % (id)
        db_path = "public/img/3D/front%d.png" % (id)
        plt.savefig(save_path, dpi=300, bbox_inches="tight", pad_inches=0)
        front_img = '<img width="100%c" src="%s">' % ('%', db_path)
        plt.close(fig1)

        #######################################################
        #                                                     #
        #                 INSERT INTO PLOT DB                 #
        #                                                     #
        #######################################################
        print("Iniciou o INSERT")
        db = startDB(_host, _db, _user, _pass)
        sql = f"insert into plot values (default, '{standard_img}', '{front_img}', '{side_img}')"    
        createInsertDB(db, sql)

        print("Iniciou o SELECT")
        sql = 'SELECT * FROM plot'
        recset = getFromDB(db, sql)

        for rec in recset:
            print (rec)

        closeDB(db)
        end = datetime.today()
        diff = end - init
        print(diff.total_seconds())

        #################################################
        #                                               #
        #           DISCONNECT SENSOR AND SDK           #
        #                                               #
        #################################################

        ######### Disconnect from scanner #########
        disconnect(scanner)

    ######### Cleanup resources allocated with sdk_init() #########
    sdk_cleanup()
