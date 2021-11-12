#------------------------------------------------------------------------------
# This module is for making umbrella sampling folders and mdin files
#------------------------------------------------------------------------------
from __future__ import print_function
import numpy
import os
import os.path
import pandas as pd

def print_inputf(file_name, nxt, window_steps):

    md_mdf = open(file_name, 'w')

    if nxt in ['min','nvt','npt','md','snpt']:
        print("%s for US"%(nxt), file=md_mdf)

    print(" &cntrl", file=md_mdf)

    if nxt in ['min']:
        print("  imin=1,", file=md_mdf)
        print("  maxcyc=%d," %window_steps, file=md_mdf)
        ncyc = window_steps//2
        print("  ncyc=%d," %ncyc, file=md_mdf)
    elif nxt in ['nvt']:
        print("  imin=0,", file=md_mdf)
        print("  irest=0,", file=md_mdf)
        print("  ntx=1,", file=md_mdf)
        print("  ig=-1,", file=md_mdf)
        print("  nstlim=%d," %window_steps, file=md_mdf)
        print("  dt=0.002,", file=md_mdf)
    elif nxt in ['snpt','npt', 'md']:
        print("  imin=0,", file=md_mdf)
        print("  irest=1,", file=md_mdf)
        print("  ntx=5,", file=md_mdf)
        print("  nstlim=%d," %window_steps, file=md_mdf)
        print("  dt=0.002,", file=md_mdf)

    print("  cut=10.0,", file=md_mdf)
    print("  ntc=2,", file=md_mdf)
    print("  ntf=2,", file=md_mdf)

    if nxt in ['min']:
        print("  ntb=1,", file=md_mdf)
    elif nxt in ['nvt','md']:
        print("  ntb=1,", file=md_mdf)
        print("  ntt=3,", file=md_mdf)
        print("  gamma_ln=2.0,", file=md_mdf)
    elif nxt in ['npt','snpt']:
        print("  ntp=1,", file=md_mdf)
        print("  pres0=1.01325,", file=md_mdf)
        print("  taup = 5.0,", file=md_mdf)
        print("  ntt=3,", file=md_mdf)
        print("  gamma_ln=2.0,", file=md_mdf)

    if nxt in ['nvt']:
        print("  tempi=0.0,", file=md_mdf)
        print("  temp0=300.0,", file=md_mdf)
    elif nxt in ['snpt','npt','md']:
        print("  tempi=300.0,", file=md_mdf)
        print("  temp0=300.0,", file=md_mdf)

    print("  ntpr=5000,", file=md_mdf)
    print("  ntwr=5000,", file=md_mdf)

    if nxt in ['min']:
        print("  ntwx=2000,", file=md_mdf)
    elif nxt in ['snpt','nvt','npt','md']:
        ntwx = window_steps//10
        print("  ntwx=%d," %ntwx, file=md_mdf)
        print("  ntwv=-1,", file=md_mdf)

    print("  ioutfm=1,", file=md_mdf)
    print("  iwrap=0,", file=md_mdf)
    print(" ", file=md_mdf)
    print("  nmropt=1,", file=md_mdf)
    print("/", file=md_mdf)

    if nxt == 'nvt':
        istep2_1 = int(window_steps)-10000
        istep1_2 = istep2_1 + 1
        print("&wt TYPE='TEMP0', istep1=0, istep2=%s, value1=0.0, value2=300.0 /"%(istep2_1),file=md_mdf) 
        print("&wt TYPE='TEMP0', istep1=%s, istep2=%s, value1=300.0, value2=300.0 /"%(istep1_2,window_steps),file=md_mdf)
        print("&wt TYPE='DUMPFREQ', istep1=10000, /",file=md_mdf)
        print("&wt TYPE='END', /",file=md_mdf)
        print("DISANG=us_dis.RST",file=md_mdf)
        print("DUMPAVE=%s_us.log"%(nxt),file=md_mdf)
    elif nxt in ['min','npt','snpt']:
        print("&wt TYPE='DUMPFREQ', istep1=10000, /",file=md_mdf)
        print("&wt TYPE='END', /",file=md_mdf)
        print("DISANG=us_dis.RST",file=md_mdf)
        print("DUMPAVE=%s_us.log"%(nxt),file=md_mdf)
    elif nxt in ['md']:
        print("&wt TYPE='DUMPFREQ', istep1=500, /",file=md_mdf)
        print("&wt TYPE='END', /",file=md_mdf)
        print("DISANG=us_dis.RST",file=md_mdf)
        print("DUMPAVE=%s_us.log"%(nxt),file=md_mdf)

    md_mdf.close()

def us_mkdir(prmtop, inpcrd, avg_res_val, us_min_steps, us_nvt_steps, us_npt_steps, us_md_steps,us_window_space,space_number,slm_header):

    print("**** making US directory for space %s..."%(space_number))
    
    start = round(float(us_window_space[space_number][0]),2)
    end = round(float(us_window_space[space_number][1]),2)
    interval = round(float(us_window_space[space_number][2]),2)
    f_window_num = int((end-avg_res_val)/interval)
    r_window_num = int((avg_res_val-start)/interval)
    path = os.getcwd()
    
    for i in range(0,r_window_num+1):
       window = round(float(avg_res_val - i*interval),2)
       workdir = path + '/%s/'%(window)
       if not os.path.isdir(workdir):
          os.system("mkdir %s"%(window))
       os.chdir(workdir)

       dat=pd.read_csv('../smd_reverse_md_tailed.txt', delim_whitespace=True, header=0,engine='python')
       dat.columns = ["num", "value"]
       index = abs(dat['value'] - window).idxmin()
       smd_fram_num=dat['num'][index]
       ptrajin = open("ptraj.in","w")
       print("trajin ../smd_reverse_md_center.netcdf %s %s"%(smd_fram_num,smd_fram_num),file=ptrajin)
       print("trajout start.rst restart",file=ptrajin)
       ptrajin.close()
       os.system("cp ../%s ."%(prmtop))
       os.system("cpptraj %s < ptraj.in > out"%(prmtop)) 

       #mdin
       print_inputf('us_min.in', 'min', us_min_steps)
       print_inputf('us_nvt.in', 'nvt', us_nvt_steps)
       print_inputf('us_npt.in', 'npt', us_npt_steps)
       print_inputf('us_md.in', 'md', us_md_steps)
       print_inputf('us_snpt.in', 'snpt', 50000)

       slm = open("command",'w')
       print("pmemd.cuda -O -i us_min.in -o us_min.out -p %s -c start.rst -r us_min.rst -x us_min.netcdf -ref start.rst" %(prmtop),file=slm)
       print("pmemd.cuda -O -i us_nvt.in -o us_nvt.out -p %s -c us_min.rst -r us_nvt.rst -x us_nvt.netcdf -ref us_min.rst" %(prmtop),file=slm)
       print("mpirun -np 4 pmemd.MPI -O -i us_snpt.in -o us_snpt.out -p %s -c us_nvt.rst -r us_snpt.rst -x us_snpt.netcdf -ref us_nvt.rst" %(prmtop),file=slm)
       print("pmemd.cuda -O -i us_npt.in -o us_npt.out -p %s -c us_snpt.rst -r us_npt.rst -x us_npt.netcdf -ref us_snpt.rst" %(prmtop),file=slm)
       print("pmemd.cuda -O -i us_md.in -o us_md.out -p %s -c us_npt.rst -r us_md.rst -x us_md.netcdf -ref us_npt.rst" %(prmtop),file=slm)
       print("if grep 'Total wall time' us_md.out;then",file=slm)
       print("   echo 'all done'",file=slm)
       print("else",file=slm)
       print("   sbatch %s.slm"%(window),file=slm)
       print("fi", file=slm)
       slm.close()
       os.system("cp ../%s ."%(slm_header))
       os.system("cat %s command > %s.slm"%(slm_header,window))
       os.system("sed -i 's/XXXXXXXXX/%s/g' %s.slm"%(window,window))
       os.chdir(path)

    for i in range(1,f_window_num+1):
       window = round(float(avg_res_val + i*interval),2)
       workdir = path + '/%s/'%(window)
       if not os.path.isdir(workdir):
          os.system("mkdir %s"%(window))
       os.chdir(workdir)

       dat=pd.read_csv('../smd_forward_md_tailed.txt', delim_whitespace=True, header=0,engine='python')
       dat.columns = ["num", "value"]
       index = abs(dat['value'] - window).idxmin()
       smd_fram_num=dat['num'][index]
       ptrajin = open("ptraj.in","w")
       print("trajin ../smd_forward_md_center.netcdf %s %s"%(smd_fram_num,smd_fram_num),file=ptrajin)
       print("trajout start.rst restart",file=ptrajin)
       ptrajin.close()
       os.system("cp ../%s ."%(prmtop))
       os.system("cpptraj %s < ptraj.in > out"%(prmtop)) 

       #mdin
       print_inputf('us_min.in', 'min', us_min_steps)
       print_inputf('us_nvt.in', 'nvt', us_nvt_steps)
       print_inputf('us_npt.in', 'npt', us_npt_steps)
       print_inputf('us_md.in', 'md', us_md_steps)
       print_inputf('us_snpt.in', 'snpt', 50000)

       slm = open("command",'w')
       print("pmemd.cuda -O -i us_min.in -o us_min.out -p %s -c start.rst -r us_min.rst -x us_min.netcdf -ref start.rst" %(prmtop),file=slm)
       print("pmemd.cuda -O -i us_nvt.in -o us_nvt.out -p %s -c us_min.rst -r us_nvt.rst -x us_nvt.netcdf -ref us_min.rst" %(prmtop),file=slm)
       print("mpirun -np 4 pmemd.MPI -O -i us_snpt.in -o us_snpt.out -p %s -c us_nvt.rst -r us_snpt.rst -x us_snpt.netcdf -ref us_nvt.rst" %(prmtop),file=slm)
       print("pmemd.cuda -O -i us_npt.in -o us_npt.out -p %s -c us_snpt.rst -r us_npt.rst -x us_npt.netcdf -ref us_snpt.rst" %(prmtop),file=slm)
       print("pmemd.cuda -O -i us_md.in -o us_md.out -p %s -c us_npt.rst -r us_md.rst -x us_md.netcdf -ref us_npt.rst" %(prmtop),file=slm)
       print("if grep 'Total wall time' us_md.out;then",file=slm)
       print("   echo 'all done'",file=slm)
       print("else",file=slm)
       print("   sbatch %s.slm"%(window),file=slm)
       print("fi", file=slm)
       slm.close()
       os.system("cp ../%s ."%(slm_header))
       os.system("cat %s command > %s.slm"%(slm_header,window))
       os.system("sed -i 's/XXXXXXXXX/%s/g' %s.slm"%(window,window))
       os.chdir(path)


def us_restraint_setup(prmtop, inpcrd, coord_atm1_num, coord_atm2_num, us_window_restraint, restraint_number,forward_limit):

    print("**** writing RST files for restraint space %s..."%(restraint_number))
    
    start = round(float( us_window_restraint[restraint_number][0]),2)
    end = round(float( us_window_restraint[restraint_number][1]),2)
    #print (start, end)
    restraint_const = round(float( us_window_restraint[restraint_number][2]),2)
    path = os.getcwd()
    os.chdir(path)

    dir_list = next(os.walk('.'))[1]
    if 'log_files' in dir_list:
      dir_list.remove('log_files')
    dir_list = [float(i) for i in dir_list]
    dir_list.sort()
    #print (dir_list)
    for window in dir_list:
       window = round(float(window),2)
       if window >= start and window < end:
          workdir = path + '/%s/'%(window)
          os.chdir(workdir)

          f1=open('us_dis.RST','w')
          print("# restraint",file=f1)
          print(" &rst  iat=-1, -1, r1=0.0, r2=%s, r3=%s, r4=100., rk2=%s, rk3=%s,igr1=%s,igr2=%s,/"%(window,window,restraint_const,restraint_const,coord_atm1_num,coord_atm2_num),file=f1)
          f1.close()
          print (window,restraint_const)
          os.system("sbatch %s.slm"%(window))
          os.chdir(path)
       elif window == end and end == round(float(forward_limit),2):
          workdir = path + '/%s/'%(window)
          os.chdir(workdir)

          f1=open('us_dis.RST','w')
          print("# restraint",file=f1)
          print(" &rst  iat=-1, -1, r1=0.0, r2=%s, r3=%s, r4=100., rk2=%s, rk3=%s,igr1=%s,igr2=%s,/"%(window,window,restraint_const,restraint_const,coord_atm1_num,coord_atm2_num),file=f1)
          f1.close()
          print (window,restraint_const)
          os.system("sbatch %s.slm"%(window))
          os.chdir(path)
