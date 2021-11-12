import os
import pandas as pd

def check_wham(us_window_restraint, restraint_number):

    #print("**** checking metafile for space %s..."%(restraint_number))

    start = round(float( us_window_restraint[restraint_number][0]),2)
    end = round(float( us_window_restraint[restraint_number][1]),2)
    restraint_const = 2*round(float( us_window_restraint[restraint_number][2]),2)
    path = os.getcwd() +'/'
    dir_list = next(os.walk('.'))[1]
    dir_list.remove('log_files')
    dir_list = [float(i) for i in dir_list]
    dir_list.sort()

    for window in dir_list:
       window = round(float(window),2)
       if window >= start and window < end:
          workdir = path + '%s/'%(window)
          os.chdir(workdir)

          RST=open("us_dis.RST","r")
          for line in RST:
            if "rk3" in line:
              a,b=line.split(",igr1=")
              #a,b=line.split(",/")
              c,d=a.split("rk3=")
              restraint=int(float(d))
              fc=restraint*2
          RST.close()
          
          #if "%slog_files//%s.log %s %s"%(path,window,window,fc) not in open(../log_files/metafile).read():
          meta=open("../log_files/metafile","r")
          for line in meta:
             if "%s.log %s"%(window,window) in line:
                i,j,k=line.split()
                fc_meta=int(float(k))
          if fc != fc_meta:
             print ("XXXXXXXXXXXXXXXXXXXXXX not match",window,"RST force constant", fc , "metafile force constant", fc_meta)
          else:
            #print "match",window,"RST restraint", restraint, "metafile force constant", fc_meta
             pass
          os.chdir(path)
