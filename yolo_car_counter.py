from ultralytics import YOLO
import cv2
import cvzone
import math
from sort import *
import numpy as np

cap = cv2.VideoCapture('cars2.mp4')
model = YOLO('yolov8n.pt')

# # Export the model to NCNN format
# model.export(format="ncnn")  # creates 'yolov8n_ncnn_model'

# # Load the exported NCNN model
ncnn_model = YOLO("yolov8n_ncnn_model")


mask = cv2.imread('E:/YOLO/mask.png')

tracker = Sort(max_age = 20 ,min_hits=3, iou_threshold=0.3)

classNames = ['person','bicycle','car','motorbike','airplane','bus','train','truck','boat','traffic light','fire hydrant','stop sign',
              'parking meter','bench','bird','cat','dog','horse','sheep','cow','elephant','bear','zebra','giraffe','backpack','umbrella',
              'handbag','tie','suitcase','frisbee','skis','snowboard','sports ball','kite','baseball bat','baseball glove','skateboard',
              'surfboard','tennis racket','bottle','wine glass','cup','fork','knife','spoon','bowl','banana','apple','sandwich','orange',
              'broccoli','carrot','hot dog','pizza','donut','cake','chair','couch','potted plant','bed','dining table','toilet','tv',
              'laptop','mouse','remote','keyboard','cell phone','microwave','oven','toaster','sink','refrigerator','book','clock','vase',
              'scissors','teddy bear','hair drier','toothbrush']

limits = [400, 297, 673, 297]

totalCount = []

while True:
    isTrue, frame = cap.read()
    imgRegion = cv2.bitwise_and(frame, mask)
    results = ncnn_model(imgRegion, stream=True)

    detections = np.empty((0,5))

    for r in results:
        boxes = r.boxes
        for box in boxes:
            x1,y1,x2,y2 = box.xyxy[0]
            x1,y1,x2,y2 = int(x1), int(y1), int(x2), int(y2)
            # print(x1,y1,x2,y2)
            # cv2.rectangle(frame, (x1,y1), (x2,y2), (255,0,255), 3)
            w, h = x2 -x1, y2 - y1
            conf = math.ceil((box.conf[0] * 100)) / 100
            cls = int(box.cls[0])
            currentClass = classNames[cls]

            if currentClass == 'car' or currentClass == 'motorbike' or currentClass == 'truck' or currentClass == 'bus' and conf > 0.3:
            #   cvzone.putTextRect(frame, f'{currentClass} {conf}', (max(0, x1), max(35, y1)), scale = 0.6, thickness=1,offset=3)
            #   cvzone.cornerRect(frame, (x1, y1, w, h), l=9)
              currentArray = np.array([x1, y1, x2, y2, conf])
              detections = np.vstack((detections, currentArray))     
    
    resultTracker =  tracker.update(detections)

    cv2.line(frame, (limits[0], limits[1]), (limits[2], limits[3]), (0,0,255), 5) 
    
    for result in resultTracker:
        x1, y1, x2, y2, id = result
        x1,y1,x2,y2 = int(x1), int(y1), int(x2), int(y2)
        print(result)
        w, h = x2 -x1, y2 - y1
        cvzone.cornerRect(frame, (x1, y1, w, h), l=9, rt=2, colorR=(255,0,255))
        cvzone.putTextRect(frame, f'{int(id)}', (max(0, x1), max(35, y1)), scale = 2, thickness=3,offset=10)

        cx, cy = x1+w//2, y1+h//2
        cv2.circle(frame, (cx,cy), 5, (255,0,255), cv2.FILLED)
        
        if limits[0]<cx<limits[2] and limits[1]-30<cy<limits[1]+30:
            if totalCount.count(id) == 0:
                totalCount.append(id)
                cv2.line(frame, (limits[0], limits[1]), (limits[2], limits[3]), (0,0,255), 5)
    cvzone.putTextRect(frame, f'Count {len(totalCount)}',(50,50))

    # cv2.imshow('Region', imgRegion)
    cv2.imshow('Video', frame)
    cv2.waitKey(1)






