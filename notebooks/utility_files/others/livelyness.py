import cv2
import time
import math
import random
import numpy as np
import mediapipe as mp

LEFT_EYE_OUTER, LEFT_EYE_INNER, LEFT_EYE_UPPER, LEFT_EYE_LOWER = 33, 133, 159, 145
RIGHT_EYE_OUTER, RIGHT_EYE_INNER, RIGHT_EYE_UPPER, RIGHT_EYE_LOWER = 263, 362, 386, 374
MOUTH_LEFT, MOUTH_RIGHT, MOUTH_UP, MOUTH_DOWN = 61, 291, 13, 14
NOSE_TIP, CHIN = 1, 199

NUM_CHALLENGES = 4
CHALLENGE_DURATION = 3.5 

def _euclidean(p, q): 
    return math.hypot(p[0]-q[0], p[1]-q[1])

def _get_point(landmarks, idx, w, h): 
    return np.array([landmarks[idx].x*w, landmarks[idx].y*h], dtype=np.float64)

def eye_aspect_ratio(landmarks, w, h, side="left"):
    if side == "left":
        upper = _get_point(landmarks, LEFT_EYE_UPPER, w, h)
        lower = _get_point(landmarks, LEFT_EYE_LOWER, w, h)
        outer = _get_point(landmarks, LEFT_EYE_OUTER, w, h)
        inner = _get_point(landmarks, LEFT_EYE_INNER, w, h)
    else:
        upper = _get_point(landmarks, RIGHT_EYE_UPPER, w, h)
        lower = _get_point(landmarks, RIGHT_EYE_LOWER, w, h)
        outer = _get_point(landmarks, RIGHT_EYE_OUTER, w, h)
        inner = _get_point(landmarks, RIGHT_EYE_INNER, w, h)
    vertical, horizontal = _euclidean(upper, lower), _euclidean(outer, inner)

    return vertical / horizontal if horizontal > 0 else 0.0

def inter_ocular_distance(landmarks, w, h):

    leftEye = _get_point(landmarks, LEFT_EYE_OUTER, w, h)
    rightEye = _get_point(landmarks, RIGHT_EYE_OUTER, w, h)

    return _euclidean(leftEye, rightEye)

def smile_metric(landmarks, w, h):

    iod = inter_ocular_distance(landmarks, w, h)
    mouthLeft = _get_point(landmarks, MOUTH_LEFT, w, h)
    mouthRight = _get_point(landmarks, MOUTH_RIGHT, w, h)

    return _euclidean(mouthLeft, mouthRight) / iod if iod else 0.0

def mouth_open_metric(landmarks, w, h):

    iod = inter_ocular_distance(landmarks, w, h)
    mouthUp = _get_point(landmarks, MOUTH_UP, w, h)
    mouthDown = _get_point(landmarks, MOUTH_DOWN, w, h)

    return _euclidean(mouthUp, mouthDown) / iod if iod else 0.0

def head_pose_angles(landmarks, w, h):

    pts2d_idx = [NOSE_TIP, CHIN, LEFT_EYE_OUTER, RIGHT_EYE_OUTER, MOUTH_LEFT, MOUTH_RIGHT]  # points in 2d
    pts_2d = np.array([_get_point(landmarks, i, w, h) for i in pts2d_idx], dtype=np.float64)

    pts_3d = np.array([[0,0,0],[0,-63.6,-12.5],[-43.3,32.7,-26],[43.3,32.7,-26],[-28.9,-28.9,-24.1],[28.9,-28.9,-24.1]], dtype=np.float64)
    camera_matrix = np.array([[w,0,w/2],[0,w,h/2],[0,0,1]], dtype=np.float64)

    success, rvec, tvec = cv2.solvePnP(pts_3d, pts_2d, camera_matrix, np.zeros((4,1)), flags=cv2.SOLVEPNP_ITERATIVE)

    if not success: 
        return 0.0,0.0,0.0
    
    rot_matrix,_ = cv2.Rodrigues(rvec)

    sy = math.sqrt(rot_matrix[0,0]**2+rot_matrix[1,0]**2)
    singular = sy < 1e-6

    if not singular: 
        pitch = math.atan2(-rot_matrix[2,0],sy)
        yaw = math.atan2(rot_matrix[1,0],rot_matrix[0,0])
        roll = math.atan2(rot_matrix[2,1],rot_matrix[2,2])

    else: 
        pitch = math.atan2(-rot_matrix[2,0],sy)
        yaw = math.atan2(-rot_matrix[0,1],rot_matrix[1,1])
        roll = 0
        
    return math.degrees(yaw), math.degrees(pitch), math.degrees(roll)


class BlinkDetector:
    def __init__(self, ear_thresh=0.21, min_consec_frames=2): self.ear_thresh, self.min_consec_frames, self.counter, self.total_blinks = ear_thresh, min_consec_frames, 0, 0
    def update(self, ear_left, ear_right):
        ear, blinked = (ear_left+ear_right)/2, False
        if ear < self.ear_thresh: self.counter += 1
        else:
            if self.counter >= self.min_consec_frames: self.total_blinks += 1; blinked = True
            self.counter = 0
        return blinked


class Challenge:
    def __init__(self, timeout_sec=6.0): 
        self.timeout_sec = timeout_sec
        self.start_time = None
        self.done = False
        self.success = False

    def start(self): 
        self.start_time = time.time()
        self.done =  False
        self.success = False

    def expired(self): 
        return (time.time()-self.start_time) > self.timeout_sec
    
    def instructions(self): 
        return "Follow the instruction"
    
    def update(self, signal): 
        pass

class BlinkN(Challenge):
    def __init__(self,n=2,timeout_sec=6.0): 
        super().__init__(timeout_sec)
        self.n = n
        self.blinks_detected = 0

    def instructions(self): 
        return f"Blink {self.n} time(s)"
    
    def update(self,signal):
        if self.done: 
            return
        if signal.get('blinked'): 
            self.blinks_detected+=1

        if self.blinks_detected>=self.n: 
            self.done = True
            self.success=True

        elif self.expired(): 
            self.done = True
            self.success = False

class TurnHead(Challenge):
    def __init__(self,direction="left",angle_thresh=8.0,timeout_sec=6.0): 
        super().__init__(timeout_sec)
        self.direction,self.angle_thresh=direction,angle_thresh

    def instructions(self): 
        return f"Turn head {self.direction.upper()}"
    
    def update(self,signal):
        if self.done: 
            return
        yaw = signal.get('yaw',0.0)
        pitch = signal.get('pitch',0.0)

        if (self.direction=='left' and yaw<-self.angle_thresh) or (self.direction=='right' and yaw>self.angle_thresh) or (self.direction=='up' and pitch<-self.angle_thresh) or (self.direction=='down' and pitch>self.angle_thresh): 
            self.done =  True
            self.success = True

        elif self.expired(): 
            self.done = True
            self.success = False

class Smile(Challenge):
    def __init__(self,thresh=0.42,timeout_sec=6.0): 
        super().__init__(timeout_sec)
        self.thresh=thresh

    def instructions(self): 
        return "Smile"
    def update(self,signal):
        if self.done: 
            return
        
        if signal.get('smile',0.0) > self.thresh: 
            self.done = True 
            self.success = True

        elif self.expired(): 
            self.done = True
            self.success = False

class MouthOpen(Challenge):
    def __init__(self,thresh=0.20,timeout_sec=6.0): 
        super().__init__(timeout_sec)
        self.thresh=thresh

    def instructions(self): 
        return "Open your mouth"
    
    def update(self,signal):
        if self.done: 
            return
        
        if signal.get('mouth_open',0.0)>self.thresh: 
            self.done = True
            self.success = True

        elif self.expired(): 
            self.done = True
            self.success = False


def next_random_challenge():

    choice = random.choice(['blink','turn','smile','mouth'])

    if choice=='blink': 
        return BlinkN(n=random.choice([1,2]),timeout_sec=CHALLENGE_DURATION)
    
    if choice=='turn': 
        return TurnHead(direction=random.choice(['left','right','up','down']),angle_thresh=8.0,timeout_sec=CHALLENGE_DURATION)
    
    if choice=='smile': 
        return Smile(thresh=0.20,timeout_sec=CHALLENGE_DURATION)
    
    return MouthOpen(thresh=0.20,timeout_sec=CHALLENGE_DURATION)


def main():
    test_success_count = 0
    cap = cv2.VideoCapture(0)

    if not cap.isOpened(): 
        raise SystemExit("Cannot open camera")
    
    mp_face_mesh = mp.solutions.face_mesh

    face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False,
                                      max_num_faces=1,
                                      refine_landmarks=True,
                                      min_detection_confidence=0.5,
                                      min_tracking_confidence=0.5)
    
    blink_detector=BlinkDetector()

    challenge_count,challenge=1,next_random_challenge(); challenge.start()

    print(f"Challenge {challenge_count}: {challenge.instructions()}")

    while True:
        ret,frame=cap.read()
        if not ret: 
            break
        frame = cv2.flip(frame,1)
        h,w = frame.shape[:2]
        rgb = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
        results = face_mesh.process(rgb)

        ear_l = ear_r = yaw = pitch = roll = smile_m = mouth_m = 0.0
        blinked=False

        if results.multi_face_landmarks:

            landmarks=results.multi_face_landmarks[0].landmark
            ear_l = eye_aspect_ratio(landmarks,w,h,"left")
            ear_r = eye_aspect_ratio(landmarks,w,h,"right")
            yaw, pitch, roll = head_pose_angles(landmarks,w,h)
            smile_m = smile_metric(landmarks,w,h)
            mouth_m = mouth_open_metric(landmarks,w,h)
            blinked=blink_detector.update(ear_l,ear_r)

        signal={'blinked':blinked,'yaw':yaw,'pitch':pitch,'roll':roll,'smile':smile_m,'mouth_open':mouth_m}
        challenge.update(signal)

        cv2.rectangle(frame,(0,0),(w,80),(0,0,0),-1)
        cv2.putText(frame,
                    f"Challenge {challenge_count}/{NUM_CHALLENGES}: {challenge.instructions()}",(16,48),
                    cv2.FONT_HERSHEY_SIMPLEX,1.0,(255,255,255),2,cv2.LINE_AA)

        if challenge.done:

            color=(0,255,0) if challenge.success else (0,0,255)

            cv2.putText(frame,"PASS" if challenge.success else "FAIL",(w-150,48),cv2.FONT_HERSHEY_SIMPLEX,1.2,color,3,cv2.LINE_AA)

            if challenge.success:
                test_success_count += 1

            cv2.imshow("Liveness",frame)
            cv2.waitKey(1000)  # small pause to show result
            challenge_count+=1

            if challenge_count>NUM_CHALLENGES: 
                print("Liveness check completed.")
                break

            challenge=next_random_challenge(); challenge.start()

            print(f"Challenge {challenge_count}: {challenge.instructions()}")
    

        cv2.imshow("Liveness",frame)
        if cv2.waitKey(1)&0xFF==ord('q'): 
            break
    
    if test_success_count > NUM_CHALLENGES//2:
        print(f"Liveness Detection: True || {test_success_count}/{NUM_CHALLENGES} passed !")
    else:
        print(f"Liveness Detection: False || {test_success_count}/{NUM_CHALLENGES} passed !")

    cap.release(); cv2.destroyAllWindows()

if __name__=="__main__":
    main()
