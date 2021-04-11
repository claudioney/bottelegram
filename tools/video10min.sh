#!/bin/sh

i="0"
while [ $i -lt 6 ]
do
rm /home/pi/camimage/$(date --date 'now - 6 hour' +%H)/directVideo*.mkv
cd /home/pi/fontes/larabot
cat ipcam.csv \
 | sed -e 's/\r$//g' \
 | awk -F, '{print "ffmpeg -y -i rtsp://192.168.2."$2":1981//Master-0  -t 600 -codec copy /home/pi/camimage/HORA/directVideo_"$2"-TEMPO.mkv"}' \
 | sed s/HORA/$(date +%H)/g \
 | sed s/TEMPO/$(date +%H-%M)/g \
 | sh
done

# removendo arquivos de 6 horas atras
#rm /home/pi/camimage/$(date --date 'now - 6 hour' +%H)/directPhoto*.jpg

#ffmpeg -i rtsp://192.168.2.'+ipSet+':1981//Master-0 -t 30 -codec copy '+str(chat_id)+'/capture.mkv

#ffmpeg -i rtsp://192.168.2.'+ipSet+':1981//Master-0 -t 30 -codec copy '+str(chat_id)+'/capture.mkv
