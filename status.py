import os
import sys
import time
import random
import datetime
import telepot
import subprocess as sp
from telepot.loop import MessageLoop
import RPi.GPIO as GPIO
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton
import config as cfg

def tocaAlarme():
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(18,GPIO.OUT)
        print "LED on"
        GPIO.output(18,GPIO.HIGH)
        time.sleep(60)
        print "LED off"
        GPIO.output(18,GPIO.LOW)
	return;

def validaTempo(chat_id,hora):
	enviaFoto(chat_id)
	enviaVideo(chat_id)
	return;

def mudaIp(chat_id,msg):
        global ipSet
	ipSet = msg['text'][8:]
	print 'ip mudado para '+ipSet
	bot.sendMessage(chat_id,'Agora estou de '+ipSet)
	return;

def listaIps(chat_id):
	bot.sendMessage(chat_id,'Deixa eu ver...')
	list = sp.check_output('nmap -sP 10.0.0.1-255 | grep 10.0.0 |  awk \'{ print $5 }\' | sed -e \'s/10.0.0./IP /g\'',shell=True)
        opt = list.split('\n')
        bot.sendMessage(chat_id,'tem esse pessoal:',reply_markup=ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="/menu")],opt]))
	return;

def listaIpsMenu(chat_id):
	list = sp.check_output('nmap -sP 10.0.0.1-255 | grep 10.0.0',shell=True)
	bot.sendMessage(chat_id,'Tem esse pessoal aqui',list.split('\n'))
	return;

def limpaIp(chat_id,msg):
        sp.check_call('echo "" > /home/pi/camimage/camp_ip.ini', shell=True)
	bot.sendMessage(chat_id,'Estou limpinha')
	return;

def botaIp(chat_id,msg):
        global ipSet
        ipSet = msg['text'][8:]
        print 'ip no arquivo '+ipSet
	sp.check_call('echo "'+ipSet+'\n" >> /home/pi/camimage/camp_ip.ini', shell=True)
	return;

def enviaTimelapse(chat_id):
        bot.sendMessage(chat_id,'estou indo fazer a paradinha...')
        sp.check_call('ffmpeg -y -r 3 -pattern_type glob -i "/home/pi/camimage/screenshot*.jpg" -vcodec libx264 /home/pi/camimage/timelapse.mp4 && rm /home/pi/camimage/screenshot*.jpg', shell=True)
        bot.sendMessage(chat_id,'estou mandando a paradinha')
        bot.sendVideo(chat_id, open('/home/pi/camimage/timelapse.mp4', 'rb'))
        time.sleep(0.5)
        return;

def enviaFoto(chat_id):
	imagem = os.getcwd()+'/'+str(chat_id)+'/screenshot.jpg';
	if os.path.exists(imagem):
		os.remove(imagem)
	bot.sendMessage(chat_id,'estou indo tirar a foto')
        sp.check_call('ffmpeg -i rtsp://10.0.0.'+ipSet+':554//Master-0 -frames:v 1 '+str(chat_id)+'/screenshot.jpg', shell=True)
        bot.sendMessage(chat_id,'estou mandando a foto')
        bot.sendPhoto(chat_id,('screenshot.jpg',open(str(chat_id)+'/screenshot.jpg', 'rb')),caption='pronto! ta ae a foto!')
        time.sleep(0.5)
	return;

def enviaVideo(chat_id):
        global ipSet
	imagem = os.getcwd()+'/'+str(chat_id)+'/capture.mkv';
	if os.path.exists(imagem):
		os.remove(imagem)
	bot.sendMessage(chat_id,'fazendo um video de 30 segundos')
	sp.check_call('ffmpeg -i rtsp://10.0.0.'+ipSet+':554//Master-0 -t 30 -codec copy '+str(chat_id)+'/capture.mkv', shell=True)
	bot.sendMessage(chat_id,'mandando o video')
	bot.sendVideo(chat_id, open(str(chat_id)+'/capture.mkv', 'rb'))
	time.sleep(0.5)
	return;

def menu(chat_id):
	time.sleep(0.5)
	return;

def handle(msg):
        global ipSet
	chat_id = msg['chat']['id']
	command = msg['text']

	print 'Texto digitado: %s' % command

	if str(chat_id) != str(cfg.chatCfg['idChat']):
		bot.sendMessage(chat_id,'ops, vc nao pode acessar esse chatbot! sorry!')
	elif command.startswith("Quero 69"):
        	ipSet = msg['text'][8:]
        	print 'ip mudado para '+ipSet
        	bot.sendMessage(chat_id,'Agora estou de '+ipSet)
	elif command == '/start':
		bot.sendMessage(chat_id,'Bem vindo!')
		sp.check_call('mkdir '+str(chat_id), shell=True)
	elif command.startswith("Ta so"):
		listaIps(chat_id)
	elif command =='Manda nude':
		enviaFoto(chat_id)
	elif command == 'Corta pra 18':
		enviaVideo(chat_id)
        elif command == 'Paradinha':
                enviaTimelapse(chat_id)
	elif command.startswith("IP "):
                ipSet = msg['text'][3:]
                print 'ip mudado para '+ipSet
                bot.sendMessage(chat_id,'IP='+ipSet)
	elif command == '/menu':
		bot.sendMessage(chat_id,'Selecione',reply_markup=ReplyKeyboardMarkup(
                                keyboard=[
                                    [KeyboardButton(text="Manda nude")],
				    [KeyboardButton(text="Corta pra 18")],
				    [KeyboardButton(text='Ta sozinha?')],
				    [KeyboardButton(text='Paradinha')]
                                ]
                            ))
	elif command == 'Toca o terror':
		bot.sendMessage(chat_id,'Tocando o alarme por 60 segundos')
		tocaAlarme()
	elif command == 'Bomb':
                bot.sendMessage(chat_id,'Bomb has been planted')
	elif command == 'Defuse':
                bot.sendMessage(chat_id,'Bomb has been defused')


bot = telepot.Bot(cfg.botTelepot['id'])

MessageLoop(bot, handle).run_as_thread()
print 'Estou ouvindo ...'
horas = '99'
ipSet = '51'

enviaFoto(cfg.chatCfg['idChat'])

while 1:
    time.sleep(10)
