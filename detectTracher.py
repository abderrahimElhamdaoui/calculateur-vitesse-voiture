import math
from typing import Type
import numpy as np
import time
from datetime import datetime
import webcolors
from scipy.spatial import KDTree
from webcolors import *
import cv2
# 

class EuclideanDistTracker:
    def __init__(self):
        self.center_points = {}
        self.id_count = 0
        self.count = 0
        self.s1 = np.zeros((1,1000))
        self.s2 = np.zeros((1,1000))
        self.s = np.zeros((1,1000))
        self.f = np.zeros((1,1000))
        self.vitess=0
        self.dt=0
        self.Diste=25
        self.limet=80
        self.file = open("infos.txt", "w")
        self.file.write("ID \t son vitesse \n----------------\n")

    def update(self, objects_rect):
        objects_bbs_ids = []

        # Obtenir le point central du nouvel objet
        for rect in objects_rect:
            x, y, w, h = rect
            cx = (x + x + w) // 2
            cy = (y + y + h) // 2
            
            # VÉRIFIER SI L'OBJET EST DÉJÀ DÉTECTÉ
            same_object_detected = False

            for id, pt in self.center_points.items():
                dist = math.hypot(cx - pt[0], cy - pt[1])
                if dist < 70:
                    self.center_points[id] = (cx, cy)
                    objects_bbs_ids.append([x, y, w, h, id])
                    same_object_detected = True
                  
                    if (cy >= 135 and cy <= 155):
                        self.s1[0,id] = time.time()
                        # print("start "+str(id)+"\t\t"+str(self.s1[0,id]))
                        
                    if (cy >= 280 and cy <= 290):
                        self.s2[0,id] = time.time()
                        self.s[0,id] = self.s2[0,id] - self.s1[0,id]
                        # print("end "+str(id)+"\t\t"+str(self.s1[0,id])+"\t\t"+str(self.s2[0,id])+"\t\t"+str(self.s[0,id]))
                    if(self.s[0,id]>0 and self.f[0,id]!=1):
                         if(self.s1[0,id]!=0):
                            self.vitess=(self.Diste/self.s[0,id])*3.6
                            self.vitess=int(self.vitess)
                            self.file = open("infos.txt", "a")
                            if(self.vitess > self.limet):
                                self.file.write(str(id) +"\t"+str(self.vitess)+" Km/h"+"\t<=== cette voiture est depasse la vitesse specifiee."+"\n")
                            else:
                                self.file.write(str(id) +"\t"+str(self.vitess)+" Km/h"+"\n")
                            self.file.close()
                            print(str(id)+"\t\t"+str(self.s1[0,id])+"\t\t"+str(self.s2[0,id])+"\t\t"+str(self.s[0,id]))
                            self.f[0,id]=1
                        
                        
                        
            # NOUVELLE DÉTECTION D'OBJETS
            if same_object_detected is False:
                self.center_points[self.id_count] = (cx, cy)
                objects_bbs_ids.append([x, y, w, h, self.id_count])
                self.id_count += 1
                self.s[0,self.id_count]=0
                self.s1[0,self.id_count]=0
                self.s2[0,self.id_count]=0
               

        #  ATTRIBUER UN NOUVEL ID à OBJET
        new_center_points = {}
        for obj_bb_id in objects_bbs_ids:
            _, _, _, _, object_id = obj_bb_id
            center = self.center_points[object_id]
            new_center_points[object_id] = center

        self.center_points = new_center_points.copy()
        return objects_bbs_ids

    def getvitess(self):
        return str(self.vitess) 
    
    def getColor(self,var,x,y,w,h):
        hsv_frame = cv2.cvtColor(var, cv2.COLOR_BGR2HSV)
        cx = (x + x + w) // 2
        cy = (y + y + h) // 2
        color=""
        pixel_center_bgr = var[cy, cx]
        b, g, r = int(pixel_center_bgr[0]), int(pixel_center_bgr[1]), int(pixel_center_bgr[2])
        color=self.convert_rgb_to_names((b,g,r))
        return color

    def convert_rgb_to_names(self,rgb_tuple):
        names = []
        rgb_values = []
        for color_hex, color_name in webcolors.CSS3_HEX_TO_NAMES.items():
            names.append(color_name)
            rgb_values.append(hex_to_rgb(color_hex))

        kdt_db = KDTree(rgb_values)
        distance, index = kdt_db.query(rgb_tuple)
        return f'{names[index]}'

