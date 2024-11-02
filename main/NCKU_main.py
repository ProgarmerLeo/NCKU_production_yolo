import logging
import cv2
import serial
from ultralytics import YOLO
import time
import sys
import json

class Timer():
    def __init__(self) -> None:
        self.start = False

    def timing(self, ticks):  # seconds
        if not self.start:
            self.start = round(time.time(), 3)
        now = round(time.time(), 3)
        if now - self.start >= ticks:
            self.start = False
            return True
        return False

def send_msg(ser: serial.Serial, msg: str):
    ser.write(bytes(msg.encode()) + b"\n")

# Set logging level to ERROR to hide INFO messages
logging.getLogger("ultralytics").setLevel(logging.ERROR)

INPUT_INTERVAL = 8.5  # seconds
DEFECTION_INTERVAL = 1.3  # seconds
RECT_INTERVAL = 2.25
COM_PORT = "COM6"
INPUT = "INPUT"
DEFECT = "DEFECT"
BAUD_RATES = 9600
SERIAL = True

running = True
detactions = 10
detactions_total = 0
trace = 0
hole = 0
missing = 0
trace_flag = 0
hole_flag = 0
missing_flag = 0
trace_rate = 0
hole_rate = 0
missing_rate = 0
blemishe_total = 0
blemish_rate = 0
detected = False

timer_input = Timer()
timer_defect = Timer()
time_rect = Timer()
rectangle = False
blemished = False

model = YOLO(r"E:\下載\NCKU_try.v2i.yolov11\runs\detect\train\weights\best.pt")
cap = cv2.VideoCapture(1)  # Using webcam



if SERIAL:
    ser = serial.Serial(COM_PORT, BAUD_RATES, bytesize=8, parity="N", stopbits=1, timeout=1)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    
    results = model(frame)
    detections = results[0].boxes
    for box in detections:
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        conf = box.conf[0]
        cls = int(box.cls[0])
        label = f"{model.names[cls]} {conf:.2f}"
        
        if model.names[cls] == "rectangle" and conf >= 0.6:
            rectangle = True
        elif conf >= 0.6 :
            if model.names[cls] == "trace":
                trace_flag = True
            elif model.names[cls] == "hole":
                hole_flag = True
            elif model.names[cls] == "missing":
                missing_flag = True
            blemished = True
        
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(frame, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    
    cv2.imshow("Image", frame)
    
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

    if SERIAL:
        if timer_input.timing(INPUT_INTERVAL):
            if rectangle :
                detactions_total += 1
            detected = False
            print(999)
            rectangle = False
            trace_flag = False
            hole_flag = False
            missing_flag = False
            send_msg(ser, INPUT)
            blemished = False
        
        if rectangle and timer_defect.timing(DEFECTION_INTERVAL):
            if blemished and not detected:
                if trace_flag:
                    trace += 1
                if hole_flag:
                    hole += 1
                if missing_flag:
                    missing += 1  
                blemished = False
                detected = True
                blemishe_total += 1
                send_msg(ser, DEFECT)
                print("yes")
        
        if detactions_total == detactions:
            break

        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').rstrip()
            if line == "stop":
                running = False
            elif line == "run":
                running = True
        

    # Read em_stop value from JSON file
    with open(r'C:\Users\HanX\Desktop\NCKU__proj\web\data.json', 'r') as json_file:
        data = json.load(json_file)
        em_stop = data.get("em_stop", False)  # Default to False if not found

    # Send em_stop value to Arduino
    send_msg(ser, "EM_STOP_ON" if em_stop else "EM_STOP_OFF") 
    if em_stop : 
        print("stopped")
        sys.exit()

    if detactions_total:
        blemish_rate = blemishe_total / detactions_total if detactions_total else 0
        trace_rate = trace / detactions_total if detactions_total else 0
        hole_rate = hole / detactions_total if detactions_total else 0
        missing_rate = missing / detactions_total if detactions_total else 0
        
        # Update JSON data
        data = {
            "detactions_total": detactions_total,
            "blemishe_total": blemishe_total,
            "trace_rate": round(trace_rate,1),
            "hole_rate": round(hole_rate,1),
            "missing_rate": round(missing_rate,1),
            "blemish_rate": round(blemish_rate,1),
            "status": "running" if running else "stopped"
        }
        with open(r'C:\Users\HanX\Desktop\NCKU__proj\web\data.json', 'w') as json_file:
            json.dump(data, json_file)

cap.release()
cv2.destroyAllWindows()
