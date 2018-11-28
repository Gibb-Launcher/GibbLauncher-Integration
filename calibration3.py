import cv2
import numpy as np
import imutils
import time
import math
from hawkeye import AnalyzeVideo

 
def calc_distance(itemA, itemB):
    return math.sqrt((itemB[0] - itemA[0])**2 + (itemB[1] - itemB[1])**2)

#cap = cv2.VideoCapture(0)
# cap = cv2.VideoCapture('../../Documents/PI2/Dia23/video001.h264')
def calc_all(ponto_quique, video, numb_frame):
    cap = cv2.VideoCapture(video)

    count = 0

    x0 = 175
    y0 = 282
    x1 = 10
    y1 = 390

    m = (x1 - x0)/(y1 - y0)
    frame_n = 0
    while True:

        _, frame = cap.read()
        if frame is not None:
            # frame = imutils.resize(frame, width=800, height=600)
            # cv2.circle(frame, (457, 379), 5, (0, 255, 255), -1)
            cv2.circle(frame, (170, 272), 5, (0, 0, 255), -1) #1 superior esquerdo
            cv2.circle(frame, (440, 283), 5, (0, 0, 255), -1) #2 superior direito
            cv2.circle(frame, (0, 385), 5, (0, 0, 255), -1) #3 inferior esquerdo
            cv2.circle(frame, (633, 399), 5, (0, 0, 255), -1) #4 inferior direito
        
            pts1 = np.float32([[173, 272], [440, 283], [6, 385], [633, 399]])
            #pts2 = np.float32([[0, 0], [500, 0], [0, 600], [500, 600]]) 
            #pts2 = np.float32([[0, 0], [0, 300], [800, 0], [800, 300]])
            #pts2 = np.float32([[0, 0], [600, 0], [0, 700], [600, 700]])
            #pts2 = np.float32([[175,282], [432, 291], [10,390], [615, 405]])
            pts2 = np.float32([[0, 0], [640, 0], [0, 480], [640, 480]])

            # Ambos dão o mesmo resultado
            matrix = cv2.getPerspectiveTransform(pts1, pts2)
            h, status = cv2.findHomography(pts1,pts2)
            """ 
            print(matrix)
            print('====================')
            print(h)
            print("\n")
            """
            # x = ((379-y0) - y0) /m  + x0
            # print(x)
            # d = calc_distance((0, 379-y0), (x ,379-y0))
            # print('=========')
            # Duas Maneiras de representar o ponto do quique do video 2
            # video 001
            # ponto_quique = np.array( [ [457.0],[379.0],[1.0] ] ) 
            # video 002
            # video 010
            # ponto_quique = np.array( [ [531.0],[449.0],[1.0] ] ) 
            # ponto_quique = [197.0, 427.0, 1.0 ]

            xa = matrix
            xb = ponto_quique

            # Maneiras de calcular a matrix. matrix_calculada (1x3) = H(3x3) * ponto_quique(1x3)
            #matrix_calculada =  np.mat(teste) * np.mat(ponto_quique)
            matrix_calculada = xa.dot(xb)
            xx = (matrix_calculada[0][0]/matrix_calculada[2][0])
            yy = (matrix_calculada[1][0]/matrix_calculada[2][0])
            print(xx, yy)

            # Serve para aplicar a homografia na imagem
            result = cv2.warpPerspective(frame, h, (640,480))

            # result = imutils.resize(result, width=800, height=600)
            cv2.circle(result, (int(xx), int(yy)), 5, (0, 255, 255), -1)

            cv2.imshow("Perspective transformation", result)
            cv2.imshow("Frame", frame)

            key = cv2.waitKey(1)
            if key == 27:
                break

            if(frame_n == numb_frame):
                time.sleep(1)
            frame_n += 1
        
        else:
            break

        

    
    cap.release()
    cv2.destroyAllWindows()

"""
1 Kika
2 Kika
3 Kika
4 Bate na Rede
5 Vai fora
6 Kika
7 Kika
8 Kika
9 Kika
10 Kika
"""

if __name__ == '__main__':
    for i in range(1, 11):
        test = AnalyzeVideo('../Dia23/video{}.h264'.format(i))
        test.start()
        test.join()
        print('=========Jogada {}========='.format(i))
        if(test.candidate):
            calc_all(np.array([[test.candidate[0][1][0][0]], [test.candidate[0][1][0][1]], [1.0]]), '../Dia23/video{}.h264'.format(i), test.candidate[0][0])
            # print(test.candidate[0][1][0][0], test.candidate[0][1][0][1])
    # cap = cv2.VideoCapture('../Dia23/video{}.h264'.format(i))

    # while True:
    #     _, frame = cap.read()

    #     if frame is not None:
    #         cv2.imshow("Frame{}".format(i), frame)
    #         time.sleep(0.02)

    #         key = cv2.waitKey(1)
    #         if key == 27:
    #             break
    #     else:
    #         break
