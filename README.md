##Video-Benchmark


Goal is to create a framework for distributed video transacoding and post processing.

 - Confirmed that splitting the video does not add any penalty.
 - Tries to estimate the total time that a distributed transcoding and face detection on a video would take.
 

#Dependencies
 - Python
 - FFmpeg
 - OpenCV


#How to run
    
    usagestr = 'Phase1.py -l <splitLength> -n <number of splits/number of computers> -b <bandwidth> -w <latency within comp> -e [1 : to estimate the time]'
    

- l : Specify length of each split in seconds 
- n : Number of files you want the video to be split. Also used to specify number of computers availble for distributing the job
- b : Available bandwidth (MBps). Used when -e switch is set to 1
- w : Latency among the computers. Used when -e switch is set to 1
- e : Set it to 1 if you want this tool to estimate the time it would take to transcode and do facedetect on the entire video. Extrapolates the data gathered from a single split
    
