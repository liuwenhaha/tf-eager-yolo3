# -*- coding: utf-8 -*-

import argparse
import cv2
import tensorflow as tf
tf.enable_eager_execution()

from yolo.post_proc.decoder import decode_netout
from yolo.post_proc.box import correct_yolo_boxes, do_nms, draw_boxes

from yolo.net.yolonet import Yolonet, preprocess_input


argparser = argparse.ArgumentParser(
    description='test yolov3 network with coco weights')

argparser.add_argument(
    '-w',
    '--weights',
    default="yolov3.weights",
    help='path to weights file')

argparser.add_argument(
    '-i',
    '--image',
    default="imgs/dog.jpg",
    help='path to image file')


def postprocess_ouput(yolos, anchors, net_h, net_w, image_h, image_w, obj_thresh=0.5, nms_thresh=0.5):
    """
    # Args
        yolos : list of arrays
            Yolonet outputs
    
    """
    boxes = []
    for i in range(len(yolos)):
        # decode the output of the network
        boxes += decode_netout(yolos[i][0], anchors[i], obj_thresh, net_h, net_w)

    # correct the sizes of the bounding boxes
    correct_yolo_boxes(boxes, image_h, image_w, net_h, net_w)

    # suppress non-maximal boxes
    do_nms(boxes, nms_thresh)
    return boxes



if __name__ == '__main__':
    args = argparser.parse_args()

    weights_path = args.weights
    image_path   = args.image

    # set some parameters
    net_h, net_w = 416, 416
    anchors = [[116,90,  156,198,  373,326],  [30,61, 62,45,  59,119], [10,13,  16,30,  33,23]]
    labels = ["person", "bicycle", "car", "motorbike", "aeroplane", "bus", "train", "truck", \
              "boat", "traffic light", "fire hydrant", "stop sign", "parking meter", "bench", \
              "bird", "cat", "dog", "horse", "sheep", "cow", "elephant", "bear", "zebra", "giraffe", \
              "backpack", "umbrella", "handbag", "tie", "suitcase", "frisbee", "skis", "snowboard", \
              "sports ball", "kite", "baseball bat", "baseball glove", "skateboard", "surfboard", \
              "tennis racket", "bottle", "wine glass", "cup", "fork", "knife", "spoon", "bowl", "banana", \
              "apple", "sandwich", "orange", "broccoli", "carrot", "hot dog", "pizza", "donut", "cake", \
              "chair", "sofa", "pottedplant", "bed", "diningtable", "toilet", "tvmonitor", "laptop", "mouse", \
              "remote", "keyboard", "cell phone", "microwave", "oven", "toaster", "sink", "refrigerator", \
              "book", "clock", "vase", "scissors", "teddy bear", "hair drier", "toothbrush"]

    # 1. create yolo model & load weights
    yolov3 = Yolonet()
    yolov3.load_darknet_params(weights_path)

    # 2. preprocess the image
    image = cv2.imread(image_path)
    image = image[:,:,::-1]
    image_h, image_w, _ = image.shape
    new_image = preprocess_input(image, net_h, net_w)

    # 3. predict
    yolos = yolov3.predict(new_image)
    boxes = postprocess_ouput(yolos, anchors, net_h, net_w, image_h, image_w)
    
    print(image.shape)
    
    # draw bounding boxes on the image using labels
    image = draw_boxes(image, boxes, labels) 
    
    import matplotlib.pyplot as plt
    plt.imshow(image)
    plt.show()


 


