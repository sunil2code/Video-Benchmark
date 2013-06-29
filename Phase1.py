#!/usr/bin/python
#========================================
import os
import glob
import time
import sys
#========================================
root = "/tmp/Data";
srcDir = root+"/VideoSrc";
outDir = root+"/VideoOut";
splitDir = outDir + "/split"
decodeDir = outDir + "/decode"
opencvDir = outDir + "/opencv"
video = "sample.mov";
videoLoc = srcDir+"/"+video
dataoutput = "output.csv";
dataOutputLoc = root+"/"+dataoutput
fileName, fileExtension = os.path.splitext(videoLoc)

faceDetectScript = "/home/samba/Video/facedetect.py"

splitLength = 2

doCleanup = 1
splitVideo = 1
doDecode = 1
doDetect = 1

#contains output string
l = []

if not os.path.exists(videoLoc):
		print "Video source not found."
		sys.exit()
#========================================
#Functions
def getTimeStr(i):
		if i < 60:
				return "00:00:"+str(i).zfill(2)
		else:
				numHours = i/3600
				if numHours > 0:
						i = i-(numHours*3600)
				numMinuts = i/60
				if numMinuts > 0:
						i = i-(numMinuts*60)
				print "numHours = " + str(numHours)
				print "numMins = " + str(numMinuts)
				print "seconds = " + str(i)
				s = "00:" if numHours == 0 else str(numHours).zfill(2)+":"
				s += "00:" if numMinuts == 0  else str(numMinuts).zfill(2)+":"
				s += "00:" if i == 0  else str(i).zfill(2)
				return s


def getNumFrames(v):
		if not os.path.exists(v):
				return 0
		cmd1 = "ffmpeg -i " + v + " -vcodec copy -f rawvideo -y /dev/null 2>&1 | tr ^M '\\n' | awk '/^frame=/ {print $2}'|tail -n 1"
		f = os.popen(cmd1)
		numberOfFrames = f.read().rstrip()
		if numberOfFrames == "":
			return 0
		return numberOfFrames

#========================================
#cleanup old data
if doCleanup == 1:
		#delete files
		if os.path.exists(splitDir):
				for files in os.listdir(splitDir):
						os.remove(splitDir+'/'+files)
		if os.path.exists(decodeDir):
				for files in os.listdir(decodeDir):
						os.remove(decodeDir+'/'+files)
		if os.path.exists(opencvDir):
				for files in os.listdir(opencvDir):
						os.remove(opencvDir+'/'+files)
		if os.path.exists(outDir):
				for files in os.listdir(outDir):
						if os.path.isfile(files):
								os.remove(outDir+'/'+files)
		print "Cleanup Done!"

#create folders if necessary
if not os.path.exists(splitDir):
		os.makedirs(splitDir)
if not os.path.exists(decodeDir):
		os.makedirs(decodeDir)
if not os.path.exists(opencvDir):
		os.makedirs(opencvDir)

#========================================
#get number of frames
print "Number of Frame = " + str(getNumFrames(videoLoc))

#========================================
#get fps of video
fps = 0
cmd2 = "ffmpeg -i " + videoLoc + " slkjdf 2>&1 | grep Video:"
f = os.popen(cmd2)
fpsOut = f.read().rstrip()
fpsOut = fpsOut.split(',')
for param in fpsOut:
		if param.find('fps') >= 0:
				param = param.replace("fps", "").strip()
				fps = int(float(param))

print "FPS = " + str(fps)

#========================================
#get gop of video
gopSize = 0
cmd3 = "ffprobe -v quiet -show_format -show_streams -i " + videoLoc
f = os.popen(cmd3)
fpsOut = f.read().rstrip()
fpsOut = fpsOut.split('\n')
for param in fpsOut:
		if param.find('gop_size') >= 0:
				param = param.replace("gop_size=", "").strip()
				gopSize = int(float(param))

if gopSize > 0:
		print "GOP = " + str(gopSize)
else:
		print "GOP = 0 [Could not find GOP]"


#========================================
#get duration of video
cmd4 = "ffprobe -v quiet -show_format " + videoLoc + " | grep duration="
f = os.popen(cmd4)
duration = f.read().rstrip()
duration = duration.replace("duration=","").strip()
duration = int(float(duration))
print "Duration = " + str(duration)

#========================================
#split frames
#-segment_time " + str((duration * (fps/gopSize )) if gopSize > 0 else (duration * fps)) + "
#cmd5 = "ffmpeg -i " + videoLoc + " -f segment -c copy -segment_time_delta 0.5 -map 0 " + splitDir + "/out-%3d" + fileExtension + " 2>&1"
#cmd5 = "ffmpeg -i " + videoLoc + " -f segment -c copy -segment_time " + str((duration * (fps/gopSize )) if gopSize > 0 else (numberOfFrames)) + " -map 0 " + outDir + "/out-%3d" + fileExtension + " 2>&1"
#cmd5 = "ffmpeg -i " + videoLoc + " -c copy -ss " + getTimeStr(i) + " -t 00:00:02 -map 0  " + splitDir +"/out"+str(index).zfill(3)+fileExtension + " 2>&1 >/dev/null"
index = 0
if splitVideo == 1:
		print "Splitting..."
		if gopSize > 0:
				cmd5 = "ffmpeg -i " + videoLoc + " -f segment -c copy -segment_time " + str(duration * (fps/gopSize )) + " -map 0 " + splitDir + "/out-%3d" + fileExtension + " 2>&1"
				print cmd5
				os.system(cmd5)
		else:
				for i in range(0, duration, splitLength):
						index += 1
						cmd5 = "ffmpeg -i " + videoLoc + " -vcodec copy -acodec copy -ss " + getTimeStr(i) + " -t 00:00:02 " + splitDir +"/out"+str(index).zfill(3)+fileExtension + " 2>&1 >/dev/null"
						print cmd5
						os.system(cmd5)
		print "Done!"

#========================================
#get time to save
prevMTime = 0
timeToSave = 0
for files in sorted(os.listdir(splitDir)):
		if files.startswith("."):
				continue
		curFileLoc = splitDir+"/"+files
		fileSize = os.path.getsize(curFileLoc)
		mtime = os.path.getmtime(curFileLoc)
		if prevMTime != 0:
				timeToSave = mtime - prevMTime
		prevMTime = mtime
		l.append(files + "," + str(getNumFrames(curFileLoc)) + "," + str(fileSize) + "," + str(timeToSave))

#========================================
#decode frames
curIndex = 0
if doDecode == 1:
	for files in sorted(os.listdir(splitDir)):
			fileName, efileExtension = os.path.splitext(files)
			cmd6 = "ffmpeg -i " + splitDir + "/" + files + " -f rawvideo -vcodec rawvideo " + decodeDir + "/" + fileName + ".raw"
			print cmd6
			st = time.time()
			os.system(cmd6)
			et = time.time()
			fileSize = 0
			if os.path.exists(decodeDir+"/"+fileName+".raw"):
					fileSize = os.path.getsize(decodeDir+"/"+fileName+".raw")
			l[curIndex] = l[curIndex] + "," + str(fileSize) + "," + str(et-st)
			curIndex+=1

#========================================
#face detect frames
curIndex = 0
if doDetect == 1:
	for files in sorted(os.listdir(splitDir)):
			fileName, efileExtension = os.path.splitext(files)
			cmd7 = faceDetectScript + " " + splitDir + "/" + files
			print cmd7
			st = time.time()
			os.system(cmd7)
			l[curIndex] = l[curIndex] + "," + str(time.time()-st)
			curIndex+=1

#========================================
#save output
f = open(dataOutputLoc, "w")
f.write("Split Name, # Frames, Split Size, Time to split (s), Decode Size, Time to decode (s), opencv time (s)\n");
for item in l:
		f.write(item + "\n")
f.close()
