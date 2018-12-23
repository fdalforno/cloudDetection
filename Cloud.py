import cv2
import numpy as np

th = 20 * 255 / 100


class Detector(object):
    def __init__(self):
        pass
    
    def rescale(self, image, width=None, height=None, inter=cv2.INTER_AREA):
        dim = None
        (h, w) = image.shape[ :2 ]

        if width is None and height is None:
            return image

        if width is None:
            r = height / float(h)
            dim = (int(w * r), height)
        elif height is None:
            r = width / float(w)
            dim = (width, int(h * r))
        else:
            dim = (width, height)

        resized = cv2.resize(image, dim, interpolation=inter)

        return resized

    def detect_glass(self,image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray,(15,15),0)
        _,thresh = cv2.threshold(blur,th,255,cv2.THRESH_BINARY)
        _, contours, _= cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        mask = np.zeros(image.shape, dtype=np.uint8)

        for contour in contours:
            (x,y),radius = cv2.minEnclosingCircle(contour)
            if(radius > 250):
                center = (int(x),int(y))
                radius = int(radius) - 40
                cv2.circle(mask, center, radius, (255, 255, 255), -1, 8, 0)
                break
        
        return mask

    def cloud_detection(self,image,mean = 200, overture = 80):
        b,g,r = cv2.split(image)
        arrB = np.float32(b)
        arrG = np.float32(g)
        arrR = np.float32(r)
        height,width,_ = image.shape

        meanVis = (arrB + arrG + arrR) / 3.0
        whiteness = np.zeros((height,width))
        for n in [arrB, arrG, arrR]:
            whiteness = whiteness + np.absolute(n - meanVis)
    
        clouds = (meanVis > mean) & (whiteness < overture)

        mask = np.zeros(image.shape, dtype = "uint8")
        mask[clouds] = (255,255,255)

        return mask

    def detect(self,src):
        image = cv2.imread(src)
        rescaled = self.rescale(image,800)
        glass = self.detect_glass(rescaled)
        cloud = self.cloud_detection(rescaled)

        glassMasked = cv2.bitwise_and(rescaled, glass)
        cloudMasked = cv2.bitwise_and(glassMasked, cloud)

        return glass,cloud,cloudMasked


