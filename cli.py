#!/usr/bin/env python3
import sys
import time

def writeNew(tag):
    context = open("./templates/md.tpl").read()
    t = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(time.time())))
    tag = tag.split(",")
    context = context%(t,tag)
    print(context)

tag = sys.argv[1]
writeNew(tag)