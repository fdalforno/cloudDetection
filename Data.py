import picamera
import ephem
import time
import datetime as dt
import os
import math
import time

import csv

class Photo(object):
    def __init__(self):
        # Picamera object and horizontally flips it
        self.camera = picamera.PiCamera()
        self.camera.hflip = True
        #self.camera.annotate_background = picamera.Color('black')
        #self.camera.iso = 800
        
        self.folder = "./Data"
        
        if not os.path.exists(self.folder):
            os.makedirs(self.folder)
        
    def captureImage(self):
        timeStamp = time.strftime("%Y%m%d%H%M%S")
        directory = ('%s/img_%s.jpg' % (self.folder,timeStamp))
        self.camera.capture(directory)
        
        return directory
    
    def close(self):
        self.camera.close()

class Measure(object):
    def __init__(self):
        self.folder = "./Data/"
        self.file = "measure.csv"
        self.measure = 0
        
        if not os.path.exists(self.folder):
            os.makedirs(self.folder)
            
        self.path = os.path.join(self.folder,self.file)
        self.csv = open(self.path,"a",newline="")
        self.writer = csv.writer(self.csv,delimiter=";",quotechar="'",quoting=csv.QUOTE_NONNUMERIC)
    
    def write_data(self,lat,lon,angle,cloudpx,glasspx,photo):
        timer = time.strftime("%Y%m%d%H%M%S")

        row = []
        row.append(self.measure)
        row.append(timer)
        row.append(lat / ephem.degree)
        row.append(lon / ephem.degree)
        row.append(angle)
        row.append(cloudpx)
        row.append(glasspx)
        row.append(photo)
        self.writer.writerow(row)

        if(self.measure % 10):
            self.csv.flush()

        self.measure += 1

    
    def close(self):
        self.csv.close()


class Tracker(object):
    def __init__(self,name,tle1,tle2):
        self.name = name
        self.sat = ephem.readtle(name, tle1, tle2)

        self.twilight = 0
        self.sun = ephem.Sun()
    
    def getPosition(self,time = None):
        if(self.sat):
            if(time is None):
                self.sat.compute()
            else:
                self.sat.compute(time)
            return (self.sat.sublong,self.sat.sublat)
        else:
            return (None,None)
    
    def isDayLight(self,time = None):
        lon,lat = self.getPosition(time)

        observer = ephem.Observer()
        observer.lat = lat
        observer.long = lon
        observer.elevation = 0

        self.sun.compute(observer)
        sun_angle = math.degrees(self.sun.alt)

        return sun_angle,sun_angle > self.twilight

    
    