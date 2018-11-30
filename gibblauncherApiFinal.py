from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect
from flask import Flask, jsonify, request
from datetime import datetime
import time
import random
import os
import socket
from threading import Thread
from hawkeye import AnalyzeVideo
#import uart_communication
import queue


IP_MUTEX = None
OLD_POSITION = 2 #Sempre começa no centro
analyze_queue = queue.Queue()
analyzing_training = False
app = Flask(__name__)
basedir = basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
    os.path.join(basedir, 'gibb.db')
db = SQLAlchemy(app,session_options={"autoflush": False, "autocommit": False, "expire_on_commit": False})
db.create_all()

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

class Training(db.Model):
  __tablename__ = "training"
  id_training = db.Column(db.Integer, primary_key=True)
  id_trainingResult = db.Column(db.Integer, nullable=False)
  mac = db.Column(db.String(20), nullable=False)
  ip = db.Column(db.String(15), nullable=False)
  postions = db.relationship(
      'PositionShot', backref='training_positionShot', lazy=True)


class PositionShot(db.Model):
  __tablename__ = "positionShot"
  id_positionShot = db.Column(db.Integer, primary_key=True)
  training_id = db.Column(db.Integer, db.ForeignKey(
      'training.id_training'), nullable=False)
  postiionX = db.Column(db.Integer, nullable=False)
  postiionY = db.Column(db.Integer, nullable=False)


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

    # Synchronous
    # Methdo to call uart communicatio and pass 
          '''Caso o fim de curso para de funcionar
          # dict_position = dictionary_positions(OLD_POSITION, request.get_json()['launcherPosition'])
          # responsePosition = uart_communication.uart_communication_position(str(dict_position[1]))
            time.sleep(dict_position[0])
            responsePosition = uart_communication.uart_communication_position('z')
          '''
    # responsePosition = uart_communication.uart_communication_position(str(request.get_json()['launcherPosition']))
    # 
    # if(responsePosition == True):
         #time.sleep() #Posi
    #     # Start engines to launch balls
    #     sendPlays('s')
    #     time.sleep(3)
    #     for play in listOfPlay:
    #         print(play)
    #         sendPlays(play)
    #         time.sleep()
    #time.sleep(3)
    position = str(request.get_json()['launcherPosition'])
    if position == '1':
        position = '3'
    elif position == '3':
        position = '1'
    
    responsePosition = uart_communication_position(position)
    time.sleep(7)
    
    
    if(responsePosition == True):
        uart_communication_shot('s')
        time.sleep(10)
        for i in range(1,11):
            # print(listO)
            
            print("Mandando a jogada",i)
            response = sendPlays('a')
            # Começar a gravar bem aqui
            #TODO colocar o tempo de sleep de gravar
            recordVideo(new_training.id_training, i)
            
            time.sleep(5)
            if(response == True):
                print("Confirmou a execução da jogada")
                continue
            else:
                print("Deu ruim")
                uart_communication_shot('p')
                break
            
            time.sleep(8)
    
    time.sleep(5)
    uart_communication_shot('p')
    time.sleep(3)
    uart_communication_shot('q')
    print("Deu bom")


    # Assynchronous
    # TODO add Thread to execute this block
    # TODO add hawkeye analyses here

    insert_queue(new_training)

    response = 'Ok'

      # TODO Change local

  else:
    response = 'Fail'
    print("Ocupado...")

  return jsonify(response)

def recordVideo(id_training, playNumber):
    camera = PiCamera()
    camera.resolution = (640, 480)
    #camera.framerate = 120

    #camera.start_preview()
    camera.start_recording('../videos/video_{}_{}.h264'.format(id_training,play_number))
    sleep(3) # Time of video recorded
    camera.stop_recording()
    #camera.stop_preview()
    print("Video Recorded")


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
  training_ = Training.query.filter(
      Training.id_trainingResult == id_trainingResult, Training.mac == str(mac)).first()
  print(training_)

  list_positionsShot_ = PositionShot.query.filter_by(
      training_id=training_.id_training).all()

  response_bounces = {
        'id_trainingResult': training_.id_trainingResult,
        'bounces': [
            {
              'x': list_positionsShot_[0].postiionX,
              'y': list_positionsShot_[0].postiionY,
            },
            {
              'x': list_positionsShot_[1].postiionX,
              'y': list_positionsShot_[1].postiionY,
            },
            {
              'x': list_positionsShot_[2].postiionX,
              'y': list_positionsShot_[2].postiionY,
            },
            {
              'x': list_positionsShot_[3].postiionX,
              'y': list_positionsShot_[3].postiionY,
            },
            {
              'x': list_positionsShot_[4].postiionX,
              'y': list_positionsShot_[4].postiionY,
            },
            {
              'x': list_positionsShot_[5].postiionX,
              'y': list_positionsShot_[5].postiionY,
            },
            {
              'x': list_positionsShot_[6].postiionX,
              'y': list_positionsShot_[6].postiionY,
            },
            {
              'x': list_positionsShot_[7].postiionX,
              'y': list_positionsShot_[7].postiionY,
            },
            {
              'x': list_positionsShot_[8].postiionX,
              'y': list_positionsShot_[8].postiionY,
            },
            {
              'x': list_positionsShot_[9].postiionX,
              'y': list_positionsShot_[9].postiionY,
            },
        ]
    }
  print("===============BOUNCE LOCATION======================\n")
  print(response_bounces)
  print("\n====================================================\n")
  return response_bounces


# def sendPlays(play):
#     responseShot = uart_communication.uart_communication_shot(play)
#     if(responseShot == True):
#          return True
#     else:
#          sendPlays(play)
#     return True


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


def savePositions(id_trainingResult):
  for i in range(10):
    position_ = PositionShot()
    position_.training_id = id_trainingResult
    position_.postiionX = random.randint(-100,100)
    position_.postiionY = random.randint(-100,100)

    # Save in Database
    db.session.add(position_)
    db.session.commit()

def saveTraining(request):
  id_trainingResult_ = int(request.get_json()['id'])
  ip_ = str(request.get_json()['ip'])
  MAC = str(request.get_json()['mac'])
  new_training = Training()
  new_training.id_trainingResult = id_trainingResult_
  new_training.mac = MAC
  new_training.ip = ip_

  # Save in Database
  db.session.add(new_training)
  db.session.commit()
  return new_training

def create_socket_notification(id_training, mac):
  try:
    #print(id_training)
    s = socket.socket()
    s.connect((IP_MUTEX , 4444))
    response = "Você é um batatão! Errou quase Tudo.;"+ mac + ";" + str(id_training)
    s.send(response.encode())
    s.close()
  except Exception as e:

    print('Erro no socket' + str(e))

class AsynchronousAnalyze(Thread):
    def __init__(self, new_training):
        self.new_training = new_training
        super(AsynchronousAnalyze, self).__init__()

    def run(self):
      self.result = self.analyze_all_videos()

      print("----------------", self.new_training.id_training, self.new_training.id_trainingResult)
      savePositions(self.new_training.id_training)
      time.sleep(1)
      create_socket_notification(self.new_training.id_training, self.new_training.mac)

    def analyze_all_videos(self):
        list_results = []

        for k in range(1, 10, 2):
            global analyzing_training

            thread_list = []
            for i in range(k, k+2):
                #TODO - Colocar o id certo Ronyell
                thread_list.append(AnalyzeVideo('../videos/video_{}_{}.h264'.format(self.new_training.id_training,i)))

            for index, thread in enumerate(thread_list):
                thread.start()

            for index, thread in enumerate(thread_list):
                thread.join()
                list_results.append(thread.candidate)
                if os.path.exists(thread.video_path):
                  os.remove(thread.video_path)


        analyzing_training = False
        verify_queue()
        return list_results

if __name__ == "__main__":
    app.run(host='0.0.0.0')
