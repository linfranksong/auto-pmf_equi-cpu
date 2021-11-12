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

    if nxt in ['md2']:
        print("%s for US"%(nxt), file=md_mdf)

    print(" &cntrl", file=md_mdf)

    if nxt in ['md2']:
        print("  imin=0,", file=md_mdf)
        print("  irest=1,", file=md_mdf)
        print("  ntx=5,", file=md_mdf)
        print("  nstlim=%d," %window_steps, file=md_mdf)
        print("  dt=0.002,", file=md_mdf)

    print("  cut=10.0,", file=md_mdf)
    print("  ntc=2,", file=md_mdf)
    print("  ntf=2,", file=md_mdf)

    if nxt in ['md2']:
        print("  ntb=2,", file=md_mdf)
        print("  ntp=1,", file=md_mdf)
        print("  pres0=1.01325,", file=md_mdf)
        print("  taup = 5.0,", file=md_mdf)
        print("  ntt=3,", file=md_mdf)
        print("  gamma_ln=2.0,", file=md_mdf)
        print("  tempi=300.0,", file=md_mdf)
        print("  temp0=300.0,", file=md_mdf)

    print("  ntpr=5000,", file=md_mdf)
    print("  ntwr=5000,", file=md_mdf)

    if nxt in ['md2']:
        ntwx = window_steps//10
        print("  ntwx=%d," %ntwx, file=md_mdf)
        print("  ntwv=-1,", file=md_mdf)

    print("  ioutfm=1,", file=md_mdf)
    print("  iwrap=0,", file=md_mdf)
    print(" ", file=md_mdf)
    print("  nmropt=1,", file=md_mdf)
    print("/", file=md_mdf)

    if nxt in ['md2']:
        print("&wt TYPE='DUMPFREQ', istep1=500, /",file=md_mdf)
        print("&wt TYPE='END', /",file=md_mdf)
        print("DISANG=us_dis.RST",file=md_mdf)
        print("DUMPAVE=%s_us2.log"%(nxt),file=md_mdf)

    md_mdf.close()

def us2(prmtop, inpcrd, avg_res_val, us_min_steps, us_nvt_steps, us_npt_steps, us_md_steps,us_window_space,space_number,slm_header):

    start = round(float(us_window_space[space_number][0]),2)
    end = round(float(us_window_space[space_number][1]),2)
    interval = round(float(us_window_space[space_number][2]),2)
    f_window_num = int((end-avg_res_val)/interval)
    r_window_num = int((avg_res_val-start)/interval)
    path = os.getcwd()
    
    for i in range(0,r_window_num+1):
       window = round(float(avg_res_val - i*interval),2)
       workdir = path + '/%s/'%(window)
       os.chdir(workdir)

       print_inputf('us_md2.in', 'md2', 3000000)

       slm = open("command",'w')
       print("pmemd.cuda -O -i us_md2.in -o us_md2.out -p %s -c us_md.rst -r us_md2.rst -x us_md2.netcdf -ref us_md.rst" %(prmtop),file=slm)
       print("if grep 'Total wall time' us_md2.out;then",file=slm)
       print("   echo 'all done'",file=slm)
       print("else",file=slm)
       print("   sbatch %s2.slm"%(window),file=slm)
       print("fi", file=slm)
       slm.close()
       os.system("cp ../%s ."%(slm_header))
       os.system("cat %s command > %s2.slm"%(slm_header,window))
       os.system("sed -i 's/XXXXXXXXX/%s/g' %s2.slm"%(window,window))
       os.system("sbatch %s2.slm"%(window))
       os.chdir(path)

    for i in range(1,f_window_num+1):
       window = round(float(avg_res_val + i*interval),2)
       workdir = path + '/%s/'%(window)
       os.chdir(workdir)

       print_inputf('us_md2.in', 'md2', 3000000)

       slm = open("command",'w')
       print("pmemd.cuda -O -i us_md2.in -o us_md2.out -p %s -c us_md.rst -r us_md2.rst -x us_md2.netcdf -ref us_md.rst" %(prmtop),file=slm)
       print("if grep 'Total wall time' us_md2.out;then",file=slm)
       print("   echo 'all done'",file=slm)
       print("else",file=slm)
       print("   sbatch %s2.slm"%(window),file=slm)
       print("fi", file=slm)
       slm.close()
       os.system("cp ../%s ."%(slm_header))
       os.system("cat %s command > %s2.slm"%(slm_header,window))
       os.system("sed -i 's/XXXXXXXXX/%s/g' %s2.slm"%(window,window))
       os.system("sbatch %s2.slm"%(window))
       os.chdir(path)
