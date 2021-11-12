#!/mnt/home/songlin3/anaconda3/bin/python
from __future__ import print_function
import os
from optparse import OptionParser
import numpy
import math
from cal_ave_di import freeMD
from smd_forward import smd_forward_MD
from smd_reverse import smd_reverse_MD
from us_NVT import us_restraint_setup
from us import us_mkdir
from us_NVT import us_mkdir_NVT
from us_2 import us2
from us_NVT_2 import us2_NVT
from functions import check_force, check_force2, write_wham, check_wham, plot, check_force3

#----------------------------------------------------------------------------#
#                            Main Program                                    #
#----------------------------------------------------------------------------#
parser = OptionParser("Usage: Auto-PMF-NVT-di_equi-cpu.py -i inputfile -s/--step step_number \n")

parser.add_option("-i", dest="inputf", type='string',
                  help="Input file name")
parser.add_option("-s", "--step", dest="step", type='string',
                  help="Step number")
(options, args) = parser.parse_args()


# Print the title of the program
version = '1.0'

#---------------------------Default values------------------------------------

# About the program 
mode = 'normal'
prmtop = 'INITIAL.prmtop'
inpcrd = 'INITIAL.inpcrd'
ADDTIONAL_RST="NONE"

if options.step not in ['prepare', 'sampling_NVT','check_force','write_wham','check_wham','result','adaptive_force', 'check_force2', 'adaptive_force2','us2_NVT','check_force3']:
    raise pymsmtError('Invalid step number chosen. please choose among the following values: prepare, sampling_NVT,check_force,write_wham,check_wham,result,adaptive_force,check_force2,adaptive_force2,us2_NVT,check_force3')
#----------------------------Read the input files------------------------------
rinput = open(options.inputf, 'r')
for line in rinput:
    line = line.split()
    if line[0].lower() == "inputin":
        inputin = line[1]
    if line[0].lower() == "mode":
        mode = line[1]
    elif line[0].lower() == "prmtop":
        prmtop = line[1]
    elif line[0].lower() == "inpcrd":
        inpcrd = line[1]
    elif line[0].lower() == "coord_type":
        coord_type = line[1]
    elif line[0] == "ADDTIONAL_RST":
        ADDTIONAL_RST = line[1]
    elif line[0].lower() == "coord_atm1_num":
        coord_atm1_num = line[1]
    elif line[0].lower() == "coord_atm2_num":
        coord_atm2_num = line[1]
    elif line[0].lower() == "md_min_steps":
        md_min_steps = int(line[1])
    elif line[0].lower() == "md_nvt_steps":
        md_nvt_steps = int(line[1])
    elif line[0].lower() == "md_npt_steps":
        md_npt_steps = int(line[1])
    elif line[0].lower() == "md_md_steps":
        md_md_steps = int(line[1])
    elif line[0].lower() == "smd_forward_md_steps":
        smd_forward_md_steps = int(line[1])
    elif line[0].lower() == "forward_limit":
        forward_limit = line[1]
    elif line[0].lower() == "smd_reverse_md_steps":
        smd_reverse_md_steps = int(line[1])
    elif line[0].lower() == "reverse_limit":
        reverse_limit = line[1]
    elif line[0].lower() == "us_npt_steps":
        us_npt_steps = int(line[1])
    elif line[0].lower() == "us_md_steps":
        us_md_steps = int(line[1])
    elif line[0].lower() == "us_window_space":
        space_num = (len(line)-1)//3
        us_window_space = {}
        for num in range(1,space_num+1):
           us_window_space[num]=[]
           us_window_space[num].append(line[(num-1)*3+1])
           us_window_space[num].append(line[(num-1)*3+2])
           us_window_space[num].append(line[(num-1)*3+3])
    elif line[0].lower() == "us_window_restraint":
        restraint_num = (len(line)-1)//3
        us_window_restraint = {}
        for num in range(1,restraint_num+1):
           us_window_restraint[num]=[]
           us_window_restraint[num].append(line[(num-1)*3+1])
           us_window_restraint[num].append(line[(num-1)*3+2])
           us_window_restraint[num].append(line[(num-1)*3+3])
    elif line[0].lower() == "us_window_optimize":
        optimize_num = (len(line)-1)//3
        us_window_optimize = {}
        for num in range(1,optimize_num+1):
           us_window_optimize[num]=[]
           us_window_optimize[num].append(line[(num-1)*5+1])
           us_window_optimize[num].append(line[(num-1)*5+2])
           us_window_optimize[num].append(line[(num-1)*5+3])
           #us_window_optimize[num].append(line[(num-1)*5+4])
           #us_window_optimize[num].append(line[(num-1)*5+5])
    elif line[0].lower() == "slm_header":
        slm_header = line[1]
    elif line[0].lower() == "wham_tol":
        wham_tol = line[1]
    elif line[0].lower() == "wham_window":
        wham_window = line[1]
    elif line[0].lower() == "center_deviation":
        center_deviation = line[1]
    elif line[0].lower() == "test_us_md_steps":
        test_us_md_steps = int(line[1])
    elif line[0].lower() == "plot_grid":
        plot_grid = line[1]
rinput.close()

#-------------------Setting for the program and steps use----------------------
if mode == "test":
    md_min_steps = 500
    md_nvt_steps = 20000
    md_npt_steps = 500
    md_md_steps = 2000
    smd_forward_md_steps = 2000
    smd_reverse_md_steps = 2000
#--------------------------------Print the variables---------------------------
#try:
#    print('The variable reverse_limit is : ', reverse_limit)
#except:
#    raise auotPMF_error('reverse_limit needs to be provided.')

######## step1 ########
if (options.step == 'prepare'):

  # About the program running
  print('The variable mode is : ', mode)
  print('The variable prmtop is : ', prmtop)
  print('The variable inpcrd is : ', inpcrd)
  print('The variable coord_type is : ', coord_type)
  print('The variable coord_atm1_num is : ', coord_atm1_num)
  print('The variable coord_atm2_num is : ', coord_atm2_num)
  print('The variable md_min_steps is : ', md_min_steps)
  print('The variable md_nvt_steps is : ', md_nvt_steps)
  print('The variable md_npt_steps is : ', md_npt_steps)
  print('The variable md_md_steps is : ', md_md_steps)
  print('The variable smd_forward_md_steps is : ', smd_forward_md_steps)
  print('The variable forward_limit is : ', forward_limit)
  print('The variable smd_reverse_md_steps is : ', smd_reverse_md_steps)
  print('The variable reverse_limit is : ', reverse_limit)
  print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
  ar=open("%s"%(ADDTIONAL_RST),"r")
  if ADDTIONAL_RST != "NONE":
     md_equi_RST=open("final_md_dis.RST","w")
     md_equi_RST.seek(0,2)
     md_equi_RST.write("# restraint\n")
     for line in ar:
       md_equi_RST.write(line)
     md_equi_RST.close()
  ar.close()

  avg_res_val,fram_num = freeMD(prmtop, inpcrd, md_min_steps, md_nvt_steps, md_npt_steps, md_md_steps,coord_atm1_num,coord_atm2_num,ADDTIONAL_RST)
  avg_res_val=round(float(avg_res_val),2)
  info=open("freemd.txt","w")
  print ("%s %s"%(avg_res_val,fram_num),file=info)
  info.close()
 #info=open("freemd.txt",'r')
 #for lines in info:
 #  lines=lines.split()
 #avg_res_val=round(float(lines[0]),2); fram_num=int(lines[1])

  smd_forward_MD(prmtop, inpcrd, smd_forward_md_steps, coord_atm1_num, coord_atm2_num,forward_limit,avg_res_val,fram_num,ADDTIONAL_RST)
  smd_reverse_MD(prmtop, inpcrd, smd_reverse_md_steps, coord_atm1_num, coord_atm2_num,reverse_limit,avg_res_val,fram_num,ADDTIONAL_RST)

if (options.step == 'sampling_NVT'):

  line_num=sum((1 for line in open('freemd.txt')))
  if line_num > 1:
    print ("freemd.txt has more than one line, terminate")
  else:
    info=open("freemd.txt","r")
    for line in info:
      line=line.split()
      avg_res_val=round(float(line[0]),2)
      fram_num=int(line[1])
    info.close()

    for space_number in range(1,space_num+1):
       us_mkdir_NVT(prmtop, inpcrd, avg_res_val, us_npt_steps, us_md_steps,us_window_space,space_number,slm_header)

    for restraint_number in range(1,restraint_num+1):
       us_restraint_setup(prmtop, inpcrd, coord_atm1_num, coord_atm2_num, us_window_restraint, restraint_number, forward_limit,ADDTIONAL_RST)


elif (options.step == 'adaptive_force'):
  path = os.getcwd() +'/'
  dir_list = next(os.walk('.'))[1]
  if 'log_files' in dir_list:
    dir_list.remove('log_files')
  dir_list = [float(i) for i in dir_list]
  dir_list.sort()
  for window in dir_list:
     window = round(float(window),2)
     workdir=path+'%s/'%(window)
     os.chdir(workdir)
     for optimize_number in range(1,optimize_num+1):
       ini = round(float(us_window_optimize[optimize_number][0]),2)
       fin = round(float(us_window_optimize[optimize_number][1]),2)
       increament = int(float(us_window_optimize[optimize_number][2]))
       center_deviation = float(center_deviation)
       if window >= ini and window < fin:
         os.system("cp ~/auto-pmf_equi-cpu/adaptive.py .")
         os.system("sed -i 's/WINDOW/%s/g' adaptive.py"%(window))
         os.system("sed -i 's/CENTER_DEVIATION/%s/g' adaptive.py"%(center_deviation))
         os.system("sed -i 's/INCREMENT/%s/g' adaptive.py"%(increament))
         os.system("sed -i 's/SLM_HEADER/%s/g' adaptive.py"%(slm_header))
         os.system("sed -i 's/=US_MD_STEPS/=%s/g' adaptive.py"%(us_md_steps))
         os.system("sed -i 's/=TEST_US_MD_STEPS/=%s/g' adaptive.py"%(test_us_md_steps))
         os.system("sed -i 's/PRMTOP/%s/g' adaptive.py"%(prmtop))
         os.system("python adaptive.py")
     os.chdir(path)

elif (options.step == 'adaptive_force2'):
  path = os.getcwd() +'/'
  dir_list = next(os.walk('.'))[1]
  if 'log_files' in dir_list:
    dir_list.remove('log_files')
  dir_list = [float(i) for i in dir_list]
  dir_list.sort()
  for window in dir_list:
     window = round(float(window),2)
     workdir=path+'%s/'%(window)
     os.chdir(workdir)
     for optimize_number in range(1,optimize_num+1):
       ini = round(float(us_window_optimize[optimize_number][0]),2)
       fin = round(float(us_window_optimize[optimize_number][1]),2)
       increament = int(float(us_window_optimize[optimize_number][2]))
       center_deviation = float(center_deviation)
       if window >= ini and window < fin:
         os.system("cp ~/auto-pmf_equi-cpu/adaptive2.py .")
         os.system("sed -i 's/WINDOW/%s/g' adaptive2.py"%(window))
         os.system("sed -i 's/CENTER_DEVIATION/%s/g' adaptive2.py"%(center_deviation))
         os.system("sed -i 's/INCREMENT/%s/g' adaptive2.py"%(increament))
         os.system("sed -i 's/SLM_HEADER/%s/g' adaptive2.py"%(slm_header))
         os.system("sed -i 's/=US_MD_STEPS/=3000000/g' adaptive2.py")
         os.system("sed -i 's/=TEST_US_MD_STEPS/=%s/g' adaptive2.py"%(test_us_md_steps))
         os.system("sed -i 's/PRMTOP/%s/g' adaptive2.py"%(prmtop))
         os.system("python adaptive2.py")
     os.chdir(path)



elif (options.step == 'check_force'):
  for optimize_number in range(1,optimize_num+1):
       check_force(us_window_optimize, optimize_number, us_window_restraint, center_deviation)

elif (options.step == 'check_force2'):
  for optimize_number in range(1,optimize_num+1):
       check_force2(us_window_optimize, optimize_number, us_window_restraint, center_deviation)

elif (options.step == 'check_force3'):
  for optimize_number in range(1,optimize_num+1):
       check_force3(us_window_optimize, optimize_number, us_window_restraint, center_deviation)

elif (options.step == 'check_wham'):
  for restraint_number in range(1,restraint_num+1):
    check_wham(us_window_restraint, restraint_number)

elif (options.step == 'result'):

  os.system("sh cp_log.sh")
  os.system("rm log_files/plot*py")
  os.system("ml GCC/6.4.0-2.28  OpenMPI/2.1.2 CGAL/4.11.1-Python-2.7.14")
  for space_number in range(1,space_num+1):
     plot(us_window_space,space_number,plot_grid)
  logdir=os.getcwd()+'/log_files/'
  os.chdir(logdir)
  os.system("sh %s_wham.sh"%(wham_window))
  os.system("sh %s_wham_1.sh"%(wham_window))
  os.system("sh %s_wham_2.sh"%(wham_window))

elif (options.step == 'write_wham'):

  os.system("rm -r log_files/ cp_log.sh metafile* *wham*.sh")
  os.system("mkdir log_files")

  for restraint_number in range(1,restraint_num+1):
    write_wham(us_window_restraint, restraint_number,forward_limit)

  line_num=sum((1 for line in open('metafile')))-1
  metafile=open('metafile','r')
  metafile_line=metafile.readlines()
  wham=open("%s_wham.sh"%(wham_window),"w")

  metafile_line_0 = metafile_line[0]
  metafile_line_f = metafile_line[line_num]

  tra,fir,trash=metafile_line_0.split()
  tra,las,trash=metafile_line_f.split()

  wham.write("~/wham/wham/wham %s %s %s %s 300 0 metafile %s-%s_pmf_%s.txt 5 5"%(fir,las,wham_window, wham_tol,fir,las,wham_window))
  wham.close()
  metafile.close()

  metafile=open('metafile','r')
  metafile_1=open("metafile_1","w")
  metafile_line=metafile.readlines()
  for i in range(1,line_num+1):
    metafile_1.write(metafile_line[i])
  metafile_1.close()
  wham_1=open("%s_wham_1.sh"%(wham_window),"w")

  metafile_line_0 = metafile_line[1]
  metafile_line_f = metafile_line[line_num]

  tra,fir,trash=metafile_line_0.split()
  tra,las,trash=metafile_line_f.split()

  wham_1.write("~/wham/wham/wham %s %s %s %s 300 0 metafile_1 %s-%s_pmf_%s.txt 5 5"%(fir,las,wham_window, wham_tol,fir,las,wham_window))
  wham_1.close()
  metafile.close()

  metafile=open('metafile','r')
  metafile_2=open("metafile_2","w")
  metafile_line=metafile.readlines()
  for i in range(2,line_num+1):
    metafile_2.write(metafile_line[i])
  metafile_2.close()
  wham_2=open("%s_wham_2.sh"%(wham_window),"w")

  metafile_line_0 = metafile_line[2]
  metafile_line_f = metafile_line[line_num]

  tra,fir,trash=metafile_line_0.split()
  tra,las,trash=metafile_line_f.split()

  wham_2.write("~/wham/wham/wham %s %s %s %s 300 0 metafile_2 %s-%s_pmf_%s.txt 5 5"%(fir,las,wham_window, wham_tol,fir,las,wham_window))
  wham_2.close()
  metafile.close()

  os.system("cp metafile* log_files/")
  os.system("cp *wham*.sh log_files/")

elif (options.step == 'us2_NVT'):
  line_num=sum((1 for line in open('freemd.txt')))
  if line_num > 1:
    print ("freemd.txt has more than one line, terminate")
  else:
    info=open("freemd.txt","r")
    for line in info:
      line=line.split()
      avg_res_val=round(float(line[0]),2)
      fram_num=int(line[1])
    info.close()

    for space_number in range(1,space_num+1):
      us2_NVT(prmtop, inpcrd, avg_res_val, us_npt_steps, us_md_steps,us_window_space,space_number,slm_header)

quit()
