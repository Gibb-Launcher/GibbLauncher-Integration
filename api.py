from flask import Flask, jsonify, request
from datetime import datetime
from picamera import PiCamera
import time
import random
import os
import socket
from threading import Thread
from hawkeye import AnalyzeVideo, map_homography_point
from uart_communication import *
import queue


IP_MUTEX = None
camera = PiCamera()

analyse_videos = {}
OLD_POSITION = 2 #Sempre comeca no centro
analyze_queue = queue.Queue()
analyzing_training = False
app = Flask(__name__)

dictionary_shots_position = {(3, 'Forehand Cruzado - Longo'): 'a',
                             (3, 'Backhand Cruzado - Centro'): 'b',
                             (3, 'Backhand Paralelo - Longo'): 'c',
                             (3, 'Forehand Cruzado - Curto'): 'd',
                             (3, 'Backhand Paralelo - Curto'): 'e',
                             (2, 'Forehand Cruzado - Longo'): 'f',
                             (2, 'Backhand Paralelo - Centro'): 'g',
                             (2, 'Backhand Cruzado - Longo'): 'h',
                             (2, 'Forehand Cruzado - Curto'): 'i',
                             (2, 'Backhand Cruzado - Curto'): 'j',
                             (1, 'Forehand Paralelo - Longo'): 'k',
                             (1, 'Backhand Cruzado - Centro'): 'l',
                             (1, 'Backhand Cruzado - Longo'): 'm',
                             (1, 'Forehand Paralelo - Curto'): 'n',
                             (1, 'Backhand Cruzado - Curto'): 'o'}

#0 fica no mesmo lugar
# dictionary_positions = {(1,1): (0,'d'),
#                         (1,2): (15, 'd'),
#                         (1,3): (30, 'd'),
#                         (2,1): (15, 'e'),
#                         (2,2): (0, 'e'),
#                         (2,3): (15, 'd'),
#                         (3,1): (30, 'e'),
#                         (3,2): (15, 'e'),
#                         (3,3): (0, 'e') 
#                        }

@app.route('/positions', methods=['GET'])
def getTrainingResult():
  mac = request.args.get('mac', None)
  id_trainingResult = request.args.get('id_trainingResult', None)
  print('===============GET=====================\n')
  print(mac, id_trainingResult)
  print('====================================\n')

  JSON_ = getJsonPositions(mac, id_trainingResult)

  """
    {
        'id_trainingResult': 1,

        'bounces': [
          {
            'x': 50,
            'y': 17,
          },
          {
            'x': 25,
            'y': 10,
          },
        ]
    }
  """
  return jsonify(JSON_)

@app.route('/', methods=['POST'])
def start_request():
  global IP_MUTEX
  requestIP = str(request.get_json()['ip'])
  print('===============POST=====================\n')
  print(request.json)
  print('\n======================================\n')
  if IP_MUTEX == None or IP_MUTEX == requestIP or isAvailable():
    IP_MUTEX = requestIP
    new_training = saveTraining(request)
    listOfPlay = getConvertShots(request)
    
    play = listOfPlay[0]

    position = str(request.get_json()['launcherPosition'])
    """
    if position == '1':
        position = '3'
    elif position == '3':
        position = '1'
    """
    print("=============POSICAO NO TRILHO=================")
    responsePosition = uart_communication_position(position)
    time.sleep(5)
    print("=====================================")
    
    if(play == 'a'):
        angulo = 'A'
    elif (play == 'b'):
        angulo = 'B'
    elif (play == 'c'):
        angulo = 'C'
    elif (play == 'd'):
        angulo = 'D'
    elif (play == 'e'):
        angulo = 'E'
    elif (play == 'f'):
        angulo = 'F'
    elif (play == 'g'):
        angulo = 'G'
    elif (play == 'h'):
        angulo = 'H'
    elif (play == 'i'):
        angulo = 'I'
    elif (play == 'j'):
        angulo = 'J'
    elif (play == 'k'):
        angulo = 'K'
    elif (play == 'l'):
        angulo = 'L'
    elif (play == 'm'):
        angulo = 'M'
    elif (play == 'n'):
        angulo = 'N'
    elif (play == 'o'):
        angulo = 'O'
    else:
        print("Default")
    
    global camera
    if camera.recording:
      camera.stop_recording()
    if(responsePosition == True):
        print("=============ANGULO JOGADAS=================")
        responseAngle = uart_communication_angle(angulo)
        time.sleep(5)
        print("============================================")
        
        if( responseAngle == True):
            print("===========INICIAR MOTORES LANCAMENTO==============")
            uart_communication_shot('s')
            print("===================================================")
            time.sleep(5)
             
            
            for i in range(1,22):
                try:
                    camera.resolution = (640, 480)    
                    camera.start_recording('../videos/video_{}_{}.h264'.format(new_training['id_training'],i))
                except:
                    if camera.recording:
                      camera.stop_recording()
                    camera.resolution = (640, 480)    
                    camera.start_recording('../videos/video_{}_{}.h264'.format(new_training['id_training'],i))

                print("==============================")
                print("Enviando para o lancador a jogada",i)
                
                response = sendPlays(play)
                
               # time.sleep(2)
                if(response == True):
                    
                    print("[INFO]Jogada executada com sucesso")
                    continue
                else:
                    print("[ERRO]A jogada não foi realizada.")
                    #uart_communication_shot('p')
                    break
                print("==============================")
                
        else:
            print("[ERRO]O lancador nao foi posicionado no angulo correto")
    else:
            print("[ERRO]O lancador nao foi posicionado na posicao correta do trilho")
    
    if camera.recording:
      camera.stop_recording()

    time.sleep(5)

    if(play == 'a'):
        uart_communication_angle('4')
    elif (play == 'b'):
        uart_communication_angle('5')
    elif (play == 'c'):
        uart_communication_angle('6')
    elif (play == 'd'):
        uart_communication_angle('7')
    elif (play == 'e'):
        uart_communication_angle('8')
    elif (play == 'f'):
        uart_communication_angle('y')
    elif (play == 'g'):
        uart_communication_angle('w')
    elif (play == 'h'):
        uart_communication_angle('z')
    elif (play == 'i'):
        uart_communication_angle('r')
    elif (play == 'j'):
        uart_communication_angle('0')
    elif (play == 'k'):
        uart_communication_angle('9')
    elif (play == 'l'):
        uart_communication_angle('t')
    elif (play == 'm'):
        uart_communication_angle('u')
    elif (play == 'n'):
        uart_communication_angle('v')
    elif (play == 'o'):
        uart_communication_angle('x')
    else:
        print("Default")
    
    print("=============ENCERRANDO=================")
    time.sleep(5)
    print("[INFO]Enviando comando para parar motores de lancamento")
    uart_communication_shot('p')
    time.sleep(5)
    print("[INFO]Enviando comando para resetar posicao do lancador")
    uart_communication_shot('q')
    time.sleep(5)
    
    
    
    print("\o/ \o/ \o/ \o/Treino Finalizado\o/ \o/ \o/ \o/")
    print("==============================")
    

    # Assynchronous
    # TODO add Thread to execute this block
    # TODO add hawkeye analyses here

    #insert_queue(new_training)

    response = 'Ok'

      # TODO Change local

  else:
    response = 'Fail'
    print("Ocupado...")

  return jsonify(response)

def recordVideo(id_training, playNumber):
    camera = PiCamera()
    camera.resolution = (640, 480)

    #camera.start_preview()
    camera.start_recording('../videos/video_{}_{}.h264'.format(id_training,play_number))
    sleep(3) # Time of video recorded
    camera.stop_recording()
    #camera.stop_preview()
    print("Video Recorded")
    pass


def verify_analisys():
    global analyzing_training
    if not analyzing_training:
        analyzing_training = True
        #TODO - colocar para começar a análise no treino do ID, pegando o primeiro daa fila
        #TODO - Pegar o primeiro treino da fila Ronyell
        new_training = analyze_queue.get_nowait()
        analyze = AsynchronousAnalyze(new_training)
        analyze.start()


def verify_queue():
    if not analyze_queue.empty():
        verify_analisys()


def insert_queue(training):
    # TODO - colocar o id certo Ronyell
    analyze_queue.put(training)
    verify_analisys()


def getJsonPositions(mac, id_trainingResult):
  global analyse_videos
  analyse = analyse_videos[(int(id_trainingResult), mac)]

  print("===============BOUNCE LOCATION======================\n")
  print(analyse)
  print("\n====================================================\n")
  return analyse

def sendPlays(play):
    responseShot = uart_communication_shot(play)
    if(responseShot == True):
         return True
    else:
         sendPlays(play)
    return True


def getConvertShots(request):
  position = request.get_json()['launcherPosition']
  listOfShots = request.get_json()['shots']
  # List shots
  # print(listOfShots)

  listOfConvertShots = []

  for shot in listOfShots:
    listOfConvertShots.append(dictionary_shots_position.get((position, shot)))

  # List convert shots
  # print(listOfConvertShots)

  return listOfConvertShots


def isAvailable():
  if IP_MUTEX != None:
    response = os.system("ping -c 1 " + IP_MUTEX)
    if response == 0:
      response = False
    else:
      response = True
  else:
    response = False
  return response


def savePositions(id_trainingResult, mac, result):
  global analyse_videos
  analyse = {}
  analyse['id_training'] = id_trainingResult
  analyse['bounces']  = []
  for candidate in result:
    print(candidate)
    position_ = {}
    if(candidate):
      cord = map_homography_point(candidate[0][1][0][0], candidate[0][1][0][1])
      position_['x'] = cord[0]
      position_['y'] = cord[1]
    else:
      position_['x'] = -999
      position_['y'] = -999

    analyse['bounces'].append(position_)
    
  analyse_videos[(id_trainingResult, mac)] =  analyse
  print('------', analyse_videos)


def saveTraining(request):
  id_trainingResult_ = int(request.get_json()['id'])
  ip_ = str(request.get_json()['ip'])
  MAC = str(request.get_json()['mac'])
  #print(id_training, ip_, MAC)
  new_training = {}
  new_training['id_training'] = id_trainingResult_
  new_training['mac'] = MAC
  new_training['ip'] = ip_

  print("----------------SALVOU-------------------")
  return new_training


def create_socket_notification(id_training, mac, tr=0):
  try:
    #print(id_training)
    s = socket.socket()
    s.connect((IP_MUTEX , 4444))
    response = "A análise do seu treino esta pronta.;"+ mac + ";" + str(id_training)
    s.send(response.encode())
    s.close()
  except Exception as e:
    print('Erro no socket' + str(e))
    if tr <= 2:
        tr += 1
        create_socket_notification(id_training, mac, tr)

class AsynchronousAnalyze(Thread):
    def __init__(self, new_training):
        self.new_training = new_training
        super(AsynchronousAnalyze, self).__init__()

    def run(self):
      self.result = self.analyze_all_videos()

      print("*************************", self.new_training['id_training'], '************************')
      savePositions(self.new_training['id_training'], self.new_training['mac'], self.result)
      time.sleep(1)
      create_socket_notification(self.new_training['id_training'], self.new_training['mac'])

    def analyze_all_videos(self):
        list_results = []

        for k in range(1, 10, 2):
            global analyzing_training

            thread_list = []
            print(k, k+1)
            for i in range(k, k+2):
                print('../videos/video_{}_{}.h264'.format(self.new_training['id_training'],i))
                thread_list.append(AnalyzeVideo('../videos/video_{}_{}.h264'.format(self.new_training['id_training'],i)))

            for index, thread in enumerate(thread_list):
                thread.start()

            for index, thread in enumerate(thread_list):
                thread.join()
                list_results.append(thread.candidate)
                # if os.path.exists(thread.video_path):
                #   os.remove(thread.video_path)


        analyzing_training = False
        verify_queue()
        return list_results

if __name__ == "__main__":
    app.run(host='0.0.0.0')

