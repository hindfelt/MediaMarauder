#! /usr/bin/env python3

import subprocess



#load urls from file into a list
with open('files', 'r') as file:
    urls = file.readlines()

for line in urls:
    line = line.strip()
    #line = "yt-dlp --write-subs --use-postprocessor FFmpegCopyStream --ppa CopyStream:'-c:v libx264 -c:a aac -f mp4' " + line
    line = "yt-dlp -f 'bv*[ext=mp4][vcodec^=avc1]+ba[ext=m4a]/b[ext=mp4]' -S 'codec:h264' " + line
    command = f"{line}"
    subprocess.run(command, shell=True, check=True)
   

print(urls)
