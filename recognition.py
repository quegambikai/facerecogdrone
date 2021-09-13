import cv2
import numpy as np
import os
import socket
import time
import threading

def receiveData():
    global response
    while True:
        try:
            response, _ = clientSocket.recvfrom(1024)
        except:
            break

def readStates():
    global battery
    while True:
        try:
            response_state, _ = stateSocket.recvfrom(256)
            if response_state != 'ok':
                response_state = response_state.decode('ASCII')
                list = response_state.replace(';', ':').split(':')
                battery = int(list[21])
        except:
            break

def sendCommand(command):
    global response
    timestamp = int(time.time() * 1000)

    clientSocket.sendto(command.encode('utf-8'), address)

    while response is None:
        if (time.time() * 1000) - timestamp > 5 * 1000:
            return False

    return response


def sendReadCommand(command):
    response = sendCommand(command)
    try:
        response = str(response)
    except:
        pass
    return response

def sendControlCommand(command):
    response = None
    for i in range(0, 5):
        response = sendCommand(command)
        if response == 'OK' or response == 'ok':
            return True
    return False

# ———————————————–
# Main program
# ———————————————–

# connection info
UDP_IP = '192.168.10.1'
UDP_PORT = 8889
last_received_command = time.time()
STATE_UDP_PORT = 8890

address = (UDP_IP, UDP_PORT)
response = None
response_state = None

clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
clientSocket.bind(('', UDP_PORT))
stateSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
stateSocket.bind(('', STATE_UDP_PORT))

# start threads
recThread = threading.Thread(target=receiveData)
recThread.daemon = True
recThread.start()

stateThread = threading.Thread(target=readStates)
stateThread.daemon = True
stateThread.start()

# connect to drone. Streamoff first in case it was on
response = sendControlCommand("command")
print("\ncommand response: {response}")
response = sendControlCommand("streamoff")
print("\ncommand response: {response}")
response = sendControlCommand("streamon")
print("\n streamon response: {response}")

# drone information
battery = 0

# open UDP
print("\n opening UDP video feed, wait 2 seconds ")
videoUDP = 'udp://192.168.10.1:11111'
cap = cv2.VideoCapture(videoUDP)
time.sleep(2)

recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read('trainer.yml')

face_cascade_Path = "haarcascade_frontalface_default.xml"

faceCascade = cv2.CascadeClassifier(face_cascade_Path)

font = cv2.FONT_HERSHEY_SIMPLEX

id = 0
# names related to ids: The names associated to the ids: 1 for Kugam, 2 for Ariana, etc...
names = ['None', 'Kugam', 'Ariana', 'Harry'] # add a name into this list

#rescale the frame size
def rescale_frame(frame, percent=75):
    top = int(frame.shape[1] * percent/ 100)
    right = int(frame.shape[0] * percent/ 100)
    dim = (top, right)
    return cv2.resize(frame, dim, interpolation =cv2.INTER_AREA)

i = 0
while True:
    i = i + 1
    start_time = time.time()

    try:
        ret, frame = cap.read()
        frame = rescale_frame(frame,percent=70)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = faceCascade.detectMultiScale(
            gray,
            scaleFactor=1.2,
            minNeighbors=5,

        )

        for (top, right, bottom, left) in faces:
            cv2.rectangle(frame, (top,right), (top+bottom,right+left), (0, 255, 0), 2)
            id, confidence = recognizer.predict(gray[right:right + left, top: top + bottom])
            if (confidence < 100):
                id = names[id]
                confidence = "  {0}%".format(round(100 - confidence))
            else:
                # Unknown Face
                id = "Unknown"
                confidence = "  {0}%".format(round(100 - confidence))

            cv2.putText(frame, str(id), (top + 5, right - 5), font, 1, (255, 255, 255), 2)
            cv2.putText(frame, str(confidence), (top + 5, right + left - 5), font, 1, (255, 255, 0), 1)

        # display fps
        if (time.time() - start_time) > 0:
            fpsInfo = "FPS: " + str(1.0 / (time.time() - start_time))  # FPS = 1 / time to process loop
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, fpsInfo, (10, 20), font, 0.4, (255, 255, 255), 1)

        cv2.imshow('DJI Tello Camera', frame)

    except Exception as e:
        print("\n exc: {e}")
        pass
    # Hit "q" to exit the webcam / program
    if cv2.waitKey(10) & 0xff == ord('q'):
        break
print("\n [INFO] Exiting Program.")
cap.release()
cv2.destroyAllWindows()