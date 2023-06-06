#!/usr/bin/env python

import rospy
  
from ros_object_detect.msg import Infodata2
                                  
def detresCB(data):
    print("label:{} x1:{} x2:{}".format(data.label, data.x1, data.x2))


rospy.init_node('info_subscriber')

det_sub = rospy.Subscriber('detdata', Infodata2, detresCB, queue_size=10)

rospy.spin()

