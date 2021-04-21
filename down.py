#!/usr/bin/env python3


url="https://public.spider.surfsara.nl/project/spexone/Public2/PACE/20210412"
downdir="./downdir"


import requests
import re
import os


def handledir(url, currentlocaldir):
  for suburl in re.findall(r"(?<=href=\").+?(?=\")|(?<=href=\').+?(?=\')", requests.get(url).text)[1:]:
    abssuburl=os.path.join(url, suburl)
    localpath=os.path.join(currentlocaldir, suburl)
    if suburl.endswith("/"): #directory
      os.mkdir(localpath)
      handledir(abssuburl, localpath)
    else: #file
      print("Downloading to: ", localpath)
      with open(localpath, "wb") as fo:
        fo.write(requests.get(abssuburl).content)


handledir(url, downdir)
