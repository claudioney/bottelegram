#!/bin/sh
#ffmpeg -i rtsp://192.168.2.102:1981//Master-0 -frames:v 1 /home/pi/fontes/larabot/images/$(date +%H)/directPhoto_cam1-$(date +%H-%M-%S).jpg
echo  'ffmpeg -y -r 3 -pattern_type glob -i "/home/pi/camimage/HORA/directPhoto*.jpg" -vcodec libx264 /home/pi/camimage/timelapse_quase_HORA.mp4' \
 | sed s/HORA/$(date --date 'now - 1 hour' +%H)/g  \
 | sh

#ffmpeg -y -r 3 -pattern_type \    glob -i "/home/pi/camimage/$(date +%H)/directPhoto*.jpg" \    -vcodec libx264 /home/pi/camimage/timelapse_quase_$(date +%H).mp4'

mv /home/pi/camimage/timelapse_quase_$(date --date 'now - 1 hour' +%H).mp4 /home/pi/camimage/timelapse_$(date --date 'now - 1 hour' +%H).mp4

# removendo arquivos de 6 horas atras
rm /home/pi/camimage/$(date --date 'now - 6 hour' +%H)/directPhoto*.jpg
