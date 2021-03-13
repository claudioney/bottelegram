ffmpeg -i rtsp://192.168.2.'+ipSet+':1981//Master-0 -t 30 -codec copy '+str(chat_id)+'/capture.mkv
