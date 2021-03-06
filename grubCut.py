import numpy as np
import cv2 as cv
import sys
import argparse
import os
import sys

BLUE = [255,0,0]        # rectangle color
RED = [0,0,255]         # PR BG
GREEN = [0,255,0]       # PR FG
BLACK = [0,0,0]         # sure BG
WHITE = [255,255,255]   # sure FG

DRAW_BG = {'color' : BLACK, 'val' : 0}
DRAW_FG = {'color' : WHITE, 'val' : 1}
DRAW_PR_FG = {'color' : GREEN, 'val' : 3}
DRAW_PR_BG = {'color' : RED, 'val' : 2}

rect = (0,0,1,1)
drawing = False         # flag for drawing curves
rectangle = False       # flag for drawing rect
rect_over = False       # flag to check if rect drawn
rect_or_mask = 100      # flag for selecting rect or mask mode
value = DRAW_FG         # drawing initialized to FG
thickness = 3           # brush thickness


def onmouse(event,x,y,flags,param):
    global img,img2,drawing,value,mask,rectangle,rect,rect_or_mask,ix,iy,rect_over

    # Draw Rectangle
    if event == cv.EVENT_RBUTTONDOWN:
        rectangle = True
        ix,iy = x,y

    elif event == cv.EVENT_MOUSEMOVE:
        if rectangle == True:
            img = img2.copy()
            cv.rectangle(img,(ix,iy),(x,y),BLUE,2)
            rect = (min(ix,x),min(iy,y),abs(ix-x),abs(iy-y))
            rect_or_mask = 0

    elif event == cv.EVENT_RBUTTONUP:
        rectangle = False
        rect_over = True
        cv.rectangle(img,(ix,iy),(x,y),BLUE,2)
        rect = (min(ix,x),min(iy,y),abs(ix-x),abs(iy-y))
        rect_or_mask = 0
        print(" Now press the key 'n' a few times until no further change \n")
    
    if event == cv.EVENT_LBUTTONDOWN:
        if rect_over == False:
            print("first draw rectangle \n")
        else:
            drawing = True
            cv.circle(img,(x,y),thickness,value['color'],-1)
            cv.circle(mask,(x,y),thickness,value['val'],-1)

    elif event == cv.EVENT_MOUSEMOVE:
        if drawing == True:
            cv.circle(img,(x,y),thickness,value['color'],-1)
            cv.circle(mask,(x,y),thickness,value['val'],-1)

    elif event == cv.EVENT_LBUTTONUP:
        if drawing == True:
            drawing = False
            cv.circle(img,(x,y),thickness,value['color'],-1)
            cv.circle(mask,(x,y),thickness,value['val'],-1)

ap = argparse.ArgumentParser()
ap.add_argument("-f", "--file", required = True, help = "file to parse")
args = vars(ap.parse_args())


file = args["file"]


exists = os.path.isfile(file)
if not exists:
    print("File {0} not exists")
    sys.exit(1)

img = cv.imread(file)
img2 = img.copy()
mask = np.zeros(img.shape[:2],dtype = np.uint8)
output = np.zeros(img.shape,np.uint8)

cv.namedWindow('output')
cv.namedWindow('input')
cv.setMouseCallback('input',onmouse)
cv.moveWindow('input',img.shape[1]+10,90)





print(" Instructions: \n")
print(" Draw a rectangle around the object using right mouse button \n")

while(True):
    cv.imshow('output',output)
    cv.imshow('input',img)
    k = cv.waitKey(1)
    
    if k == 27:
        break
    elif k == ord('0'): # BG drawing
        print(" mark background regions with left mouse button \n")
        value = DRAW_BG
    elif k == ord('1'): # FG drawing
        print(" mark foreground regions with left mouse button \n")
        value = DRAW_FG
    elif k == ord('2'): # PR_BG drawing
        value = DRAW_PR_BG
    elif k == ord('3'): # PR_FG drawing
        value = DRAW_PR_FG
    elif k == ord('r'): # reset everything
            print("resetting \n")
            rect = (0,0,1,1)
            drawing = False
            rectangle = False
            rect_or_mask = 100
            rect_over = False
            value = DRAW_FG
            img = img2.copy()
            mask = np.zeros(img.shape[:2],dtype = np.uint8) # mask initialized to PR_BG
            output = np.zeros(img.shape,np.uint8)           # output image to be shown
    elif k == ord('s'): # save image
            cv.imwrite('grabcut_output.png',mask2)
            print(" Result saved as image \n")

    elif k == ord('n'): # segment the image
            print(""" For finer touchups, mark foreground and background after pressing keys 0-3 and again press 'n' \n""")
            if (rect_or_mask == 0):         # grabcut with rect
                bgdmodel = np.zeros((1,65),np.float64)
                fgdmodel = np.zeros((1,65),np.float64)
                cv.grabCut(img2,mask,rect,bgdmodel,fgdmodel,1,cv.GC_INIT_WITH_RECT)
                rect_or_mask = 1
            elif rect_or_mask == 1:         # grabcut with mask
                bgdmodel = np.zeros((1,65),np.float64)
                fgdmodel = np.zeros((1,65),np.float64)
                cv.grabCut(img2,mask,rect,bgdmodel,fgdmodel,1,cv.GC_INIT_WITH_MASK)

    mask2 = np.where((mask==1) + (mask==3),255,0).astype('uint8')
    output = cv.bitwise_and(img2,img2,mask=mask2)
    


cv.destroyAllWindows()