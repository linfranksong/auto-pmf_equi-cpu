#------------------------------------------------------------------------------
# This module is for making umbrella sampling folders and mdin files
#------------------------------------------------------------------------------
from __future__ import print_function
import numpy
import os
import os.path
import pandas as pd

def write_wham(us_window_restraint, restraint_number,forward_limit):

    start = round(float( us_window_restraint[restraint_number][0]),2)
    end = round(float( us_window_restraint[restraint_number][1]),2)
    restraint_const = 2*round(float( us_window_restraint[restraint_number][2]),2)
    path = os.getcwd()
    os.chdir(path)

    dir_list = next(os.walk('.'))[1]
    if 'log_files' in dir_list:
      dir_list.remove('log_files')
    dir_list = [float(i) for i in dir_list]
    dir_list.sort()


    for window in dir_list:
       window = round(float(window),2)
       if window >= start and window < end:
          workdir = path + '/%s/'%(window)
          os.chdir(workdir)

          if os.path.isfile("md2_us2.log"):
             os.system("cat md_us.log md2_us2.log > md_usc.log")
             os.system("awk '{ print NR FS $2 }' md_usc.log > md_usf.log")
          else:
             os.system("cp md_us.log md_usf.log")

          RST=open("us_dis.RST","r")
          for line in RST:
            if "rk3" in line:
              a,b=line.split(",igr1=")
              #a,b=line.split(",/")
              c,d=a.split("rk3=")
              restraint=int(float(d))
              fc=restraint*2
          RST.close()

          cplog_sh = open("../cp_log.sh","a")
          cplog_sh.seek(0,2)
          print("cp %s/md_usf.log log_files/%s.log"%(window,window),file=cplog_sh)
          cplog_sh.close()

          meta_file = open("../metafile",'a')
          meta_file.seek(0,2)
          print("%s.log %s %d"%(window, window, fc),file=meta_file)
          meta_file.close()
          os.chdir(path)
       elif window == end and end == round(float(forward_limit),2):
          workdir = path + '/%s/'%(window)
          os.chdir(workdir)

          if os.path.isfile("md2_us2.log"):
             os.system("cat md_us.log md2_us2.log > md_usc.log")
             os.system("awk '{ print NR FS $2 }' md_usc.log > md_usf.log")
          else:
             os.system("cp md_us.log md_usf.log")

          RST=open("us_dis.RST","r")
          for line in RST:
            if "rk3" in line:
              a,b=line.split(",igr1=")
              #a,b=line.split(",/")
              c,d=a.split("rk3=")
              restraint=int(float(d))
              fc=restraint*2
          RST.close()

          cplog_sh = open("../cp_log.sh","a")
          cplog_sh.seek(0,2)
          print("cp %s/md_usf.log log_files/%s.log"%(window,window),file=cplog_sh)
          cplog_sh.close()

          meta_file = open("../metafile",'a')
          meta_file.seek(0,2)
          print("%s.log %s %s"%(window, window, fc),file=meta_file)
          meta_file.close()
          os.chdir(path)
