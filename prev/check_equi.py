import os
import pandas as pd

def check_equi(us_window_optimize, optimize_number, us_window_restraint, center_deviation):

    #print("**** checking equilibration step for space %s..."%(optimize_number))

    ini = round(float(us_window_optimize[optimize_number][0]),2)
    fin = round(float(us_window_optimize[optimize_number][1]),2)
    #start = int(float(us_window_optimize[optimize_number][2]))
    #end = int(float(us_window_optimize[optimize_number][3]))

    #ini_r = round(float(us_window_restraint[restraint_number][0]),2)
    #fin_r = round(float(us_window_restraint[restraint_number][1]),2)

    center_deviation = float(center_deviation)

    path = os.getcwd() +'/'
    dir_list = next(os.walk('.'))[1]
    if "log_files" in os.listdir('.'):
      dir_list.remove('log_files')
    dir_list = [float(i) for i in dir_list]
    dir_list.sort()

    for window in dir_list:
       window = round(float(window),2)
       if window >= ini and window <= fin:
          #if window >= ini_r and window < fin_r:
             workdir = path + '%s/'%(window)
             os.chdir(workdir)
             #print window
             if os.path.isfile('us_md.out'):
                if 'Total wall time' not in open('us_npt.out').read() or 'NaN' in open('us_npt.out').read() or '[********]' in open('us_npt.out').read():
                    #os.system("sed -i 's/pmemd.cuda -O -i us_min.in/#pmemd.cuda -O -i us_min.in/g' *slm")
                    #os.system("sed -i 's/pmemd.cuda -O -i us_nvt.in/#pmemd.cuda -O -i us_nvt.in/g' *slm")
                    #print '%s not finished'%(window)
                    os.system("sbatch %s.slm"%(window))
                    os.chdir(path)
                else:
                    pass
                    os.chdir(path)
             else:
                print ('%s no us_npt.out'%(window))
                os.chdir(path)
