#!/usr/bin/env python3

import rospy
import cv2

from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError


gst_str = ("nvarguscamerasrc ! video/x-raw(memory:NVMM), width=(int)320, height=(int)240, format=(string)NV12, framerate=(fraction)60/1 ! nvvidconv flip-method=2 ! video/x-raw, width=(int)320, height=(int)240, format=(string)BGRx ! videoconvert ! video/x-raw, format=(string)BGR ! appsink")


cap = cv2.VideoCapture(gst_str, cv2.CAP_GSTREAMER)

rospy.init_node("csi_pub", anonymous=True)
image_pub = rospy.Publisher("csi_image", Image, queue_size=1)

bridge = CvBridge()

while not rospy.is_shutdown():
    # Capture frame-by-frame
    ret, cv_image = cap.read()

    # Display the resulting frame
    # cv2.imshow('frame',cv_image)
    # cv2.waitKey(3)
    image_pub.publish(bridge.cv2_to_imgmsg(cv_image, "bgr8"))


# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
