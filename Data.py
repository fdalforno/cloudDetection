import picamera
import ephem
import time
import datetime as dt
import os
import math
import time

import csv

#this file contains our tools (one class each) for managing the datas

# This is our camera! 
class Photo(object):
    def __init__(self):
        # Picamera object and horizontally flips it
        self.camera = picamera.PiCamera() #Pick up the camera from the tools shelf
        self.camera.hflip = True
        #self.camera.annotate_background = picamera.Color('black')
        #self.camera.iso = 800
        
        self.folder = "./Data" #Save our photos here!
        
        if not os.path.exists(self.folder): 
            os.makedirs(self.folder) #create the pictures destination if it does not exist
        
    def captureImage(self): #smile for the camera! This function allows the camera to take a picture of the earth
        timeStamp = time.strftime("%Y%m%d%H%M%S") #append the current time to the picture
        directory = ('%s/img_%s.jpg' % (self.folder,timeStamp))
        self.camera.capture(directory) #save the picture!
        
        return directory
    
    def close(self):
        self.camera.close() #close the camera and put it away

#This is our scientific notebook tool
class Measure(object):
    def __init__(self): #pick up the notebook
        self.folder = "./Data/" #write the datas here
        self.file = "measure.csv" #at this page (file)
        self.measure = 0
        
        if not os.path.exists(self.folder):
            os.makedirs(self.folder) #buy a new notebook if u dont have one (its free dont worry >.< )
            
        self.path = os.path.join(self.folder,self.file) #this is the complete file path
        self.csv = open(self.path,"a",newline="") #put the pen on the page, after everything u have already written! (dont overwrite)
        self.writer = csv.writer(self.csv,delimiter=";",quotechar="'",quoting=csv.QUOTE_NONNUMERIC) #this is our pen
    
    def write_data(self,lat,lon,angle,cloudpx,glasspx,photo):
        timer = time.strftime("%Y%m%d%H%M%S")

		#write ALL the data! 
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

        if (self.measure % 10) == 0:
            self.csv.flush() #dont forget to write ;)

        self.measure += 1 

    
    def close(self): #put away the notebook
        self.csv.close()


#This is the tool that tells us where the iss is!
class Tracker(object): 
    def __init__(self,name,tle1,tle2): #prepare our tool
        self.name = name #this is our name :)
        self.sat = ephem.readtle(name, tle1, tle2) 

        self.twilight = 0
        self.sun = ephem.Sun() #this is the position of the Sun
    
    def getPosition(self,time = None):4 #This function is used to get the position of the ISS
        if(self.sat):
            if(time is None):
                self.sat.compute()
            else:
                self.sat.compute(time)
            return (self.sat.sublong,self.sat.sublat)
        else:
            return (None,None)
    
    def isDayLight(self,time = None): #Are we in the lighened side of earth? Let's find out!
        lon,lat = self.getPosition(time)

        observer = ephem.Observer()
        observer.lat = lat
        observer.long = lon
        observer.elevation = 0

        self.sun.compute(observer)
        sun_angle = math.degrees(self.sun.alt)

        return sun_angle,sun_angle > self.twilight

    
    