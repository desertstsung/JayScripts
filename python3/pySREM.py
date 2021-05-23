#!/usr/bin/env python3
from math import sin, cos, radians, acos, exp


class SREM(object):
  """
  Surface Reflectance Estimation Method (SREM)
  From https://doi.org/10.3390/rs11111344
  
  Required:
    +-----------+-------------------+----------------------------------+
    | Parameter | Type              | Description                      |
    +-----------+-------------------+----------------------------------+
    | toa       | Scalar or ndarray | Reflectance at Top-Of-Atmosphere |
    | lam       | Scalar            | Wavelength in Micrometre         |
    | theta_s   | Scalar or ndarray | Satellite Zenithal Angle         |
    | theta_v   | Scalar or ndarray | Viewing Zenithal Angle           |
    | phi       | Scalar or ndarray | Relative Azimuthal Angle         |
    +-----------+-------------------+----------------------------------+
  
  Default:
    +-----------+------+-------+---------------------------+
    | Parameter | Type | Value | Description               |
    +-----------+------+-------+---------------------------+
    | radian    | Bool | Fasle | All Angle in Degree Units |
    +-----------+------+-------+---------------------------+
  
  Output:
    sr Stands for Surface Reflectance
  
  Sample:
    from pySREM import SREM
    srem=SREM(toa=0.5, lam=0.553, theta_s=30, theta_v=25, phi=67, radian=False)
    srem.run()
    print(srem.sr)
    
  """
  def __init__(self, radian=False, *, toa, lam, theta_s, theta_v, phi):
    self.toa=toa
    self.lam=lam
    if radian:
      self.theta_s=theta_s
      self.theta_v=theta_v
      self.phi=phi
    else:
      self.theta_s=radians(theta_s)
      self.theta_v=radians(theta_v)
      self.phi=radians(phi)
    self.ctheta_s=cos(self.theta_s)
    self.ctheta_v=cos(self.theta_v)
    
    self.rod=self.rod()
    self.csa=self.csa()
    self.rpf=self.rpf()
    
    self.sr=-1
  
  # Rayleigh Optical Depth
  # From https://doi.org/10.1007/BF00168069
  def rod(self):
    return 0.008569*(t:=self.lam**-4)*(1+0.0113*self.lam**-2+0.0013*t)
  
  # cos(Scattering Angle)
  # From https://doi.org/10.1016/S0074-6142(02)80026-2
  def csa(self):
    return -self.ctheta_s*self.ctheta_v+sin(self.theta_s)*sin(self.theta_v)*cos(self.phi)
  
  # Rayleigh Phase Function
  # From https://sentinels.copernicus.eu/documents/247904/349589/OLCI_L2_Rayleigh_Correction_Land.pdf
  def rpf(self, value_A=0.9587256):
    return 3*value_A*(1+self.csa**2)/4+1-value_A
  
  # Rayleigh Reflectance
  # From https://sentinels.copernicus.eu/documents/247904/349589/OLCI_L2_Rayleigh_Correction_Land.pdf
  def rr(self):
    return self.rpf*(1-exp(-(1/self.ctheta_s+1/self.ctheta_v)*self.rod))/(4*(self.ctheta_s+self.ctheta_v))
  
  # Atmospheric Backscattering Ratio
  # From https://doi.org/10.1364/AO.18.003587
  # Assuming tau_p is 0
  def abr(self):
    return 0.92*self.rod*exp(-self.rod)
  
  # Total Atmospheric Transmission
  # From https://doi.org/10.1364/AO.18.003587
  # Assuming tau_p is 0
  def tat(self):
    return exp(-(t1:=self.rod/self.ctheta_s))*(exp(0.52*t1)-1)*exp(-(t2:=self.rod/self.ctheta_v))*(exp(0.52*t2)-1)
  
  # SREM Method
  def run(self):
    self.sr=(t:=self.toa-self.rr())/(t*self.abr()+self.tat())
    print(t)

