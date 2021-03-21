#!/usr/bin/python3

import matplotlib.pyplot as plt
import numpy as np

def getdata(fn):
  pass
  return x, y

def scplot(x, y):
  plt.figure(figsize=(7, 7), dpi=300)
  plt.scatter(x,y, c='black', s=2)
  plt.xticks(range(0, 250, 50), fontsize=8)
  plt.yticks(range(0, 250, 50), fontsize=8)
  plt.xlabel("X Value", fontdict={'size': 8})
  plt.ylabel("Y Value", fontdict={'size': 8})
  plt.title('Title', fontdict={'size': 10})
  coefs=np.polyfit(x, y, 1)
  p=np.poly1d(coefs)
  y_=p(x)
  r2=1-(((y-y_)**2).sum()/((y-np.array(y).mean())**2).sum())
  plt.plot(x, y_, "r-")
  plt.plot(range(0, 450, 50), range(0, 450, 50), 'k--')
  plt.xlim(0, 250)
  plt.ylim(0, 250)
  plt.gca().set_aspect('equal', adjustable='box')
  label="""y=%4.2fx%+4.2f
$R^2=%6.4f$""" % (coefs[0], coefs[1], r2)
  plt.text(160, 10, label)
  plt.show()

if __name__=='__main__':
  x,y=getdata(fn)
  scplot(x, y)
