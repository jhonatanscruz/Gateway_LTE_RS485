#######################################################
#                                                     #
#                      LIBRARIES                      #
#                                                     #
#######################################################

import sys
import json
import psycopg2
sys.path.append("../../../RF62X-Wrappers/Python/")
import time
from datetime import datetime, timezone
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
#   Get point cloud for .txt files previously stored                            #
#                                                                               #
#################################################################################
"""
def getPointCloud(path, X, Y, Z):
    print("Iniciou")
    my_file_X = open("%s/X.txt" % (path), "r")
    my_file_Y = open("%s/Y.txt" % (path), "r")
    my_file_Z = open("%s/Z.txt" % (path), "r")
    content_x = my_file_X.readlines()
    content_y = my_file_Y.readlines()
    content_z = my_file_Z.readlines()

    for x, y, z in zip(content_x, content_y, content_z):
        X.append(float(x))
        Y.append(float(y))
        Z.append(float(z))

    my_file_X.close
    my_file_Y.close
    my_file_Z.close

def PointCloudToDB(path, db):
    print("Iniciou")
    my_file_X = open("%s/X.txt" % (path), "r")
    my_file_Y = open("%s/Y.txt" % (path), "r")
    my_file_Z = open("%s/Z.txt" % (path), "r")
    content_x = my_file_X.readlines()
    content_y = my_file_Y.readlines()
    content_z = my_file_Z.readlines()

    for x, y, z in zip(content_x, content_y, content_z):
        sql = f"INSERT INTO points VALUES(default, {x}, {y}, {z})"
        createInsertDB(db, sql)

    my_file_X.close
    my_file_Y.close
    my_file_Z.close

"""
#################################################################################
#                                                                               #
#                      Functions to manipulate Postgres DB                      #
#                                                                               #
#################################################################################
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


#######################################################
#                                                     #
#                        MAIN                         #
#                                                     #
#######################################################
if __name__ == '__main__':
    init = datetime.today()
    X = []
    Y = []
    Z = []
    profiles_numb = 10001
    points_numb = 1296
    id = 1
    path = "TESTES/01-07-2021/16"

    # DATABASE CONNECTION CREDENTIALS
    _host='proxy21.rt3.io'
    _port='39370'
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
        sql = 'create table metrics(id SERIAL primary key, volume REAL, rigth_align REAL, left_align REAL, timestamp TIMESTAMP WITHOUT TIME ZONE);'
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

    #######################################################
    #                                                     #
    #            GETTING 3D POINTS FROM SENSOR            #
    #                                                     #
    #######################################################
    getPointCloud(path, X, Y, Z)

    #######################################################
    #                                                     #
    #              RESHAPING VECTORS TO PLOT              #
    #                                                     #
    #######################################################
    print("Iniciou NP")
    X = np.reshape(X,(profiles_numb, points_numb))
    Y = np.reshape(Y,(profiles_numb, points_numb))
    Z = np.reshape(Z,(profiles_numb, points_numb))
    
    i = 0
    for a in X[0]:
        i = i + 1
    print(f"Número em X[0] = {i}")

    i = 0
    for a in Y[0]:
        i = i + 1
    print(f"Número em Y[0] = {i}")

    i = 0
    for a in Z[0]:
        i = i + 1
    print(f"Número em Z[0] = {i}")

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
    db = startDB(_host, _port, _db, _user, _pass)
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
    """
    plt.show()
    """

    # CASO DESEJE SALVAR EM IMAGEM
    #init = datetime.today()
    #end = datetime.today()
    #diff = end - init
    #about.write("Salvou a imagem .PNG!! Demorou: %f segundos \n" % (diff.total_seconds()))
