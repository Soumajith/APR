from ultralytics import YOLO
import cv2
from time import time
import os

model = YOLO("yolov11n-face.pt")

# ********** Parameter Variables ************* #
offsetW = 10
offsetH = 15
detection_confidence = 0.75
camWidth = 640
camHeight = 480
blurThres = 80
save = True
debug = False
classId = 1 # 0 = Fake, 1 = Real
output_dir = 'dataset/data'
all_dir = 'all'
class_name = 'real'

# ******************************************** #

base_dir = os.path.dirname(os.path.abspath(__file__))
output_path = os.path.join(base_dir,output_dir,class_name)
all_path = os.path.join(base_dir,output_dir,all_dir)
os.makedirs(output_path, exist_ok=True)
os.makedirs(all_path, exist_ok=True)
cap = cv2.VideoCapture(1)
cap.set(3,camWidth)
cap.set(4,camHeight)

while True:
    ret, frame = cap.read()
    frameDisp = frame.copy()
    if not ret:
        break

    listBlur = [] # True and false values that indicate whether face blur or not
    listInfo = [] # Normalized values and class name for the label txt file
    results = model(frame,verbose = False)

    for box in results[0].boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        conf = float(box.conf[0])

        if conf > detection_confidence:

            w = abs(x2-x1)
            h = abs(y2-y1)

            widthOffset = int((offsetW/100)*w)
            heightOffset = int((offsetH/100)*h)

            x1 = x1 - widthOffset
            x2 = x2 + widthOffset

            y1 = y1 - heightOffset*2
            y2 = y2 + int(heightOffset*0.5)

            if x1 < 0: x1 = 0
            if x2 < 0: x2 = 0
            if y1 < 0: y1 = 0
            if y2 < 0: y2 = 0

            # Normalizing values
            ih, iw, _ = frame.shape
            xc = x1 + (x2-x1)/2
            yc = y1 + (y2-y1)/2

            xcn = round(xc/iw,6)
            ycn = round(yc/ih,6)
            wcn = round((x2-x1)/iw,6)
            hcn = round((y2-y1)/ih,6)

            # Avoiding values above 1
            if xcn > 1: xcn = 1
            if ycn > 1: ycn = 1
            if wcn > 1: wcn = 1
            if hcn > 1: hcn = 1

            face_region = frame[y1:y2,x1:x2]

            blurV = int(cv2.Laplacian(face_region, cv2.CV_64F).var())
            if blurV > blurThres:
                listBlur.append(True)
            else:
                listBlur.append(False)

            listInfo.append(f'{classId} {xcn} {ycn} {wcn} {hcn}\n')
            

            cv2.rectangle(frameDisp, (x1, y1), (x2, y2), (0, 255, 0), 2)

            cv2.putText(frameDisp, f'Blur: {blurV}', (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
            if debug:
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

                cv2.putText(frame, f'Blur: {blurV}', (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    #print(listBlur)

    # saving image and image metadata
    if save:
        if all(listBlur) and len(listBlur) != 0:
            t = str(time())
            t = t.split('.')
            t =  t[0] + '_' + t[1]
            cv2.imwrite(f'{output_path}/{t}.jpg',frame)
            cv2.imwrite(f'{all_path}/{t}.jpg', frame)
            print(f"Saved: {output_path}/{t}.jpg")
            
            for info in listInfo:
                f = open(f'{output_path}/{t}.txt','a')
                f.write(info)
                f.close()

                f2 = open(f'{all_path}/{t}.txt','a')
                f2.write(info)
                f2.close()
        
    cv2.imshow("Face detection", frameDisp)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
