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
# import uart_communication


IP_MUTEX = None
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
  if IP_MUTEX == None or IP_MUTEX == requestIP or isAvailable != 0:

    IP_MUTEX = requestIP
    new_training = saveTraining(request)
    listOfPlay = getConvertShots(request)

    # Synchronous
    # Methdo to call uart communicatio and pass position
    # responsePosition = uart_communication.uart_communication_position(str(request.get_json()['launcherPosition']))

    # if(responsePosition == True):
    #     for play in listOfPlay:
    #         print(play)
    #         sendPlays(play)
    #         print('FOI?')
    #         time.sleep(3)

    # TODO recording video from shots

    # Assynchronous
    # TODO add Thread to execute this block
    # TODO add hawkeye analyses here
    analyze = AsynchronousAnalyze(new_training)
    analyze.start()


    response = 'Ok'

      # TODO Change local

  else:
    response = 'Fail'
    print("Ocupado...")

  return jsonify(response)


def getJsonPositions(mac, id_trainingResult):
  training_ = Training.query.filter(
      Training.id_trainingResult == id_trainingResult, Training.mac == str(mac)).first()
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


def sendPlays(play):
    # responseShot = uart_communication.uart_communication_shot(play)
    # if(responseShot == True):
    #     return True
    # else:
    #     sendPlays(play)
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
  response = os.system("ping -c 1 " + IP_MUTEX)
  # print("Response ping: " + str(response))
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
    print(id_training)
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

      print("----------------")
      savePositions(self.new_training.id_training)
      create_socket_notification(self.new_training.id_training, self.new_training.mac)

    def analyze_all_videos(self):
        list_results = []

        for k in range(1, 10, 2):
            thread_list = []
            for i in range(k, k+2):
                thread_list.append(AnalyzeVideo('../Dia23/video{}.h264'.format(i)))
            
            for index, thread in enumerate(thread_list):
                thread.start()

            for index, thread in enumerate(thread_list):
                thread.join()
                list_results.append(thread.candidate)

        return list_results

if __name__ == "__main__":
    app.run(host='0.0.0.0')
