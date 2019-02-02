from Data import Photo,Tracker,Measure
from Cloud import Detector
import time
import numpy as np

#Retrieve last from https://www.celestrak.com/NORAD/elements/stations.txt
name = "ISS (ZARYA)"
tle1 = "1 25544U 98067A   18357.61390951  .00000669  00000-0  17397-4 0  9990"
tle2 = "2 25544  51.6383 154.7029 0004723 175.2719 288.9280 15.54087824147973"

#Here we initilize the tools that we will use
iss = Tracker(name,tle1,tle2)
photo = Photo()
detect = Detector()
measure = Measure()

print('Burn baby burn') #Let's start!

try: 
    while True: #we will execute the code forever, unless the user tells us to stop manually
        lat, lon = iss.getPosition() #where is the iss? (latitude,longitude)
        sun_angle, day_light = iss.isDayLight() #are we in day_light ?
        if day_light:                           # yes!
            print('Hooray i\'m in daylight')    
            file = photo.captureImage()         #EVERYBODY ON EARTH, smile for the camera!
            glass,cloud,cloudMasked = detect.detect(file) #where are the clouds?

            glass_clount = np.count_nonzero(glass)		  #count how much glass there is in the image
            cloud_clount = np.count_nonzero(cloud)		  #and also how "cloudy" it is 

            measure.write_data(lat,lon,sun_angle,cloud_clount,glass_clount,file) #we have to write it down on a file for science
            time.sleep(10) #Uff, we worked a lot! Time for a brief pause!
        else:
            print('Be patient :) i\'m sleeping')
            time.sleep(30) #We are on the night side of earth, so its time to rest a bit and wait


except (KeyboardInterrupt, SystemExit):
    print('\n! Hasta la vista baby \n') #Our job is done! Let's clean up and go!
    photo.close() #Put away the camera se we won't lose it
    measure.close() #Put away our notebook
