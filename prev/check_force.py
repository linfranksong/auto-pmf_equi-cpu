#-----------------------------------------------------------------------------------------
# This module for set up multiple functions
#-----------------------------------------------------------------------------------------
from __future__ import print_function
import numpy
import os
import os.path
import pandas as pd

### -----------------------------------------------------------------------------------------
### check if umbrella sampling is finished and if restraint is strong enough
### -----------------------------------------------------------------------------------------
def check_force(us_window_optimize, optimize_number, us_window_restraint, center_deviation):

    ini = round(float(us_window_optimize[optimize_number][0]),2)
    fin = round(float(us_window_optimize[optimize_number][1]),2)
    center_deviation = float(center_deviation)
    path = os.getcwd() +'/'
    dir_list = next(os.walk('.'))[1]
    if 'log_files' in dir_list:
      dir_list.remove('log_files')
    dir_list = [float(i) for i in dir_list]
    dir_list.sort()

    for window in dir_list:
       window = round(float(window),2)
       if window >= ini and window <= fin:
           workdir = path + '%s/'%(window)
           os.chdir(workdir)
           if os.path.isfile('us_md.out') and os.path.isfile('us_npt.out'):
              if 'Total wall time' not in open('us_md.out').read() or 'NaN' in open('us_md.out').read() or '[********]' in open('us_md.out').read() or 'Total time' not in open('us_npt.out').read() or 'NaN' in open('us_npt.out').read() or '[********]' in open('us_npt.out').read() :
                  os.system("sbatch %s.slm"%(window))
                  os.chdir(path)
              else:
                  new_f=open("md_us_sort.log","w")
                  old_f=open("md_us.log","r")
                  for line in old_f:
                    i,j=line.split()
                    new_f.write("%s,%s\n"%(i,j))
                  old_f.close()
                  new_f.close()
                  data=pd.read_csv('md_us_sort.log', sep=',',header=0,engine='python')
                  data.columns = ["num", "value"]
                  avg=data["value"].mean()
                  std=data["value"].std()
                  mean=round(avg,3)
                  std=round(std,3)
                  lower_b = mean - center_deviation*std
                  upper_b = mean + center_deviation*std
                  if lower_b < round(float(window),2) and round(float(window),2) < upper_b:
                     pass
                  else:
                     print (window)
                     print ('XXXXXXXXXXXXXXXXXXXXXXXXX not good', lower_b, window, upper_b)
                  os.chdir(path)
           else:
              print ('missing us_npt.out and/or us_md.out')
              os.system("sbatch %s.slm"%(window))
              os.chdir(path)

def check_force2(us_window_optimize, optimize_number, us_window_restraint, center_deviation):

    ini = round(float(us_window_optimize[optimize_number][0]),2)
    fin = round(float(us_window_optimize[optimize_number][1]),2)

    center_deviation = float(center_deviation)

    path = os.getcwd() +'/'
    dir_list = next(os.walk('.'))[1]
    if 'log_files' in dir_list:
      dir_list.remove('log_files')
    dir_list = [float(i) for i in dir_list]
    dir_list.sort()

    for window in dir_list:
       window = round(float(window),2)
       if window >= ini and window <= fin:
             workdir = path + '%s/'%(window)
             os.chdir(workdir)
             if os.path.isfile('us_md2.out'):
                if 'Total wall time' not in open('us_md2.out').read() or 'NaN' in open('us_md2.out').read():
                    #print 'not finished'
                    os.system("sbatch %s2.slm"%(window))
                    os.chdir(path)
                else:
                    new_f=open("md_us_sort2.log","w")
                    old_f=open("md2_us2.log","r")
                    for line in old_f:
                      i,j=line.split()
                      new_f.write("%s,%s\n"%(i,j))
                    old_f.close()
                    new_f.close()
                    
                    data=pd.read_csv('md_us_sort2.log', sep=',',header=0,engine='python')
                    data.columns = ["num", "value"]
                    avg=data["value"].mean()
                    std=data["value"].std()
                    mean=round(avg,3)
                    std=round(std,3)
                    lower_b = mean - center_deviation*std
                    upper_b = mean + center_deviation*std
                    if lower_b < round(float(window),2) and round(float(window),2) < upper_b:
                       #print 'good;', lower_b, window, upper_b
                       pass
                    else:
                       print (window)
                       print ('XXXXXXXXXXXXXXXXXXXXXXXXX not good', lower_b, window, upper_b)
                    os.chdir(path)
             else:
                print ('no us_md2.out')
                os.system("sbatch %s2.slm"%(window))
                os.chdir(path)
