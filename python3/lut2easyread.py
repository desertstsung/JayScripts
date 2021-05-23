#!/usr/bin/python3


import sys
import numpy as np
from array import array
from copy import deepcopy


def readlut(fn):
  with open(fn, 'rb') as fo:
    n=np.frombuffer(fo.read(4), dtype=np.byte)
    lutsza=np.frombuffer(fo.read(4*n[0]), dtype=np.float32)
    lutvza=np.frombuffer(fo.read(4*n[1]), dtype=np.float32)
    lutraa=np.frombuffer(fo.read(4*n[2]), dtype=np.float32)
    lutaot=np.frombuffer(fo.read(4*n[3]), dtype=np.float32)
    
    tmp1=[0 for _ in lutraa]
    tmp2=[0 for _ in range(len(lutsza)*len(lutvza))]
    for i in range(len(tmp2)):
      tmp2[i]=[0, 0, 0, deepcopy(tmp1)]
    lutdata=[0 for _ in lutaot]
    for i in range(len(lutdata)):
      lutdata[i]=[0, deepcopy(tmp2)]
    for i in range(len(lutaot)):
      lutdata[i][0]=array('f', fo.read(4))[0]
      for j in range(len(lutsza)):
        for k in range(len(lutvza)):
          lutdata[i][1][len(lutvza)*j+k][0:3]=array('f', fo.read(12))
          for l in range(len(lutraa)):
            lutdata[i][1][len(lutvza)*j+k][3][l]=array('f', fo.read(4))[0]
    if fo.seek(0, 1)!=fo.seek(0, 2):
      fo.close()
      print('Invalid LUT')
  return lutdata, lutsza, lutvza, lutraa, lutaot


def wcsv(fn, lutdata, lutsza, lutvza, lutraa, lutaot):
  with open(fn, 'w') as fo:
    fo.write('aot,sza,vza,raa,s,t_scadown,t_scaup,t_gas,p\n')
    for i in range(len(lutaot)):
      for j in range(len(lutsza)):
        for k in range(len(lutvza)):
          for l in range(len(lutraa)):
            fo.write(str([lutaot[i], lutsza[j], lutvza[k], lutraa[l]])[1:-1]+',')
            fo.write(str([lutdata[i][0]]+list(lutdata[i][1][len(lutvza)*j+k][0:3])+[lutdata[i][1][len(lutvza)*j+k][3][l]])[1:-1]+'\n')


def main():
  lutdata, lutsza, lutvza, lutraa, lutaot=readlut(sys.argv[1])
  wcsv(sys.argv[1]+'_easyread.csv', lutdata, lutsza, lutvza, lutraa, lutaot)


if __name__=='__main__':
  main()
