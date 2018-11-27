from flask import Flask, jsonify, request
import time
import random
import os
import hawkeye
import uart_communication


IP_MUTEX = None
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

@app.route('/', methods=['GET'])
def hello():
  return jsonify({'data': "Get Confirm!"})

def sendPlays(play):
    responseShot = uart_communication.uart_communication_shot(play)
    if(responseShot == True):
        return True
    else:
        sendPlays(play)

@app.route('/', methods=['POST'])
def start_request():
  global IP_MUTEX
  requestIP = str(request.get_json()['ip'])

  if IP_MUTEX == None or IP_MUTEX == requestIP:
    # print("IP_MUTEX = " + str(IP_MUTEX))
    IP_MUTEX = requestIP
    listOfPlay = getPlay(request)

    #TODO put method call file C passing listOfPlay
    responsePosition = uart_communication.uart_communication_position(str(request.get_json()['launcherPosition']))
        
    if(responsePosition == True):
        for play in listOfPlay:
            print(play)
            sendPlays(play)
            print('FOI?')
            time.sleep(3)

    response = set_players()
  else :
    response = checkIp(requestIP)

  return jsonify(response)


def getPlay(request):
  position = request.get_json()['launcherPosition']
  
  listOfShots = request.get_json()['shots']
  
  listOfConvertShots = []

  for shot in listOfShots:
    listOfConvertShots.append(dictionary_shots_position.get((position, shot)))

  print(listOfConvertShots)

  return listOfConvertShots

def checkIp(requestIP):
  global IP_MUTEX
  if isAvailable() != 0 :
    # print("verificou o ip")
    responseJson = set_players()
    IP_MUTEX = requestIP 
  else :
    responseJson = {'data': "Ocupado!"}
    print("Ocupado...")

  return responseJson

def isAvailable() :
  response = os.system("ping -c 1 " + IP_MUTEX)
  # print("Response ping: " + str(response))
  return response

def set_players():

    bounces = hawkeye.get_bounces()

    response_bounces = {
        'bounces': [
            {
              'x': bounces[0][0],
              'y': bounces[0][1],
            },
            {
              'x': bounces[1][0],
              'y': bounces[1][1],
            },
            {
              'x': bounces[2][0],
              'y': bounces[2][1],
            },
            {
              'x': bounces[3][0],
              'y': bounces[3][1],
            },
            {
              'x': bounces[4][0],
              'y': bounces[4][1],
            },
            {
              'x': bounces[5][0],
              'y': bounces[5][1],
            },
            {
              'x': bounces[6][0],
              'y': bounces[6][1],
            },
            {
              'x': bounces[7][0],
              'y': bounces[7][1],
            },
            {
              'x': bounces[8][0],
              'y': bounces[8][1],
            },
            {
              'x': bounces[9][0],
              'y': bounces[9][1],
            },
        ]
    }

    """
    {
        'id': 12,
        'position': -1,
        'shots': [
            50, 12, 33, 77
        ]
    }
    """
    # Sleep to simulate image processing
    time.sleep(2)

    # Print request to confirm post data
    # print(request.json)
 
    # Save in file
    """
    {
        'bounces': [
            {
              'x': 50,
              'y': 30,
            },
            {
              'x': -1,
              'y': -1,
            },...
        ]
    }
    """

    # print("\n")
    # print(response_bounces)
    return response_bounces
    
if __name__ == "__main__":
    app.run(host='0.0.0.0')
