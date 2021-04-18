#!/usr/bin/python3

#import getopt
from warnings import filterwarnings
filterwarnings('ignore')

import sys
import numpy as np
from array import array
from copy import deepcopy
from h5py import File as openh5


#Read PSAC TOA at 670 nm
#And assume SR at 670 nm equal quarter of TOA at 2250 nm
#And TOA at 443 nm and 1380 nm to mask cloud
#And angle data
def readpsac(fn):
  with openh5(fn) as fo:
    toa=fo['Data_Fields/I'][3,:,:]
    sr=fo['Data_Fields/I'][8,:,:]/2
    bl=fo['Data_Fields/I'][1,:,:]
    ir=fo['Data_Fields/I'][6,:,:]
    sza=fo['Geolocation_Fields/Sol_Zen_Ang'][:,:]
    vza=fo['Geolocation_Fields/View_Zen_Ang'][:,:]
    lat=fo['Geolocation_Fields/Latitude'][:,:]
    lon=fo['Geolocation_Fields/Longitude'][:,:]
    raa=abs(fo['Geolocation_Fields/View_Azim_Ang'][:,:]-fo['Geolocation_Fields/Sol_Azim_Ang'][:,:])
    raa=(raa>180)*(360-raa)+(raa<=180)*raa
  return toa, sr, bl, ir, sza, vza, raa, lon, lat


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
      lutdata[i][0]=array('f', fo.read(4))[0] #pherical albedo
      for j in range(len(lutsza)):
        for k in range(len(lutvza)):
          lutdata[i][1][len(lutvza)*j+k][0:3]=array('f', fo.read(12)) #tdn, tup, t
          for l in range(len(lutraa)):
            lutdata[i][1][len(lutvza)*j+k][3][l]=array('f', fo.read(4))[0] #path ref
    if fo.seek(0, 1)!=fo.seek(0, 2):
      fo.close()
      print('Invalid LUT')
  return lutdata, lutsza, lutvza, lutraa, lutaot


#Interpolation between x1 and x2
#Returns scalar if x is scalar
def interpalg(x1, x, x2, y1, y2):
  try: feq=(y1==y2).all()
  except AttributeError: feq=y1==y2
  return y1 if feq else y1+(y2-y1)*(x-x1)/(x2-x1)


def calproper(isza, ivza, iraa, lutsza, lutvza, lutraa, lutdata, lenaot):
  lutsza=np.array(lutsza)
  lutvza=np.array(lutvza)
  lutraa=np.array(lutraa)
  
  sindex=((lutsza-isza)>0).argmax()
  vindex=((lutvza-ivza)>0).argmax()
  rindex=((lutraa-iraa)>0).argmax()
  sindex=[sindex-1, sindex]
  vindex=[vindex-1, vindex]
  rindex=[rindex-1, rindex]
  
  r=np.ndarray(shape=(8, 5*lenaot))
  loop=range(lenaot)
  lenvza=len(lutvza)
  for i in range(2): #sza index
    for j in range(2): #vza index
      for k in range(2): #raa index
        r[4*i+2*j+k, :lenaot]=[lutdata[_][0] for _ in loop] #s
        r[4*i+2*j+k, lenaot:2*lenaot]=[lutdata[_][1][lenvza*sindex[i]+vindex[j]][0] for _ in loop] #tdn
        r[4*i+2*j+k, 2*lenaot:3*lenaot]=[lutdata[_][1][lenvza*sindex[i]+vindex[j]][1] for _ in loop] #tup
        r[4*i+2*j+k, 3*lenaot:4*lenaot]=[lutdata[_][1][lenvza*sindex[i]+vindex[j]][2] for _ in loop] #t
        r[4*i+2*j+k, 4*lenaot:]=[lutdata[_][1][lenvza*sindex[i]+vindex[j]][3][rindex[k]] for _ in loop] #path ref

  for i in range(4):
    r[i, :]=interpalg(lutsza[sindex[0]], isza, lutsza[sindex[1]], r[i, :], r[i+4, :])
  for i in range(2):
    r[i, :]=interpalg(lutvza[vindex[0]], ivza, lutvza[vindex[1]], r[i, :], r[i+2, :])
  return interpalg(lutraa[rindex[0]], iraa, lutraa[rindex[1]], r[0, :], r[1, :])
  

def iscloudy(bluearray, irarray, ns, nl, blue_th1=0.0025, blue_th2=0.4, ir_th1=0.003, ir_th2=0.025):
  bluesub=bluearray[nl-1:nl+2, ns-1:ns+2]
  bluestd=bluesub.std()
  bluestenew=bluesub.mean()*bluestd*3
  bluelikeclear1=(bluestenew<blue_th1)+((bluestenew>=blue_th1) and (bluestd<3*blue_th1) and (bluesub.all()>0))
  bluelikeclear2=bluearray[nl,ns]<=blue_th2
  
  irsub=irarray[nl-1:nl+2, ns-1:ns+2]
  irlikeclear1=(irsub.std()<ir_th1) and irsub.all()>-0.1
  irlikeclear2=irarray[nl,ns]<=ir_th2
  
  return not (bluelikeclear1 and bluelikeclear2 and irlikeclear1 and irlikeclear2)
  

#rt -> [s1, s2, ..., tdn1, tdn2, ..., ..., p1, p2, ..., pn]
def inversion(csr, rt, ctoa, lutaot):
  stoa=[]
  lenaot=len(lutaot)
  for i in range(lenaot):
    #s=rt[i], tdn=rt[i+lenaot], tup=rt[i+2*lenaot], t=rt[i+3*lenaot], pr=rt[i+4*lenaot]
    tmp=(rt[i+4*lenaot]+(rt[i+lenaot]*rt[i+2*lenaot]*csr)/(1-rt[i]*csr))*rt[i+3*lenaot]
    stoa.append(tmp)
  
  for i in range(lenaot-1):
    if stoa[i]<ctoa<stoa[i+1]: return interpalg(stoa[i], ctoa, stoa[i+1], lutaot[i], lutaot[i+1])
  return float('nan')


def writetoh5(fn, aot, lon, lat):
  with openh5(fn, 'w') as fo:
    fo.create_dataset('AOT550', data=aot, compression=9, dtype='f')
    fo.create_dataset('Latitude', data=lat, compression=9, dtype='f')
    fo.create_dataset('Longitude', data=lon, compression=9, dtype='f')


def main(psacfn, lutfn, aotfn):
  toa, sr, bl, ir, sza, vza, raa, lon, lat=readpsac(psacfn)
  lutdata, lutsza, lutvza, lutraa, lutaot=readlut(lutfn)
  
  outofrange=0
  well=0
  
  aotinv=sr.copy()
  lenaot=len(lutaot)
  for nl in range(sr.shape[0]):
    for ns in range(sr.shape[1]):
      aotinv[nl, ns]=inversion(sr[nl, ns], calproper(sza[nl, ns], vza[nl, ns], raa[nl, ns],
        lutsza, lutvza, lutraa, lutdata, lenaot), toa[nl, ns], lutaot)
      if 0<aotinv[nl, ns]<6: well+=1
      else: outofrange+=1
  
  writetoh5(aotfn, aotinv, lon, lat)
  print('n of outrange: ', outofrange)
  print('n of success : ', well)


if __name__=='__main__':
  psacfn='HJ2A_PSAC_E116.9_N35.8_20201106_L10000015715.hdf5'
  lutfn='LUT_670'
  outfn='AOT550.hdf5'
  main(psacfn, lutfn, outfn)
