#!/usr/bin/python
#========================================
import numpy as np
import cv2
import cv
import time

class App(object):

	def __init__(self, video_src):  
	   self.vidFile = cv.CaptureFromFile(video_src)
	   self.vidFrames = int(cv.GetCaptureProperty(self.vidFile, cv.CV_CAP_PROP_FRAME_COUNT))

	   self.cascade_fn = "haarcascades/haarcascade_frontalface_default.xml"
	   self.cascade = cv2.CascadeClassifier(self.cascade_fn)

	   self.left_eye_fn = "haarcascades/haarcascade_eye.xml"
	   self.left_eye = cv2.CascadeClassifier(self.left_eye_fn)

	   self.mouth_fn = "haarcascades/haarcascade_mcs_mouth.xml"
	   self.mouth = cv2.CascadeClassifier(self.mouth_fn)       

	   self.selection = None
	   self.drag_start = None
	   self.tracking_state = 0
	   self.show_backproj = False

	   self.face_frame = 0
	   numFaces = 0
	   for f in xrange(self.vidFrames):
		   img = cv.QueryFrame(self.vidFile)
		   tmp = cv.CreateImage(cv.GetSize(img), 8, 3)
		   cv.CvtColor(img, tmp, cv.CV_BGR2RGB)
		   img = np.asarray(cv.GetMat(tmp))
		   #print "Searching frame", f+1
		   self.face_frame = f
		   self.rects = self.faceSearch(img)
		   if len(self.rects) != 0:
			   numFaces+=1
	   print str(numFaces) + " faces detected"

	def faceSearch(self, img):

	   gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	   gray = cv2.equalizeHist(gray)

	   rects = self.detect(gray, self.cascade)

	   if len(rects) != 0:
		   #print "Detected face"
		   sizeX = rects[0][2] - rects[0][0]
		   sizeY = rects[0][3] - rects[0][1]
		   #print "Face size is", sizeX, "by", sizeY
		   return rects
	   else:
		   return []

	def detect(self, img, cascade):

	   # flags = cv.CV_HAAR_SCALE_IMAGE
	   rects = cascade.detectMultiScale(img, scaleFactor=1.1, minNeighbors=2, minSize=(80, 80), flags = cv.CV_HAAR_SCALE_IMAGE)
	   if len(rects) == 0:
		   return []
	   rects[:,2:] += rects[:,:2]
	   return rects

	def run(self):

	   for f in xrange(self.face_frame, self.vidFrames):
		   self.t = time.clock()
		   img = cv.QueryFrame(self.vidFile)
		   if type(img) != cv2.cv.iplimage:
			   break

		   tmp = cv.CreateImage(cv.GetSize(img), 8, 3)
		   cv.CvtColor(img, tmp, cv.CV_BGR2RGB)
		   img = np.asarray(cv.GetMat(tmp))    

		   #self.faceTrack(img)

		   ch = 0xFF & cv2.waitKey(5)
		   if ch == 27:
			   break
		   if ch == ord('b'):
			   self.show_backproj = not self.show_backproj     

if __name__ == '__main__':
   import sys
   try: video_src = sys.argv[1]
   except: video_src = '1'
   App(video_src).run()


