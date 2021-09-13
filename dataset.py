import os
import cv2
import socket
import time
import threading


if not os.path.exists('images'):
    os.makedirs('images')

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
print("\n streamon response: {response}")
response = sendControlCommand("streamon")
print("\n streamon response: {response}")

# drone information
battery = 0

# enable face detection and input user id
count = 0
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
face_id = input('\n enter user id (MUST be an integer) and press <return> -->  ')
print("\n [INFO] Initializing face capture. Look the camera and wait ...")

# open UDP
print("\n opening UDP video feed, wait 2 seconds ")
videoUDP = 'udp://192.168.10.1:11111'
cam = cv2.VideoCapture(videoUDP)
time.sleep(2)

# open
i = 0

while True:
    i = i + 1
    start_time = time.time()

    try:
        ret, imgOrig = cam.read()
        img = cv2.resize(imgOrig, (640, 480))
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)


        for (top, right, bottom, left) in faces:
            cv2.rectangle(img, (top,right), (top+bottom,right+left), (255,0,0), 2)
            count += 1
            # Save the captured image into the images directory
            cv2.imwrite("./images/Users." + str(face_id) + '.' + str(count) + ".jpg", gray[right:right + left, top: top + bottom])


        # display fps
        if (time.time() - start_time ) > 0:
            fpsInfo = "FPS: " + str(1.0 / (time.time() - start_time)) # FPS = 1 / time to process loop
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(img, fpsInfo, (10, 20), font, 0.4, (255, 255, 255), 1)

        cv2.imshow('DJI Tello Camera', img)

        sendReadCommand('battery?')
        print("\n battery: {battery} % – i: {i} – {fpsInfo}")


    except Exception as e:
        print("\n exc: {e}")
        pass

    # Press Escape to end the program.
    k = cv2.waitKey(10) & 0xFF
    if k < 50:
        break
    # Take 50 face samples and stop video. You may increase or decrease the number of
    # images. The more the better while training the model.
    elif count >= 50:
        break

response = sendControlCommand("streamoff")
print("\n streamon response: {response}")
cv2.destroyAllWindows()