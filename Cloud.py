import cv2
import numpy as np

th = 20 * 255 / 100

#This is a tool that allows us to identify the clouds and the water
class Detector(object):
    def __init__(self):
        pass
    
	#This tool function allows us to rescale every image to a size that we choose
    def rescale(self, image, width=None, height=None, inter=cv2.INTER_AREA):
        dim = None
        (h, w) = image.shape[ :2 ]

        if width is None and height is None: #we dont have to resize the image
            return image

        if width is None:
            r = height / float(h)
            dim = (int(w * r), height) #dont stretch the image while resizing it to the correct height
        elif height is None:
            r = width / float(w)
            dim = (width, int(h * r)) #dont stretch the image while resizing it to the correct width
        else:
            dim = (width, height)     #be careful, this could stretch the image!

        resized = cv2.resize(image, dim, interpolation=inter) 

        return resized

    def detect_glass(self,image): #The camera sees the glass of the iSS, this is not what we want so we have to find it
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) #look at the image in black and white like dogs do
        blur = cv2.GaussianBlur(gray,(15,15),0) #squint your eyes a bit to smooth the details
        _,thresh = cv2.threshold(blur,th,255,cv2.THRESH_BINARY) #ok now look where is dark, that area is glass
        _, contours, _= cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) #find the contours for that area

        mask = np.zeros(image.shape, dtype=np.uint8) #now lets find a overlay mask for the pixels that are glass (we cover them)

        for contour in contours:
            (x,y),radius = cv2.minEnclosingCircle(contour) #since the glass has a circular shape we can use a circle mask to cover it
            if(radius > 250): #We want to keep only the bigger circle found! Smaller circles could be caused by strange clouds and terrain
                center = (int(x),int(y)) #the center of our circle
                radius = int(radius) - 40 #its radius (we shrink it a bit)
                cv2.circle(mask, center, radius, (255, 255, 255), -1, 8, 0) #Create the circle :)
                break
        
        return mask

    def cloud_detection(self,image,mean = 150, overture = 80): #This tool function allows us to find the clouds ^_^
        b,g,r = cv2.split(image) #we want to look closely at each color component
        arrB = np.float32(b) #blue
        arrG = np.float32(g) #green
        arrR = np.float32(r) #red
        height,width,_ = image.shape #w and h of our image

        meanVis = (arrB + arrG + arrR) / 3.0 #the mean color value
        whiteness = np.zeros((height,width)) 
        for n in [arrB, arrG, arrR]:
            whiteness = whiteness + np.absolute(n - meanVis) #how strong is the white component for each pixel
    
        clouds = (meanVis > mean) & (whiteness < overture) #white areas that are not too bright

        mask = np.zeros(image.shape, dtype = "uint8") #create the result mask image
        mask[clouds] = (255,255,255) #and paint it white where there are clouds

        return mask

    def water_detection(self,image,threshold = -0.7): #this function is used to find the water (i'm feeling kind of thirsty!)
        b,g,r = cv2.split(image)
        arrB = np.float32(b)
        arrR = np.float32(r)


        #we use low values of ndvi to detect water areas
        num = (arrR - arrB)
        denom = (arrR + arrB)
        arrNdvi = np.divide(num,denom,where=denom > 0) 

        water = arrNdvi < threshold #we want only water! (we must be confident)
        mask = np.zeros(image.shape, dtype = "uint8") #again prepare the mask
        mask[water] = (255,255,255) #paint it white only where there is water

        return mask


    def detect(self,src): #general ALL-IN-ONE function! Finds glass, clouds and water in one run! Very handy!
        image = cv2.imread(src)
        rescaled = self.rescale(image,800)

        glass = self.detect_glass(rescaled) #look for glass
        cloud = self.cloud_detection(rescaled) #look for clouds

        water = self.water_detection(rescaled) #look for water
        not_water = cv2.bitwise_not(water) #actually, look way from water!

        glassMasked = cv2.bitwise_and(rescaled, glass) #this is the glass
        cloudMasked = cv2.bitwise_and(glassMasked, cloud) #these are the clouds :)
        cloudMasked =  cv2.bitwise_and(cloudMasked, not_water) #that are not water!

        return glass,cloud,cloudMasked


