from Data import Photo,Tracker,Measure
from Cloud import Detector
import time
import numpy as np

#Retrieve last from https://www.celestrak.com/NORAD/elements/stations.txt
name = "ISS (ZARYA)"
tle1 = "1 25544U 98067A   18357.61390951  .00000669  00000-0  17397-4 0  9990"
tle2 = "2 25544  51.6383 154.7029 0004723 175.2719 288.9280 15.54087824147973"


iss = Tracker(name,tle1,tle2)
photo = Photo()
detect = Detector()
measure = Measure()

print('Burn baby burn')

try:
    while True:
        lat, lon = iss.getPosition()
        sun_angle, day_light = iss.isDayLight()
        if day_light:
            print('Hooray i\'m in daylight')
            file = photo.captureImage()
            glass,cloud,cloudMasked = detect.detect(file)

            glass_clount = np.count_nonzero(glass)
            cloud_clount = np.count_nonzero(cloud)

            measure.write_data(lat,lon,sun_angle,cloud_clount,glass_clount,file)
            time.sleep(10)
        else:
            print('Be patient :) i\'m sleeping')
            time.sleep(30)


except (KeyboardInterrupt, SystemExit):
    print('\n! Hasta la vista baby \n')
    photo.close()
    measure.close()
