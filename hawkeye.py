import numpy as np
import cv2
import sys
import imutils
import time
import math
from sklearn.svm import SVC
import candidate
from threading import Thread


def check_movement(shadow_frame, frame, balls_traking, timestamp):
    (im2, contours, hierarchy) = cv2.findContours(
        shadow_frame.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    candidates = np.empty((0, 3))
    for contour in contours:
        if cv2.contourArea(contour) < 10:
            continue
        M = cv2.moments(contour)
        if(M["m00"] == 0.0):
            center = (M["m10"], M["m01"])
        else:
            center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))  # aqui
        candidates = np.append(candidates, np.array(
            [np.array([int(center[0]), int(center[1]), int(timestamp)])]), axis=0)

    points = np.empty((0, 3))
    if candidates.shape[0] > 1:
        q1 = candidates[(candidates[:, 0] >= 0) & (candidates[:, 0] <= 160)]
        q2 = candidates[(candidates[:, 0] > 160) & (candidates[:, 0] <= 320)]
        q3 = candidates[(candidates[:, 0] > 320) & (candidates[:, 0] <= 480)]
        q4 = candidates[(candidates[:, 0] > 480) & (candidates[:, 0] <= 640)]

        if q1.shape[0] <= 3:
            points = np.append(points, q1, axis=0)
        if q2.shape[0] <= 3:
            points = np.append(points, q2, axis=0)
        if q3.shape[0] <= 3:
            points = np.append(points, q3, axis=0)
        if q4.shape[0] <= 3:
            points = np.append(points, q4, axis=0)
    elif candidates.shape[0] == 1:
        points = np.append(points, np.array(
            [np.array([candidates[0][0], candidates[0][1], candidates[0][2]])]), axis=0)

    for point in points:
        cv2.circle(frame, (int(point[0]), int(point[1])), 4, 255, 5)
        balls_traking.append([int(point[0]), int(point[1]), int(point[2])])


class AnalyzeVideo(Thread):
    def __init__(self, video_path):
        self.candidate = None
        self.video_path = video_path
        super(AnalyzeVideo, self).__init__()

    def run(self):
        self.candidate = self.analyze_video()

        if self.candidate is not None:
            print("O candidato esta no frame :{}.\nEle é: {}".format(
                self.candidate[0][0], self.candidate[0][1]))
        else:
            print("Provavelmente não houve quique!")

    def analyze_video(self):
        # read video file
        cap = cv2.VideoCapture(self.video_path)

        fgbg = cv2.createBackgroundSubtractorKNN(history=1)
        number_frame = 0
        kernel = np.ones((5, 5), np.uint8)
        timestamp = 0
        candidates = []
        
        while (True):

            ret, frame = cap.read()
            number_frame += 1

            if frame is None:
                break
            if ret == True:
                fgmask = cv2.GaussianBlur(frame, (5, 5), 0)

                fgmask = cv2.morphologyEx(
                    fgmask, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_CROSS, (5, 5)))
                fgmask = cv2.dilate(fgmask, kernel, iterations=1)
                fgmask = cv2.morphologyEx(fgmask, cv2.MORPH_ERODE, kernel)

                fgmask = fgbg.apply(fgmask)

                intensity, frameRemoveShadow = cv2.threshold(
                    fgmask, 0, 255, cv2.THRESH_BINARY)

                check_movement(frameRemoveShadow, frame, candidates, timestamp)

                # cv2.imshow('foreground and background', frameRemoveShadow)
                # cv2.imshow('rgb', frame)

                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break

                timestamp += 1

        cap.release()
        cv2.destroyAllWindows()
        print(candidates)
        return candidate.start_verification(candidates)


def map_homography_point(bounce_x, bounce_y):
    pts1 = np.float32([[219, 351], [545, 365], [10, 490], [793, 512]])
    pts2 = np.float32([[0, 0], [800, 0], [0, 600], [800, 600]])

    # Ambos dão o mesmo resultado
    matrixH = cv2.getPerspectiveTransform(pts1, pts2)
    bounce_coord = np.array([[float(bounce_x)], [float(bounce_y)], [1.0]])

    xa = matrixH
    xb = bounce_coord

    # Calculate resulting matrix. resulting_matrix (1x3) = matrixH(3x3) * bounce_coord(1x3)
    resulting_matrix = xa.dot(xb)
    xx = (resulting_matrix[0][0]/resulting_matrix[2][0])
    yy = (resulting_matrix[1][0]/resulting_matrix[2][0])

    homography_coord = [xx, yy]
    return homography_coord


if __name__ == '__main__':
    # init = AsynchronousAnalyze()
    # init.start()
    init = AnalyzeVideo('../Dia23/video2.h264')
    init.start()
    init.join()

    # candidate = analyze_video('videos/video002.h264')
    # if candidate is not None:
    #     #print("O candidato esta no frame :{}.\nEle é: {}".format(candidate[0][0], candidate[0][1]))
    #     bounce_x = float(candidate[0][1][0][0])
    #     bounce_y = float(candidate[0][1][0][1])

    #     homography_point = map_homography_point(bounce_x,bounce_y)
    #     print(homography_point)
    # else:
    #     print("Provavelmente não houve quique!")
