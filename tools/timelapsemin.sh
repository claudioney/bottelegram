#!/bin/sh
cd /home/pi/fontes/larabot
cat ipcam.csv \
 | sed -e 's/\r$//g' \
 | awk -F, '{print "ffmpeg -y -i rtsp://192.168.2."$2":1981//Master-0 -frames:v 1 /home/pi/camimage/HORA/directPhoto_"$2"-TEMPO.jpg"}' \
 | sed s/HORA/$(date +%H)/g \
 | sed s/TEMPO/$(date +%H-%M)/g \
 | sh

#ffmpeg -i rtsp://192.168.2.102:1981//Master-0 -frames:v 1 /home/pi/telepot/laraBot/images/$(date +%H)/directPhoto_cam1-$(date +%H-%M-%S).jpg
#ffmpeg -i rtsp://192.168.2.103:1981//Master-0 -frames:v 1 /home/pi/telepot/laraBot/images/$(date +%H)/directPhoto_cam2-$(date +%H-%M-%S).jpg


