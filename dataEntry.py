import cv2
import numpy as np
import matplotlib.pyplot as plt

def isDuplicate(frame1,frame2):
    pass

def Images(filename):
    result=[]
    vd = cv2.VideoCapture(filename)
    index = 0
    while vd.isOpened():
        ret,frame = vd.read()
        if len(result) > 0 and isDuplicate(frame,result[index-1]):
            if self.hasFace(frame):
                result.append(frame)




class EntryLogic():

    def __init__(self):
        #initialize empty images array here
        self.images=[]

    def isDuplicate(self,frame1,frame2):
        if not frame1.shape==frame2.shape:
            return False
        threshold=50
        difference = cv2.subtract(frame1, frame2)
        b, g, r = cv2.split(difference)
        result =cv2.countNonZero(b) < threshold and cv2.countNonZero(g) < threshold and cv2.countNonZero(r) < threshold
        if result:
            plt.imshow(frame1)
            plt.show()
            plt.imshow(frame2)
            plt.show
        return result


    def hasFace(self,frame):
        #convert the image to grayscale
        grayscale = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
        cascade_face = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
        faces_rects = cascade_face.detectMultiScale(grayscale,scaleFactor=1.2,minNeighbors=5)
        return faces_rects
        #convert this into image first

    def getFaces(self,frame):
        '''this method will extract the faces from  the images'''
        #convert the frame to image for opencv processing
        faces = self.hasFace(frame)
        if len(faces) <= 0:
            return False
        return self.extractFaces(frame,faces)

    def extractFaces(self,frame,faces):
        result =[]
        for (x,y,w,h) in faces:
            temp = frame[y:y+h,x:x+w]
            result.append(temp)
        return result

    def loadVideo(self,filename):
        result=[np.array([1])] # this will record the faces
        vd = cv2.VideoCapture(filename)
        index = 0
        ret=True
        while ret:
            ret,frame = vd.read()

            if len(result) > 0 and not self.isDuplicate(frame,result[len(result)-1]):
                faces=self.getFaces(frame)
                if faces and len(faces) > 0:
                    result =result+faces
            index = index+1
        return result[1:]


# loader = EntryLogic()
# faces=loader.loadVideo('The Code - S01E03 HD (TvShows4Mobile.Com).mp4')
# print(faces)