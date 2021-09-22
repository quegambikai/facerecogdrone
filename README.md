### facerecogdrone
This project is about real time face recognition using Haar cascade whereby the camera feed is from the DJI Tello drone.
You can download this repository or copy paste them into your script files.
Once you have all the files included in your project file you can now run the coding as shown but remember to establish the Wifi connection of the Tello drone first.
  1) Run **dataset.py** to create datasets. You have to key in the user id first. The captured grayscale images will be stored in a folder called "images" which will be created      by itself if it does not exist. 
  2) Run the **train.py** to train the images.
  3) You can name the user according to the id in the script file. Then run the **recognition.py** file and voila you have face recognized by your drone.
 
Result 

 <img width="276" alt="d;d" src="https://user-images.githubusercontent.com/88258712/134265140-7d2c6868-4f95-4196-8acf-b31a640fc9cc.PNG">


References:
  1) https://elbruno.com/2020/03/09/coding4fun-how-to-control-your-drone-with-20-lines-of-code-10-n
  2) https://github.com/medsriha/Real-Time-Face-Recognition
  3) https://github.com/damiafuentes/DJITelloPy/blob/master/examples/manual-control-opencv.py  
