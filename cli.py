#!/usr/bin/env python3
import sys
import time
import json
def writeNew(tag):
    context = open("./templates/md.tpl").read()
    t = time.strftime("%Y.%m.%d %H:%M", time.localtime(int(time.time())))
    tag = json.dumps(tag.split(","), ensure_ascii=False)
    context = context%(t,tag)
    print(context)

tag = sys.argv[1]
writeNew(tag)