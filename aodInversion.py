#!/usr/bin/python3

#import getopt
import warnings
warnings.filterwarnings('ignore')

import sys
import numpy as np
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
    
    lutdata={_:0 for _ in lutsza}
    lutdata={_:lutdata.copy() for _ in lutvza}
    lutdata={_:lutdata.copy() for _ in lutraa}
    
    for i in lutsza:
      for j in lutvza:
        for k in lutraa:
          lutdata[k][j][i]=[]
          for _ in range(n[3]):
            lutdata[k][j][i].append(np.frombuffer(fo.read(24), dtype=np.float32))
    if fo.seek(0, 1)!=fo.seek(0, 2):
      fo.close()
      print('Invalid LUT')
      sys.exit(2)
  return lutdata, lutsza, lutvza, lutraa


#Interpolation between x1 and x2
#Returns scalar if x is scalar
def interpalg(x1, y1, x2, y2, x):
  try: feq=y1.all()==y2.all()
  except AttributeError: feq=y1==y2
  return y1 if feq else (x1*y2-x2*y1-x*(y2-y1))/(x1-x2)


def interp(lutdata, lutsza, lutvza, lutraa, csza, cvza, craa):
  for i in range(len(lutsza)):
    if lutsza[i]-csza<0: sidx1, sidx2=lutsza[i], lutsza[i+1]
  for j in range(len(lutvza)):
    if lutvza[j]-cvza<0: vidx1, vidx2=lutvza[j], lutvza[j+1]
  for k in range(len(lutraa)):
    if lutraa[k]-craa<0: ridx1, ridx2=lutraa[k], lutraa[k+1]
  
  r={_:0 for _ in [sidx1, sidx2]}
  r={_:r.copy() for _ in [vidx1, vidx2]}
  r={_:r.copy() for _ in [ridx1, ridx2]}
  for i in [sidx1, sidx2]:
    for j in [vidx1, vidx2]:
      for k in [ridx1, ridx2]:
        r[k][j][i]=lutdata[k][j][i]
  
  for x in [vidx1, vidx2]:
    for y in [ridx1, ridx2]:
      for z in range(len(r[k][j][i])):
        data1=r[y][x][sidx1][z]
        data2=r[y][x][sidx2][z]
        r[y][x][sidx1][z]=interpalg(sidx1, data1, sidx2, data2, csza)
  
  for y in [ridx1, ridx2]:
    for z in range(len(r[k][j][i])):
      data1=r[y][vidx1][sidx1][z]
      data2=r[y][vidx2][sidx1][z]
      r[y][vidx1][sidx1][z]=interpalg(vidx1, data1, vidx2, data2, cvza)
  
  for z in range(len(r[k][j][i])):
    data1=r[ridx1][vidx1][sidx1][z]
    data2=r[ridx2][vidx1][sidx1][z]
    r[ridx1][vidx1][sidx1][z]=interpalg(ridx1, data1, ridx2, data2, craa)
    
  rt=r[ridx1][vidx1][sidx1]
  del r
  return rt
  

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
  

#rt -> list: [array(p, s, t1, t2, t, aot550), array, ... array]
def inversion(csr, rt, ctoa):
  stoa=[]
  for i in range(len(rt)):
    tmp=(rt[i][0]+(rt[i][2]*rt[i][3]*csr)/(1-rt[i][1]*csr))*rt[i][4]
    if tmp==ctoa: return rt[i][3]
    else: stoa.append(tmp)
  
  for i in range(len(rt)-1):
    if stoa[i]<ctoa<stoa[i+1]: return interpalg(stoa[i], rt[i][3], stoa[i+1], rt[i+1][3], ctoa)
  return float('nan')


def writetoh5(fn, aot, lon, lat):
  with openh5(fn, 'w') as fo:
    fo.create_dataset('AOT550', data=aot, compression=9, dtype='f')
    fo.create_dataset('Latitude', data=lat, compression=9, dtype='f')
    fo.create_dataset('Longitude', data=lon, compression=9, dtype='f')


def main(psacfn, lutfn, aotfn):
  toa, sr, bl, ir, sza, vza, raa, lon, lat=readpsac(psacfn)
  lutdata, lutsza, lutvza, lutraa=readlut(lutfn)
  
  ncloud=0
  noutofrange=0
  nwell=0
  
  aotinv=sr.copy()
  for nl in range(sr.shape[0]):
    for ns in range(sr.shape[1]):
      if nl in [0, sr.shape[0]-1] or ns in [0, sr.shape[1]-1]: #edge pixel
        if bl[nl, ns]>0.4 and ir[nl, ns]>0.025:
          ncloud+=1
          aotinv[nl, ns]=float('nan') #cloudy
        else:
          aotinv[nl, ns]=inversion(sr[nl, ns], interp(lutdata, lutsza, lutvza, lutraa,
          sza[nl, ns], vza[nl, ns], raa[nl, ns]), toa[nl, ns])
          if 0<aotinv[nl, ns]<6: nwell+=1
          else: noutofrange+=1
      else: #inner pixel
        if iscloudy(bl, ir, ns, nl):
          ncloud+=1
          aotinv[nl, ns]=float('nan')
        else:
          aotinv[nl, ns]=inversion(sr[nl, ns], interp(lutdata, lutsza, lutvza, lutraa,
          sza[nl, ns], vza[nl, ns], raa[nl, ns]), toa[nl, ns])
          if 0<aotinv[nl, ns]<6: nwell+=1
          else: noutofrange+=1
  
  writetoh5(aotfn, aotinv, lon, lat)
  print('n of cloudy  : ', ncloud)
  print('n of outrange: ', noutofrange)
  print('n of success : ', nwell)


if __name__=='__main__':
  psacfn='HJ2A_PSAC_E116.9_N35.8_20201106_L10000015715.hdf5'
  lutfn='LUT_HJ2A_670'
  outfn='AOT550.hdf5'
  main(psacfn, lutfn, outfn)
