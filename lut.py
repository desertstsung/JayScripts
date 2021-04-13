#!/usr/bin/python3

"""

Description:
  Python3 scripts to generate simple Look-Up Table (LUT)
  Using 6SV2.1 to simulate atmospheric condition in certain options

Arguments:
  -m, --month=N (OPTIONAL)
         Specify the month range from 1 to 12
         1 by default
  -d, --day=N (OPTIONAL)
         Specify the day which start at 1
         1 by default
  -a, --atmospheremode=N (OPTIONAL)
         +---+--------------------------+
         | N | Meaning                  |
         +---+--------------------------+
         | 0 | No absoption             |
         +---+--------------------------+
         | 1 | Trops.                   |
         +---+--------------------------+
         | 2 | Midlatitude Summer       |
         +---+--------------------------+
         | 3 | Midlatitude Winter       |
         +---+--------------------------+
         | 4 | Subart. Summer           |
         +---+--------------------------+
         | 5 | Subart. Winter           |
         +---+--------------------------+
         | 6 | US62 (By default)        |
         +---+--------------------------+
  -b, --aerosolmode=N (OPTIONAL)
         +---+--------------------------+
         | N | Meaning                  |
         +---+--------------------------+
         | 1 | Continental (By default) |
         +---+--------------------------+
         | 2 | Maritime                 |
         +---+--------------------------+
         | 3 | Urban                    |
         +---+--------------------------+
         | 5 | Desert                   |
         +---+--------------------------+
         | 6 | Biom.                    |
         +---+--------------------------+
         | 7 | Stratos.                 |
         +---+--------------------------+
  -e, --min-sza=N (OPTIONAL)
         Specify the min value of solar zenith angle range from 0 to 180
         Required if max-sza is presented
         0 by default
  -f, --max-sza=N (OPTIONAL)
         Specify the max value of solar zenith angle range from 0 to 180
         Required if min-sza is presented
         90 by default
  -g, --step-sza=N (OPTIONAL)
         Specify the step of solar zenith angle range from 0 to 180
         10 by default if min-sza and max-sza is not specified
         1 by default if min-sza and max-sza is specified
  -i, --min-vza=N (OPTIONAL)
         Specify the min value of view zenith angle range from 0 to 180
         Required if max-vza is presented
         0 by default
  -j, --max-vza=N (OPTIONAL)
         Specify the max value of view zenith angle range from 0 to 180
         Required if min-vza is presented
         90 by default
  -k, --step-vza=N (OPTIONAL)
         Specify the step of view zenith angle range from 0 to 180
         10 by default if min-vza and max-vza is not specified
         1 by default if min-vza and max-vza is specified
  -o, --min-raa=N (OPTIONAL)
         Specify the min value of relative azimuth angle range from 0 to 180
         Required if max-raa is presented
         0 by default
  -p, --max-raa=N (OPTIONAL)
         Specify the max value of relative azimuth angle range from 0 to 180
         Required if min-raa is presented
         180 by default
  -q, --step-raa=N (OPTIONAL)
         Specify the step of relative azimuth angle range from 0 to 180
         10 by default if min-raa and max-raa is not specified
         1 by default if min-raa and max-raa is specified
  -x, --aod-range=FLOAT,FLOAT,FLOAT... (OPTIONAL)
         Specify the value range of AOD550
         [0.01, 0.05, 0.1, 0.15, 0.2, 0.3, 0.4, 0.5, 1, 2, 3, 5] by default
  -l, --lut=FILE (OPTIONAL)
         Use FILE to specify the output LUT file path
         /path/to/this/directory/LUT by default
  -s, --sixs=FILE (OPTIONAL)
         Use FILE to specify the 6SV executable file path
         /path/to/this/directory/sixsV2.1 by default
  -w, --wavelength=FLOAT (OPTIONAL)
         Specify the center wavelength in um
         0.55 um (550 nm) by default
  -h, --help
         Show the manuals to this script

Example:
  lut.py --help
    Print this manual
  lut.py -m 12 -d 11 -a 3 --wave=0.555
    Means date in Dec 11, and atm mode is midlat winter
    and center wavelength at 555 nm
  lut.py --month=12 --day=11 --lut=mylut.dat -s /usr/local/bin/sixsV2.1
    Means date in Dec 11
    and output file is /path/to/this/directory/mylut.dat
    and the 6SV executable file path is /usr/local/bin/sixsV2.1
  lut.py -m 12 -d 11 -x 0.1,0.2,0.3,0.4,0.5,1,2,5 -i 0 -j 50 -k 5
    Means date in Dec 11
    and aerosol range is [0.1, 0.2, 0.3, 0.4, 0.5, 1, 2, 5]
    and vza range is [0, 5, 10, ... 45, 50]

Built-in Parameters:
  Target at ground: No reflectance at sea level
  View altitude: Sensor onboard satellite

LUT structure:
  Saves value in binary by order
  Header include angle information
  Body contains every simulation record
  One record contains path reflectance,
  Spherical albedo, transmittance and aot550

LUT technical description in C style:
  struct Header1 {
    char nsza; //number of sza
    char nvza; //number of vza
    char nraa; //number of raa
    char naot; //number of aot550
  };
  
  struct Header2 {
    float sza[header1->nsza]; //detail of sza
    float vza[header1->nvza]; //detail of vza
    float raa[header1->nraa]; //detail of raa
    float aot[header1->naot]; //detail of aot550
  };
  
  struct Header {
    struct Header1 header1;
    struct Header2 header2;
  };
  
  struct Body3 {
    float p;                  //path reflectance in certian angles and aot550
    struct Body3 *body3_of_next_angles_aot550;
  };
  
  struct Body2 {
    float tdn;                //downward scattering transmittance in certain zenith angle and aot550
    float tup;                //upward scattering transmittance in certain zenith angle and aot550
    float t;                  //total gaseous transmittance in certain zenith angle and aot550
    struct Body3 body3;
    struct Body2 *body2_of_next_zenith_angle_aot550;
  };
  
  struct Body1 {
    float s;                  //spherical albedo in certain aot550
    struct Body2 body2;
    struct Body1 *body1_of_next_aot550;
  };
  
  struct LUTfile {
    struct Header header;
    struct Body1 body1;
  };

Author: Jay Tsung, Apr 13 21'

"""


import sys
from time import ctime
from array import array
from copy import deepcopy
from re import split as strtok
from os import path, remove as rm
from getopt import getopt, GetoptError
from subprocess import getstatusoutput as execute


#Display Usage in stdout
def usage():
  with open(sys.argv[0]) as fo:
    for _ in range(3): next(fo)
    for _ in iter(int, 1):
      l=fo.readline()
      if l.startswith('"""'): break
      else: print(l.rstrip())
  sys.exit(2)


#Return all elements from a list in 1-dimention
#example: [1, [2, 3], [4, [5, 6]]] -> [1, 2, 3, 4, 5, 6]
def list1d(a):
  r=[]
  for i in a:
    if type(i) is list: r+=list1d(i)
    else: r.append(i)
  return r


class LUT:
  #initialize class
  def  __init__(self, inputfile, sixsfile, lutfile):
    floatn=float('nan')
    self.inputfile=inputfile
    self.sixsfile=sixsfile
    self.result=''
    self.gastrans=floatn
    self.scatransup=floatn
    self.scatransdown=floatn
    self.s=floatn
    self.pathref=floatn
    self.lutfile=lutfile
  
  #write header to LUT file
  def writeLUTheader(self, sza, vza, raa, aot550):
    with open(self.lutfile, 'ab') as fo:
      array('b', [len(sza), len(vza), len(raa), len(aot550)]).tofile(fo)
      array('f', list(sza)+list(vza)+list(raa)+list(aot550)).tofile(fo)
  
  #update input file
  #par=(sza, raa, vza, month, day, atmode, aermod, aot550, wv)
  def modifyinput(self, par):
    self.currentaot=par[7]
    with open(self.inputfile, 'w+') as fo:
      fo.write("""0
%3d %3d %3d 0 %2d %2d       # geometrical
%1d                         # atm mode
%1d                         # aerosol mode 
0
%6.4f                       # aot550
0                           # altitude
-1000                       # sensor onboard satellite
-1
%5.3f                       # centre wavelength
0
0
0
0                           # const 0 reflectance
-1                          # no atmospheric correction""" % par)

  #run input file and get result
  def run(self):
    exitcode, output=execute('"'+self.sixsfile+'" < "'+self.inputfile+'"')
    self.result=output

  #extract information from the result
  def extract(self):
    for tmp in self.result.replace('*', '').splitlines():
      if tmp.find('global gas. trans.')!=-1: self.gastrans=float(strtok(' +', tmp.split(':')[1])[3])
      if tmp.find('total  sca.')!=-1:
        self.scatransdown=float(strtok(' +', tmp.split(':')[1])[1])
        self.scatransup=float(strtok(' +', tmp.split(':')[1])[2])
      if tmp.find('spherical albedo')!=-1: self.s=float(strtok(' +', tmp.split(':')[1])[3])
      if tmp.find('reflectance I')!=-1: self.pathref=float(strtok(' +', tmp.split(':')[1])[3])
  
  #write result to lut file
  def writedata(self, lutdata):
    lutdata=list1d(lutdata)
    with open(self.lutfile, 'ab') as fo:
      array('f', lutdata).tofile(fo)
  
  #one step
  def onestep(self, par):
    self.modifyinput(par)
    self.run()
    self.extract()
  
  #EOL of this LUT class
  def __del__(self):
    rm(self.inputfile)


if __name__=='__main__':
  
  #Default parameters
  sixsfile, inputfile, lutfile = [path.join(path.dirname(sys.argv[0]), _) for _ in ['sixsV2.1', 'tmp', 'LUT']]
  sza=[0, 12, 24, 36, 48, 54, 60, 66, 72, 78, 84]
  vza=[0, 6, 12, 18, 24, 30, 36, 42, 48, 54, 60, 66, 72, 78, 84]
  raa=[0, 12, 24, 36, 48, 60, 72, 84, 96, 108, 120, 132, 144, 156, 168, 180]
  aot=[0.01, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.6, 0.8, 1, 2, 5]
  wv=0.55
  atmode=6
  aermod=1
  month, day=1, 1
  
  #Update parameters from CLI
  try:
    opts, tmp=getopt(sys.argv[1:], 'm:d:a:b:e:f:g:i:j:k:o:p:q:x:l:s:w:h',
              ['month=', 'day=', 'atmospheremode=', 'aerosolmode=',
               'min-sza=', 'max-sza=', 'step-sza=',
               'min-vza=', 'max-vza=', 'step-vza=',
               'min-raa=', 'max-raa=', 'step-raa=',
               'aod-range=', 'lut=', 'sixs=', 'wavelength=',  'help'])
    for opt, arg in opts:
      if opt in ['-m', '--month']: month=int(arg)
      elif opt in ['-d', '--day']: day=int(arg)
      elif opt in ['-a', '--atmospheremode']: atmode=int(arg)
      elif opt in ['-b', '--aerosolmode']: aermod=int(arg)
      elif opt in ['-e', '--min-sza']: sza_min=int(arg)
      elif opt in ['-f', '--max-sza']: sza_max=int(arg)
      elif opt in ['-g', '--step-sza']: sza_step=int(arg)
      elif opt in ['-i', '--min-vza']: vza_min=int(arg)
      elif opt in ['-j', '--max-vza']: vza_max=int(arg)
      elif opt in ['-k', '--step-vza']: vza_step=int(arg)
      elif opt in ['-o', '--min-raa']: raa_min=int(arg)
      elif opt in ['-p', '--max-raa']: raa_max=int(arg)
      elif opt in ['-q', '--step-raa']: raa_step=int(arg)
      elif opt in ['-x', '--aod-range']: aot=[float(_) for _ in arg.split(',')]
      elif opt in ['-l', '--lut']:
        lutfile=path.join(path.dirname(sys.argv[0]), arg) if arg.find(path.sep)==-1 else arg
      elif opt in ['-s', '--sixs']: sixsfile=arg
      elif opt in ['-w', '--wavelength']: wv=float(arg)
      elif opt in ['-h', '--help']: usage()
      else: assert False, "unhandled option"
    if 'sza_min' in vars() and 'sza_max' in vars():
      step=sza_step if 'sza_step' in vars() else 1
      sza=range(sza_min, sza_max+step, step)
    if 'vza_min' in vars() and 'vza_max' in vars():
      step=vza_step if 'vza_step' in vars() else 1
      vza=range(vza_min, vza_max+step, step)
    if 'raa_min' in vars() and 'raa_max' in vars():
      step=raa_step if 'raa_step' in vars() else 1
      raa=range(raa_min, raa_max+step, step)
  except GetoptError: usage()
  
  #Ensure the input
  print('Please ensure the following options you entered')
  print('6SV executable file: ', sixsfile)
  print('Output LUT file    : ', lutfile)
  print('Wavelength         : ', wv)
  print('Date (month day)   : ', month, day)
  print('Atmosphere mode    : ', atmode)
  print('Aerosol mode       : ', aermod)
  print('SZA range          : ', sza)
  print('VZA range          : ', vza)
  print('RAA range          : ', raa)
  print('AOD550 range       : ', aot)
  if not input('Do you want to continue? [Y/n]').lower().startswith('y'):
    print('Abort.')
    sys.exit(2)
  
  print('Start at: ', ctime())
  
  if path.exists(lutfile): rm(lutfile)
  lut=LUT(inputfile, sixsfile, lutfile)
  lut.writeLUTheader(sza, vza, raa, aot)
  print('\r', end='')
  
  tmp1=[0 for _ in raa]
  tmp2=[0 for _ in range(len(sza)*len(vza))]
  for i in range(len(tmp2)):
    tmp2[i]=[0, 0, 0, deepcopy(tmp1)]
  lutdata=[0 for _ in aot]
  for i in range(len(lutdata)):
    lutdata[i]=[0, deepcopy(tmp2)]
  
  n=0
  lsza, lvza, lraa, laot=len(sza), len(vza), len(raa), len(aot)
  total=lsza*lvza*lraa*laot
  for i in range(laot):
    for j in range(lsza):
      for k in range(lvza):
        for l in range(lraa):
          lut.onestep((sza[j], raa[l], vza[k], month, day, atmode, aermod, aot[i], wv))
          lutdata[i][1][lvza*j+k][3][l]=lut.pathref
          n+=1
          if str(n).endswith('00'): print('\r', '{:6.2f}%'.format(n*100/total), end='', flush=True)
        lutdata[i][1][lvza*j+k][0:3]=[lut.scatransdown, lut.scatransup, lut.gastrans]
    lutdata[i][0]=lut.s
  lut.writedata(lutdata)
  lut=None
  print('\nLUT file in: ', lutfile)
  
  print('End at:   ', ctime())
  sys.exit(0)

