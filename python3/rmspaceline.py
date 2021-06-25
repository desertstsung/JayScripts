#!/usr/bin/env python

###########################
# Remove spaces in lines  #
# which is full of spaces #
###########################

import sys

with open(sys.argv[1], "r") as f:
        t=f.readlines()
with open(sys.argv[2], "w") as f:
        for e in t:
                f.write("\n" if e.isspace() else e)
