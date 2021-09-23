import cv2
import numpy as np
from PIL import Image
import os

#Directory path name where the face images are stored.
path = './images/'
recognizer = cv2.face.LBPHFaceRecognizer_create()
#Haar cascade file
detector = cv2.CascadeClassifier("haarcascade_frontalface_default.xml");

def getImagesAndLabels(path):
    framePaths = [os.path.join(path,f) for f in os.listdir(path)]
    faceSamples=[]
    ids = []
    for framePath in framePaths:
        # convert it to grayscale
        PIL_frame = Image.open(framePath).convert('L')
        frame_numpy = np.array(PIL_frame,'uint8')
        id = int(os.path.split(framePath)[-1].split(".")[1])
        faces = detector.detectMultiScale(frame_numpy)
        for (top, right, bottom, left) in faces:
            faceSamples.append(frame_numpy[top:top + bottom, right:right + left])
            ids.append(id)
    return faceSamples,ids
print ("\n[INFO] Training faces...")
faces,ids = getImagesAndLabels(path)
recognizer.train(faces, np.array(ids))
# Save the model into the current directory.
recognizer.write('trainer.yml')
print("\n[INFO] {0} faces trained. Exiting Program".format(len(np.unique(ids))))