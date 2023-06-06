#!/usr/bin/env python

import rospy

import jetson.inference
import jetson.utils

#from std_msgs.msg import Int32
from ros_object_detect.msg import Infodata2

speedVal = 0.1
angleVal = 0.0

stopCmd = 0

rospy.init_node('detectnet_node', disable_signals=True)

net = jetson.inference.detectNet("ssd-mobilenet-v2", threshold=0.5)
camera = jetson.utils.videoSource("csi://0")      # '/dev/video0' for V4L2
display = jetson.utils.videoOutput("display://0") # 'my_video.mp4' for file

#ctl_pub = rospy.Publisher('stopCmd', Int32, queue_size=10)
det_pub = rospy.Publisher('detdata', Infodata2, queue_size=10)

while display.IsStreaming():
    try:
        img = camera.Capture()
        detections = net.Detect(img)
        display.Render(img)
        display.SetStatus("Object Detection | Network {:.0f} FPS".format(net.GetNetworkFPS()))
        for detection in detections:
            #print(detection)
            if detection.ClassID == 1: 
                msg = Infodata2()
                msg.label = net.GetClassDesc(detection.ClassID)
                msg.x1 = detection.Left
                msg.x2 = detection.Right
                det_pub.publish(msg)
    except KeyboardInterrupt:  
        print("key int")  
        break  

print("end")
