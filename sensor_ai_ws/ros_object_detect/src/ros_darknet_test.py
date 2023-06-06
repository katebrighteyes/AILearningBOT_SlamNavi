#!/usr/bin/env python3

import rospy, rospkg
import cv2, time
import numpy as np
import darknet

from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError

def convert2relative(bbox, darknet_width, darknet_height):
    """
    YOLO format use relative coordinates for annotation
    """
    x, y, w, h  = bbox

    _height     = darknet_height
    _width      = darknet_width
    return x/_width, y/_height, w/_width, h/_height

def convert2original(image, bbox, darknet_width, darknet_height):
    x, y, w, h = convert2relative(bbox, darknet_width, darknet_height)

    image_h, image_w, __ = image.shape

    orig_x       = int(x * image_w)
    orig_y       = int(y * image_h)
    orig_width   = int(w * image_w)
    orig_height  = int(h * image_h)

    bbox_converted = (orig_x, orig_y, orig_width, orig_height)

    return bbox_converted

def image_detection2(frame, network, class_names, class_colors, thresh):
    # Darknet doesn't accept numpy images.
    # Create one with image we reuse for each detect
    darknet_width = darknet.network_width(network)
    darknet_height = darknet.network_height(network)
    darknet_image = darknet.make_image(darknet_width, darknet_height, 3)

    image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    image_resized = cv2.resize(image_rgb, (darknet_width, darknet_height),
                               interpolation=cv2.INTER_LINEAR)

    darknet.copy_image_from_bytes(darknet_image, image_resized.tobytes())
    detections = darknet.detect_image(network, class_names, darknet_image, thresh=thresh)
    detections_adjusted = []
    for label, confidence, bbox in detections:
        bbox_adjusted = convert2original(frame, bbox, darknet_width, darknet_height)
        detections_adjusted.append((str(label), confidence, bbox_adjusted))

    darknet.free_image(darknet_image)
    #image = darknet.draw_boxes(detections, image_resized, class_colors)
    image = darknet.draw_boxes(detections_adjusted, frame, class_colors)
    #return cv2.cvtColor(image, cv2.COLOR_BGR2RGB), detections
    return image




def model_detect(img):
    classIds, scores, boxes = model.detect(img, confThreshold=0.6, nmsThreshold=0.4)

    print(len(classIds))
    print(classIds)
    print(scores)

    for (classId, score, box) in zip(classIds, scores, boxes):
        cv2.rectangle(img, (box[0], box[1]), (box[0] + box[2], box[1] + box[3]),
                      color=(0, 255, 0), thickness=2)
        #text = '%s: %.2f' % (classes[classId[0]], score)
        text = '%s: %.2f' % (classes[classId], score)
        cv2.putText(img, text, (box[0], box[1] - 5), cv2.FONT_HERSHEY_SIMPLEX, 1,
                    color=(0, 255, 0), thickness=2)

    return img


rospy.init_node("ros_daeknet_test", disable_signals=True)
image_pub = rospy.Publisher("darknet_image", Image, queue_size=1)


data_path = str(rospkg.RosPack().get_path('ros_object_detect')) + "/yolo/challenge.mp4"
#label_path = str(rospkg.RosPack().get_path('ros_camera_test')) + "/yolo/coco.data"
coco_path = str(rospkg.RosPack().get_path('ros_object_detect')) + "/yolo/coco.names"
cfg_path = str(rospkg.RosPack().get_path('ros_object_detect')) + "/yolo/yolov4-tiny.cfg"
weight_path = str(rospkg.RosPack().get_path('ros_object_detect')) + "/yolo/yolov4-tiny.weights"

print(coco_path)

bridge = CvBridge()

#img = cv2.imread(data_path)
#cap = cv2.VideoCapture(1)
gst_str = ("nvarguscamerasrc ! video/x-raw(memory:NVMM), width=(int)360, height=(int)240, format=(string)NV12, framerate=(fraction)60/1 ! nvvidconv flip-method=2 ! video/x-raw, width=(int)360, height=(int)240, format=(string)BGRx ! videoconvert ! video/x-raw, format=(string)BGR ! appsink")

cap = cv2.VideoCapture(gst_str, cv2.CAP_GSTREAMER)
fps = cap.get(cv2.CAP_PROP_FPS)
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
#cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
#cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

print('width:{} height:{}'.format(width,height))

network, class_names, class_colors = darknet.load_network3(
        cfg_path, coco_path,
        weight_path, batch_size=1)

thresh=.25

while not rospy.is_shutdown():
    # Capture frame-by-frame
    ret, cv_image = cap.read()

    output= image_detection2(
                cv_image, network, class_names, class_colors, thresh)

    # Display the resulting frame
    cv2.imshow('frame',output)
    if cv2.waitKey(int(1000.0/fps)) & 0xFF == ord('q'):
        break
    #image_pub.publish(bridge.cv2_to_imgmsg(cv_image, "bgr8"))

# When everything done, release the capture
cap.release()

cv2.destroyAllWindows()

