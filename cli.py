import sys
import time

def writeNew(title,tag}:
    context = open("./templates/md.tpl").read()
    t = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(time.time())))
    context.format(title,tag,t)

title = sys.argv[1]
tag = sys.argv[2]

writeNew(title,tag,timeStr)