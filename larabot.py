import os
import sys
import time
import random
import datetime
import telepot
import asyncio
#import websockets
import subprocess as sp
from telepot.loop import MessageLoop
from datetime import timedelta 
import RPi.GPIO as GPIO
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton
#from io import gpio_number
from threading import Thread
import config as cfg
import csv


GPIO_DOOR = 22
GPIO_MOTION = 24
GPIO_MOTION2 = 23
sirene = 25
ipcam1 = 1
ipcam2 = 1

portaFechada = 1
WARNING = 1
ALARM = 0
WARN_GPIO = 1
WARN_GPIO2 = 1

async def hello(websocket, path):
    name = await websocket.recv()

    greeting = f"{name}!"
    bot.sendMessage(cfg.chatCfg['idChat'],greeting)

    await websocket.send(greeting)
    print(f"> {greeting}")

def checkStatus():
    global GPIO_DOOR
    bot.sendMessage(cfg.chatCfg['idChat'],'VERIFICACAO DE STATUS DA PORTA')
    verPorta()
    return

def alarmeRelay():
    return

def tocaAlarme():
    global sirene
    GPIO.setup(sirene,GPIO.OUT)
    print ("SIRENE on")
    GPIO.output(sirene,GPIO.HIGH)
    time.sleep(60)
    print ("SIRENE off")
    GPIO.output(sirene,GPIO.LOW)
    return

def leConfigCamera():
    global ipcam1, ipcam2
    print ('Lendo as configuraçoes da ip camera')
    linhas = csv.reader(open('ipcam.csv'))
    for row in linhas: 
        if row[0] == 'varanda': ipcam1 = row[1]
        if row[0] == 'sala': ipcam2 =  row[1]
    return

def gravaConfigCamera():
    le = csv.writer(open('ipcam.csv', 'w'))
    le.writerow(["varanda",ipcam1])
    le.writerow(["sala",ipcam2])
    return

def espacoDisco(chat_id):
    s = os.statvfs("/")
    diskSpacePercent =  round((((s.f_blocks - s.f_bfree) * s.f_frsize)/(s.f_blocks * s.f_bsize)) * 100, 2)
    bot.sendMessage(chat_id,'Espaço em disco:'+str(diskSpacePercent))
    return

def listaIps(chat_id):
    bot.sendMessage(chat_id,'Deixa eu ver...')
    list = sp.check_output('nmap -sP 192.168.2.1-255 | grep 192.168.2 |  awk \'{ print $5 }\' | sed -e \'s/192.168.2./IP /g\'',shell=True)
    opt = list.decode('utf-8').split('\n')
    bot.sendMessage(chat_id,'tem esse pessoal:',reply_markup=ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="/menu")],opt]))
    return;

def listaIpsMenu(chat_id):
    list = sp.check_output('nmap -sP 192.168.2.1-255 | grep 192.168.2',shell=True)
    bot.sendMessage(chat_id,'Tem esse pessoal aqui',list.decode('utf-8').split('\n'))
    return

def botaIp(chat_id,msg):
    global ipSet
    ipSet = msg['text'][8:]
    print ('ip no arquivo '+ipSet)
    sp.check_call('echo "'+ipSet+'\n" >> /home/pi/camimage/camp_ip.ini', shell=True)
    return

def enviaTimelapse(chat_id):
    bot.sendMessage(chat_id,'estou indo fazer a paradinha...')
    sp.check_call('ffmpeg -y -r 3 -pattern_type glob -i "/home/pi/telepot/laraBot/images/directPhoto*.jpg" -vcodec libx264 /home/pi/camimage/timelapse.mp4 && rm /home/pi/telepot/laraBot/images/directPhoto*.jpg', shell=True)
    bot.sendMessage(chat_id,'enviando..')
    bot.sendVideo(chat_id, open('/home/pi/camimage/timelapse.mp4', 'rb'))
    time.sleep(0.5)
    return

def enviaArquivo(chat_id, arquivo):
    bot.sendMessage(chat_id,'enviando arquivo...')
    bot.sendVideo(chat_id, open('/home/pi/camimage/'+arquivo, 'rb'))
    time.sleep(0.5)
    return


def enviaVideoMin(chat_id, ipcam):
    imagem = os.getcwd()+'/'+str(chat_id)+'/videoMin'+ipcam+'.mkv'
    print ('gerando arquivo '+imagem)
    if os.path.exists(imagem):
        os.remove(imagem)
    try:
       sp.check_call('ffmpeg -i rtsp://192.168.2.'+ipcam+':1981//Master-0 -t 600 -codec copy ' + imagem, shell=True)
       bot.sendVideo(chat_id, open(imagem, 'rb'))
    except:
      bot.sendMessage(chat_id,'falha ao mandar video min' + imagem)
    time.sleep(5)
    return


def enviaTimelapseHour(hora, chat_id):
    print ('Validando timelapse')
    localfile = '/home/pi/camimage/timelapse_'+str(hora)+'.mp4'
    if hora <10:
      localfile = '/home/pi/camimage/timelapse_0'+str(hora)+'.mp4'
    if os.path.exists(localfile):
      print("enviado timelapse: "+ localfile)
      try:
        bot.sendVideo(chat_id, open(localfile, 'rb'))
      except:
        bot.sendMessage(chat_id,'falha ao mandar timelapse')

    time.sleep(0.5)

def enviaFotoDirect(chat_id):
    global ipcam1, ipcam2, ipSet
    ipSet = ipcam1
    directFoto(chat_id)
    ipSet = ipcam2
    directFoto(chat_id)

def enviaVideoDirect(chat_id):
    global ipcam1, ipcam2, ipSet
    ipSet = ipcam1
    directVideo(chat_id)
    ipSet = ipcam2
    directVideo(chat_id)

def directFoto(chat_id):
    imagem = os.getcwd()+'/'+str(chat_id)+'/directPhoto.jpg';
    if os.path.exists(imagem):
        os.remove(imagem)
    try:
      sp.check_call('ffmpeg -i rtsp://192.168.2.'+ipSet+':1981//Master-0 -frames:v 1 '+str(chat_id)+'/directPhoto.jpg', shell=True)
      bot.sendPhoto(chat_id,('directPhoto.jpg',open(str(chat_id)+'/directPhoto.jpg', 'rb')),caption='Direct foto')
    except:
      bot.sendMessage(chat_id,'falha ao mandar a foto direta')
    time.sleep(0.5)
    return

def systemReboot(chat_id):
    bot.sendMessage(chat_id,'sinto q vou desmaiar...')
    os.system('systemctl reboot -i')
    return

def directVideo(chat_id):
    imagem = os.getcwd()+'/'+str(chat_id)+'/directVideo.mkv'
    if os.path.exists(imagem):
        os.remove(imagem)
    try:
       sp.check_call('ffmpeg -i rtsp://192.168.2.'+ipSet+':1981//Master-0 -t 30 -codec copy '+str(chat_id)+'/directVideo.mkv', shell=True)
       bot.sendVideo(chat_id, open(str(chat_id)+'/directVideo.mkv', 'rb'))
    except:
      bot.sendMessage(chat_id,'falha ao mandar a video direta')
    time.sleep(0.5)
    return

def enviaFoto(chat_id):
    imagem = os.getcwd()+'/'+str(chat_id)+'/screenshot.jpg'
    if os.path.exists(imagem):
        os.remove(imagem)
    bot.sendMessage(chat_id,'estou indo tirar a foto')
    try:
      sp.check_call('ffmpeg -i rtsp://192.168.2.'+ipSet+':1981//Master-0 -frames:v 1 '+str(chat_id)+'/screenshot.jpg', shell=True)
      bot.sendMessage(chat_id,'estou mandando a foto')
      bot.sendPhoto(chat_id,('screenshot.jpg',open(str(chat_id)+'/screenshot.jpg', 'rb')),caption='pronto! ta ae a foto!')
    except:
      bot.sendMessage(chat_id,'o trouxa chegou, nao posso mandar')
    time.sleep(0.5)
    return

def enviaVideo(chat_id):
    global ipSet, ipcam1, ipcam2
    imagem = os.getcwd()+'/'+str(chat_id)+'/capture.mkv'
    if os.path.exists(imagem):
        os.remove(imagem)
    bot.sendMessage(chat_id,'fazendo um video de 30 segundos')
    try:
       sp.check_call('ffmpeg -i rtsp://192.168.2.'+ipSet+':1981//Master-0 -t 30 -codec copy '+str(chat_id)+'/capture.mkv', shell=True)
       bot.sendMessage(chat_id,'mandando o video')
       bot.sendVideo(chat_id, open(str(chat_id)+'/capture.mkv', 'rb'))
    except:
       bot.sendMessage(chat_id,'o trouxa chegou, nao posso mandar')
    time.sleep(0.5)
    return

def menu(chat_id):
    time.sleep(0.5)
    return

def sensorPresenca(GPIO_MOTION):
    global WARNING, ALARM, WARN_GPIO, WARN_GPIO2

    if GPIO_MOTION == 23 and WARN_GPIO == 0:
        return
    if GPIO_MOTION == 24 and WARN_GPIO2 == 0:
        return

    if WARNING == 1:
        print("Motion Detected! ->"+str(GPIO_MOTION))
        bot.sendMessage(cfg.chatCfg['idChat'],'SENSOR DE PRESENÇA ON: '+str(GPIO_MOTION))

    if ALARM ==1:
        alarmeRelay()
    time.sleep(0.5)


def sensorPorta(GPIO_DOOR):
    if GPIO.input(GPIO_DOOR) == 1:
        sensorPortaAberta()
    if GPIO.input(GPIO_DOOR) == 0:
        sensorPortaFechada()
    return

def verPorta():
    global GPIO_DOOR
    # como o pud_up esta como up, se tiver fio separado, é 1
    if GPIO.input(GPIO_DOOR) == 1:
        bot.sendMessage(cfg.chatCfg['idChat'],'STATUS DE PORTA ABERTA')
    if GPIO.input(GPIO_DOOR) ==0:
        bot.sendMessage(cfg.chatCfg['idChat'],'STATUS DE PORTA FECHADA')

    return

def sensorPortaAberta():
    global WARNING, ALARM,portaFechada
    if (WARNING == 1 and portaFechada ==1):
        portaFechada = 0
        print('Porta aberta')
        bot.sendMessage(cfg.chatCfg['idChat'],'MOVIMENTO DE PORTA ABERTA!')
#        enviaFotoDirect(cfg.chatCfg['idChat'])
#        enviaVideoDirect(cfg.chatCfg['idChat'])

        if ALARM ==1:
            alarmeRelay()

    time.sleep(0.5)

def sensorPortaFechada():
    global WARNING, ALARM, portaFechada
    if (WARNING == 1 and portaFechada == 0):
        portaFechada = 1
        print('Porta fechada')
        bot.sendMessage(cfg.chatCfg['idChat'],'MOVIMENTO DE PORTA FECHADA!')
#         enviaFotoDirect(cfg.chatCfg['idChat'])
#         enviaVideoDirect(cfg.chatCfg['idChat'])
        if ALARM ==1:
            alarmeRelay()

    time.sleep(0.5)

def handle(msg):
    global ipSet, ipcam1, ipcam2, WARNING, WARN_GPIO, WARN_GPIO2
    chat_id = msg['chat']['id']
    command = msg['text']

    print ('Texto digitado: %s' % command)

    if str(chat_id) != str(cfg.chatCfg['idChat']):
        bot.sendMessage(chat_id,'ops, vc nao pode acessar esse chatbot! sorry!')
    elif command == '/start':
        bot.sendMessage(chat_id,'Bem vindo!')
        sp.check_call('mkdir '+str(chat_id), shell=True)
    elif command.startswith("Ta so"):
        listaIps(chat_id)
    elif command =='Manda nude':
        enviaFoto(chat_id)
    elif command == 'Corta pra 18':
        enviaVideo(chat_id)
    elif command.startswith("Toma="):
        arq = msg['text'][5:]
        enviaArquivo(chat_id, arq)
    elif command == 'Paradinha':
        enviaTimelapse(chat_id)
    elif command.startswith("Cam1="):
        ipcam1 = msg['text'][5:]
        gravaConfigCamera()
        print ('ipcam1 mudado para '+ipcam1)
        bot.sendMessage(chat_id,'IPcam1='+ipcam1)
    elif command.startswith("Cam2="):
        ipcam2 = msg['text'][5:]
        gravaConfigCamera()
        print ('ipcam2 mudado para '+ipcam2)
        bot.sendMessage(chat_id,'IPcam2='+ipcam2)
    elif command.startswith("IP "):
        ipSet = msg['text'][3:]
        print ('ip mudado para '+ipSet)
        bot.sendMessage(chat_id,'IP='+ipSet)
    elif command == '/menu':
        bot.sendMessage(chat_id,'Selecione',reply_markup=ReplyKeyboardMarkup(
                                keyboard=[
                                    [KeyboardButton(text="Manda nude")],
                                    [KeyboardButton(text="Corta pra 18")],
                                    [KeyboardButton(text='Ta sozinha?')],
                                    ['WON', 'WOFF', 'Disco', 'PORTA']
                                ]
                            ))
    elif command == 'Toca o terror':
        bot.sendMessage(chat_id,'Tocando o alarme por 60 segundos')
        tocaAlarme()
    elif command == 'Disco':
        espacoDisco(chat_id)
    elif command == 'Reboot':
        systemReboot(chat_id)
    elif command == 'WON':
        bot.sendMessage(chat_id,'WARNING ON')
        WARNING = 1
    elif command == 'WOFF':
        bot.sendMessage(chat_id,'WARNING OFF')
        WARNING = 0
    elif command == 'GPION':
        WARN_GPIO = 1
        bot.sendMessage(chat_id, 'GPIO ON')
    elif command == 'GPIOFF':
        WARN_GPIO = 0
        bot.sendMessage(chat_id, 'GPIO OFF')
    elif command == 'GPION2':
        WARN_GPIO2 = 1
        bot.sendMessage(chat_id, 'GPIO 2 ON')
    elif command == 'GPIOFF2':
        WARN_GPIO2 = 0
        bot.sendMessage(chat_id, 'GPIO 2 OFF')
    elif command == 'PORTA':
        verPorta()



bot = telepot.Bot(cfg.botTelepot['id'])

MessageLoop(bot, handle).run_as_thread()

print ('Iniciando o sistema')
try:
    bot.sendMessage(cfg.chatCfg['idChat'],'SISTEMA INICIADO.')
    achou_time = 0
    minuto = 30
    horas  = 99
    ipSet  = '0'
    portaFechada = 1

    leConfigCamera()

    Thread(target = enviaVideoMin, args = (cfg.chatCfg['idChat'], ipcam1,)).start()
    Thread(target = enviaVideoMin, args = (cfg.chatCfg['idChat'], ipcam2,)).start()
    #enviaFotoDirect(cfg.chatCfg['idChat'])

    #ativando gpio
    GPIO.setmode(GPIO.BCM)
    #selecionando sirene out
    GPIO.setwarnings(False)
    #sensor de porta
    #GPIO.setup(GPIO_DOOR, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    #sensor de presenca
    #GPIO.setup(GPIO_MOTION, GPIO.IN)
    #GPIO.setup(GPIO_MOTION2, GPIO.IN)

    print ('Validando o checkstatus')
    #vericar status  do GPIO
    #checkStatus()

    print ('Iniciando GPIO')
#    GPIO.add_event_detect(GPIO_DOOR, GPIO.BOTH, callback = sensorPorta)
#    GPIO.add_event_detect(GPIO_MOTION,  GPIO.RISING, callback= sensorPresenca, bouncetime=200)
#    GPIO.add_event_detect(GPIO_MOTION2, GPIO.RISING, callback= sensorPresenca, bouncetime=200)


#    start_server = websockets.serve(hello, "localhost", 8119)

#    asyncio.get_event_loop().run_until_complete(start_server)
#    asyncio.get_event_loop().run_forever()


    print ('iniciando o loop')
    while True:
         now = datetime.datetime.now()
         if horas != now.hour:
              print('Hora fechada')
              horas  = now.hour
              achou_time = 0
#              enviaFotoDirect(cfg.chatCfg['idChat'])
#              enviaVideoDirect(cfg.chatCfg['idChat'])
         if (now.minute > minuto) and achou_time == 0:
              print("enviado timelapse")
              achou_time = 1
              h = now - timedelta(hours=1)
              enviaTimelapseHour(h.hour,cfg.chatCfg['idChat'])
         time.sleep(60)

except:
    print("Erro no sistema!:", sys.exc_info()[0])
    GPIO.cleanup()
