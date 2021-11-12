#-----------------------------------------------------------------------------------------
# This module for set up multiple functions
#-----------------------------------------------------------------------------------------
from __future__ import print_function
import numpy
import os
import os.path
import pandas as pd

### -----------------------------------------------------------------------------------------
### check if umbrella sampling of short-pmf is finished and if restraint is strong enough
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
              if 'Total wall time' not in open('us_md.out').read() or 'NaN' in open('us_md.out').read() or '[********]' in open('us_md.out').read() or 'Total wall time' not in open('us_npt.out').read() or 'NaN' in open('us_npt.out').read() or '[********]' in open('us_npt.out').read() :
                  os.system("sbatch %s.slm"%(window))
                  os.chdir(path)
              else:
                  new_f=open("md_us_sort.log","w")
                  old_f=open("md_us.log","r")
                  #print (window)
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

### -----------------------------------------------------------------------------------------
### write wham files
### -----------------------------------------------------------------------------------------
def write_wham(us_window_restraint, restraint_number,forward_limit):

    start = round(float( us_window_restraint[restraint_number][0]),2)
    end = round(float( us_window_restraint[restraint_number][1]),2)
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
              if "igr1" in line:
                a,b=line.split(",igr1=")
              else:
                a,b=line.split(",/")
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
              if "igr1" in line:
                a,b=line.split(",igr1=")
              else:
                a,b=line.split(",/")
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

### -----------------------------------------------------------------------------------------
### check wham files
### -----------------------------------------------------------------------------------------
def check_wham(us_window_restraint, restraint_number):

    start = round(float( us_window_restraint[restraint_number][0]),2)
    end = round(float( us_window_restraint[restraint_number][1]),2)
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
              if "igr1" in line:
                a,b=line.split(",igr1=")
              else:
                a,b=line.split(",/")
              c,d=a.split("rk3=")
              restraint=int(float(d))
              fc=restraint*2
          RST.close()
          
          with open("../log_files/metafile","r") as meta: 
            if "%s.log %s"%(window,window) in meta.read():
               pass
            else:
             print ("!!! %s.log %s not in log_files/metafile, need double check !!!"%(window,window))

          met=open("../log_files/metafile","r")
          for line in met:
             if "%s.log %s"%(window,window) in line:
                i,j,k=line.split()
                fc_meta=int(float(k))
          if fc != fc_meta:
             print ("XXXXXXXXXXXXXXXXXXXXXX not match",window,"RST force constant", fc , "metafile force constant", fc_meta)
          else:
             pass
          os.chdir(path)

### -----------------------------------------------------------------------------------------
### plot the data distributions of the umbrella windows to see if overlap is good
### -----------------------------------------------------------------------------------------
def plot(us_window_space,space_number,plot_grid):

    start = round(float(us_window_space[space_number][0]),2)
    end = round(float(us_window_space[space_number][1]),2)
    interval = round(float(us_window_space[space_number][2]),2)
    window_number = int((end-start)/interval)
    path = os.getcwd()
    os.chdir(path)

    dir_list = next(os.walk('.'))[1]
    dir_list.remove("log_files")
    dir_list = [float(i) for i in dir_list]
    dir_list.sort()
    workdir = path + '/log_files/'
    os.chdir(workdir)
    num = 0
    num2 = 1
    for window in dir_list:
       window = round(float(window),2)
       if window >= start and window < end:
          num = num +1
          indicator = num % 7
          if indicator != 0:
             fil = open("plot%s_space%s.py"%(num2,space_number),"a")
             fil.seek(0,2)
             fil.write("data%s=np.loadtxt('%s.log')\n"%(indicator,window))
             fil.write("ax.hist(data%s[:,1],1000, None, fc='none', lw=0.5, histtype='step',label='%s')\n"%(indicator,window))
             fil.close()
          else:
             num2=num2+1
             fil = open("plot%s_space%s.py"%(num2,space_number),"a")
             fil.seek(0,2)
             fil.write("data%s=np.loadtxt('%s.log')\n"%(indicator,window))
             fil.write("ax.hist(data%s[:,1],1000, None, fc='none', lw=0.5, histtype='step',label='%s')\n"%(indicator,window))
             fil.close()

    command1 = open("command1","w")
    command1.write("import os\n")
    command1.write("import numpy as np\n")
    command1.write("import matplotlib\n")
    command1.write("matplotlib.use('agg')\n")
    command1.write("import matplotlib.pyplot as plt\n")
    command1.write("fig,ax=plt.subplots()\n")
    command1.close()

    items = os.listdir(".")
    for names in items:
      if 'py' in names and 'ax.xaxis' not in open(names).read():
         aaa,bbb=names.split(".py")
         ccc,ddd=aaa.split("_space")
         fff,ggg=ccc.split("plot")
         space_n = int(ddd)
         plot_n = int(ggg)
         f=open(names,"r")
         for line in f:
            if "np.loadtxt" in line:
              if "data1" in line:
                 a,b=line.split("loadtxt('")
                 c,d=b.split(".lo")
              else:
                 aa,bb=line.split("loadtxt('")
                 cc,dd=bb.split(".lo")
         ini = round(float(c) - 0.3,2)
         fin = round(float(cc) + 0.3,2)
         fi = open(names,"a")
         fi.seek(0,2)
         fi.write("legend = ax.legend(loc='upper left', shadow=True, fontsize='small')\n")
         fi.write("ax.xaxis.set_ticks(np.arange(%s, %s, %s))\n"%(ini,fin,plot_grid))
         fi.write("plt.xlabel('r$_{M-C}$ ($\AA$)')\n")
         fi.write("plt.ylabel('Number of counts')\n")
         fi.write("plt.savefig('plot%s_space%s.png')\n"%(plot_n,space_n))
         fi.close()
         os.system("cat command1 %s > final_%s"%(names,names))
         os.system("python final_%s"%(names))
    os.chdir(path)

### -----------------------------------------------------------------------------------------
### check if us_md2 is completed properly
### -----------------------------------------------------------------------------------------
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
                if 'Total wall time' not in open('us_md2.out').read() or 'NaN' in open('us_md2.out').read() or '[********]' in open('us_md2.out').read():
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
                       pass
                    else:
                       print (window)
                       print ('XXXXXXXXXXXXXXXXXXXXXXXXX not good', lower_b, window, upper_b)
                    os.chdir(path)
             else:
                print ('missing us_md2.out')
                os.system("sbatch %s2.slm"%(window))
                os.chdir(path)

### -----------------------------------------------------------------------------------------
### check if us_npt, us_md, and us_md2 are completed properly
### -----------------------------------------------------------------------------------------
def check_force3(us_window_optimize, optimize_number, us_window_restraint, center_deviation):

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
           if os.path.isfile('us_md.out') and os.path.isfile('us_npt.out') and os.path.isfile('us_md2.out'):
              if 'Total wall time' not in open('us_md.out').read() or 'NaN' in open('us_md.out').read() or '[********]' in open('us_md.out').read() or 'Total wall time' not in open('us_npt.out').read() or 'NaN' in open('us_npt.out').read() or '[********]' in open('us_npt.out').read() or 'Total wall time' not in open('us_md2.out').read() or 'NaN' in open('us_md2.out').read() or '[********]' in open('us_md2.out').read():
                  os.system("sbatch %s-all.slm"%(window))
                  os.chdir(path)
              else:
                  os.system("cat md_us.log md2_us2.log > md_usc.log")
                  os.system("awk '{ print NR FS $2 }' md_usc.log > md_usf.log")
                  new_f=open("md_usf_sort.log","w")
                  old_f=open("md_usf.log","r")
                  for line in old_f:
                    i,j=line.split()
                    new_f.write("%s,%s\n"%(i,j))
                  old_f.close()
                  new_f.close()
                  data=pd.read_csv('md_usf_sort.log', sep=',',header=0,engine='python')
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
              print ('missing us_npt.out and/or us_md.out and/or us_md2.out')
              os.system("sbatch %s-all.slm"%(window))
              os.chdir(path)
