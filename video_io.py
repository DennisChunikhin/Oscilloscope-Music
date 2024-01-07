import cv2
import numpy as np

def read_frames(path):
    frames = []
    
    video = cv2.VideoCapture(path)
    
    # Find OpenCV version
    (major_ver, minor_ver, subminor_ver) = (cv2.__version__).split('.')
    
    fps = 0
    if int(major_ver) < 3:
        fps = video.get(cv2.cv.CV_CAP_PROP_FPS)
    else:
        fps = video.get(cv2.CAP_PROP_FPS)
    
    hasNextFrame, frame = video.read()
    while hasNextFrame:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frames.append(np.asarray(frame))
        
        hasNextFrame, frame = video.read()
    
    video.release()
    cv2.destroyAllWindows()
    
    return frames, fps