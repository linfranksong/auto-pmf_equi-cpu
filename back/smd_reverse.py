#------------------------------------------------------------------------------
# This module is for average restraint value calculation
#------------------------------------------------------------------------------
from __future__ import print_function
import numpy
import os
import pandas as pd

def print_inputf(file_name, nxt, window_steps):

    md_mdf = open(file_name, 'w')
    print("%s for smd"%(nxt), file=md_mdf)
    print(" &cntrl", file=md_mdf)
    print("  imin=0,", file=md_mdf)
    print("  irest=1,", file=md_mdf)
    print("  ntx=5,", file=md_mdf)
    print("  nstlim=%d," %window_steps, file=md_mdf)
    print("  dt=0.001,", file=md_mdf)
    print("  cut=10.0,", file=md_mdf)
    print("  ntc=2,", file=md_mdf)
    print("  ntf=2,", file=md_mdf)
    print("  ntp=1,", file=md_mdf)
    print("  pres0=1.01325,", file=md_mdf)
    print("  taup = 5.0,", file=md_mdf)
    print("  ntt=3,", file=md_mdf)
    print("  gamma_ln=2.0,", file=md_mdf)
    print("  tempi=300.0,", file=md_mdf)
    print("  temp0=300.0,", file=md_mdf)
    print("  ntpr=5000,", file=md_mdf)
    print("  ntwr=5000,", file=md_mdf)
    ntwx = 100
    print("  ntwx=%d," %ntwx, file=md_mdf)
    print("  ntwv=0,", file=md_mdf)
    print("  ioutfm=1,", file=md_mdf)
    print("  iwrap=0,", file=md_mdf)
    print("  nmropt=1,", file=md_mdf)
    print("  jar=1,",file=md_mdf)
    print(" /", file=md_mdf)
    print(" &wt TYPE='DUMPFREQ', istep1=100, /",file=md_mdf)
    print(" &wt TYPE='END', /",file=md_mdf)
    print("DISANG=smd_reverse_dis.RST",file=md_mdf)
    print("DUMPAVE=smd_reverse_%s.log"%(nxt),file=md_mdf)
    md_mdf.close()

def smd_reverse_MD(prmtop, inpcrd, smd_reverse_md_steps, coord_atm1_num, coord_atm2_num,reverse_limit,aveg_res_val,fram_num):

    f1=open('equi_dis.RST','w')
    print("# restraint",file=f1)
    print(" &rst  iat=-1, -1, r1=0.0, r2=%s, r3=%s, r4=100., rk2=100.0, rk3=100.0,igr1=%s,igr2=%s,/"%(aveg_res_val,aveg_res_val,coord_atm1_num,coord_atm2_num),file=f1)
    f1.close()

    f2=open('smd_reverse_dis.RST','w')
    print("# restraint",file=f2)
    print(" &rst  iat=-1, -1, r2=%s, rk2=1000, r2a=%s,igr1=%s,igr2=%s,/"%(aveg_res_val,reverse_limit,coord_atm1_num,coord_atm2_num),file=f2)
    f2.close()

    smd_reverse_md_steps = int((-float(reverse_limit)+float(aveg_res_val))*500000)

    #smd MD simulation
    print("****Perform smd reverse MD simulation ...")
    print_inputf('smd_reverse_md.in', 'md', smd_reverse_md_steps)
    os.system("pmemd.cuda -O -i smd_reverse_md.in -o smd_reverse_md.out -p %s -c md_md_center_%s.rst -r smd_reverse_md.rst -x smd_reverse_md.netcdf -ref md_md_center_%s.rst" %(prmtop,fram_num,fram_num))

    #Cpptraj input file
    centerf = open('smd_reverse_center.in', 'w')
    print("trajin smd_reverse_md.netcdf", file=centerf)
    print("autoimage", file=centerf)
    print("trajout smd_reverse_md_center.netcdf netcdf", file=centerf)
    centerf.close()
    os.system("cpptraj -p %s -i smd_reverse_center.in > center.out" %prmtop)

    cpptrajf = open('smd_reverse_md_cpptraj.in', 'w')
    print("trajin smd_reverse_md_center.netcdf", file=cpptrajf)
    print("distance @%s @%s out smd_reverse_md.txt"%(coord_atm1_num,coord_atm2_num), file=cpptrajf)
    cpptrajf.close()
    os.system("cpptraj -p %s -i smd_reverse_md_cpptraj.in > cpptraj.out" %prmtop)
    os.system("tail -n +2 smd_reverse_md.txt > smd_reverse_md_tailed.txt")
