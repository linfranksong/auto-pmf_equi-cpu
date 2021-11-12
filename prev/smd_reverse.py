#------------------------------------------------------------------------------
# This module is for average restraint value calculation
#------------------------------------------------------------------------------
from __future__ import print_function
import numpy
import os
import pandas as pd

def print_inputf(file_name, nxt, window_steps):

    md_mdf = open(file_name, 'w')

    if nxt in ['min1','min2','min3','min4','min5','nvt','npt','md','snpt']:
        print("%s for smd equilibrate MD"%(nxt), file=md_mdf)

    print(" &cntrl", file=md_mdf)

    if nxt in ['min1','min2','min3','min4','min5']:
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
        print("  dt=0.001,", file=md_mdf)
    elif nxt in ['snpt','npt','md']:
        print("  imin=0,", file=md_mdf)
        print("  irest=1,", file=md_mdf)
        print("  ntx=5,", file=md_mdf)
        print("  nstlim=%d," %window_steps, file=md_mdf)
        print("  dt=0.001,", file=md_mdf)

    print("  cut=10.0,", file=md_mdf)
    print("  ntc=2,", file=md_mdf)
    print("  ntf=2,", file=md_mdf)

    if nxt in ['min1','min2','min3','min4','min5']:
        print("  ntb=1,", file=md_mdf)
    elif nxt == 'nvt':
        print("  ntb=1,", file=md_mdf)
        print("  ntt=3,", file=md_mdf)
        print("  gamma_ln=2.0,", file=md_mdf)
        print("  tempi=0.0,", file=md_mdf)
        print("  temp0=300.0,", file=md_mdf)
    elif nxt in ['snpt','npt', 'md']:
        print("  ntp=1,", file=md_mdf)
        print("  pres0=1.01325,", file=md_mdf)
        print("  taup = 5.0,", file=md_mdf)
        print("  ntt=3,", file=md_mdf)
        print("  gamma_ln=2.0,", file=md_mdf)
        print("  tempi=300.0,", file=md_mdf)
        print("  temp0=300.0,", file=md_mdf)

    print("  ntpr=5000,", file=md_mdf)
    print("  ntwr=5000,", file=md_mdf)

    if nxt == 'md':
        ntwx = 100
        print("  ntwx=%d," %ntwx, file=md_mdf)
    elif nxt in ['min1','min2','min3','min4','min5']:
        print("  ntwx=2000,", file=md_mdf)
    elif nxt in ['snpt','nvt','npt','snpt']:
        ntwx = window_steps//10
        print("  ntwx=%d," %ntwx, file=md_mdf)

    if nxt not in ['min1','min2','min3','min4','min5']:
        print("  ntwv=-1,", file=md_mdf)

    print("  ioutfm=1,", file=md_mdf)
    print("  iwrap=0,", file=md_mdf)
    print(" ", file=md_mdf)
    print("  nmropt=1,", file=md_mdf)


    if nxt == 'min1':
        print("  ntr=1, restraintmask='!:WAT', restraint_wt=200,", file=md_mdf)
    elif nxt == 'min2':
        print("  ntr=1, restraintmask='!:WAT & !@H=', restraint_wt=200,", file=md_mdf)
    elif nxt == 'min3':
        print("  ntr=1, restraintmask='!:WAT & @C,O,CA,N', restraint_wt=200,", file=md_mdf)
    elif nxt == 'min4':
        print("  ntr=1, restraintmask='!:WAT & @C,O', restraint_wt=200,", file=md_mdf)
    elif nxt == 'md':
        print("  jar=1,",file=md_mdf)

    print("/", file=md_mdf)

    if nxt in ['min1','min2','min3','min4','min5','npt','snpt']:
        print("&wt TYPE='DUMPFREQ', istep1=10000, /",file=md_mdf)
        print("&wt TYPE='END', /",file=md_mdf)
        print("DISANG=equi_dis.RST",file=md_mdf)
        print("DUMPAVE=%s_smd_reverse.log"%(nxt),file=md_mdf)
    elif nxt == 'nvt':
        istep2_1 = int(window_steps)-10000
        istep1_2 = istep2_1 + 1
        print("&wt TYPE='TEMP0', istep1=0, istep2=%s, value1=0.0, value2=300.0 /"%(istep2_1),file=md_mdf) 
        print("&wt TYPE='TEMP0', istep1=%s, istep2=%s, value1=300.0, value2=300.0 /"%(istep1_2,window_steps),file=md_mdf)
        print("&wt TYPE='DUMPFREQ', istep1=10000, /",file=md_mdf)
        print("&wt TYPE='END', /",file=md_mdf)
        print("DISANG=equi_dis.RST",file=md_mdf)
        print("DUMPAVE=%s_smd_reverse.log"%(nxt),file=md_mdf)
    elif nxt == 'md':
        print("&wt TYPE='DUMPFREQ', istep1=10000, /",file=md_mdf)
        print("&wt TYPE='END', /",file=md_mdf)
        print("DISANG=smd_reverse_dis.RST",file=md_mdf)
        print("DUMPAVE=smd_reverse_%s.log"%(nxt),file=md_mdf)

    md_mdf.close()

def smd_reverse_MD(prmtop, inpcrd, smd_reverse_min_steps, smd_reverse_nvt_steps, smd_reverse_npt_steps, smd_reverse_md_steps, coord_atm1_num, coord_atm2_num,reverse_limit,aveg_res_val,fram_num):

    f1=open('equi_dis.RST','w')
    print("# restraint",file=f1)
    print(" &rst  iat=-1, -1, r1=0.0, r2=%s, r3=%s, r4=100., rk2=100.0, rk3=100.0,igr1=%s,igr2=%s,/"%(aveg_res_val,aveg_res_val,coord_atm1_num,coord_atm2_num),file=f1)
    f1.close()

    f2=open('smd_reverse_dis.RST','w')
    print("# restraint",file=f2)
    print(" &rst  iat=-1, -1, r2=%s, rk2=1000, r2a=%s,igr1=%s,igr2=%s,/"%(aveg_res_val,reverse_limit,coord_atm1_num,coord_atm2_num),file=f2)
    f2.close()

    smd_reverse_md_steps = int((float(aveg_res_val)-float(reverse_limit))*1000000)

    #smd MD simulation
    print("****Perform smd reverse MD simulation ...")

    #MIN
    print("Perform smd_reverse_min1 %d steps..." %smd_reverse_min_steps)
    print_inputf('smd_reverse_min1.in', 'min1', smd_reverse_min_steps)
    os.system("pmemd.cuda -O -i smd_reverse_min1.in -o smd_reverse_min1.out -p %s -c md_md_center_%s.rst -r smd_reverse_min1.rst -x smd_reverse_min1.netcdf -ref md_md_center_%s.rst" %(prmtop,fram_num,fram_num))

    print("Perform smd_reverse_min2 %d steps..." %smd_reverse_min_steps)
    print_inputf('smd_reverse_min2.in', 'min2', smd_reverse_min_steps)
    os.system("pmemd.cuda -O -i smd_reverse_min2.in -o smd_reverse_min2.out -p %s -c smd_reverse_min1.rst -r smd_reverse_min2.rst -x smd_reverse_min2.netcdf -ref smd_reverse_min1.rst" %(prmtop))

    print("Perform smd_reverse_min3 %d steps..." %smd_reverse_min_steps)
    print_inputf('smd_reverse_min3.in', 'min3', smd_reverse_min_steps)
    os.system("pmemd.cuda -O -i smd_reverse_min3.in -o smd_reverse_min3.out -p %s -c smd_reverse_min2.rst -r smd_reverse_min3.rst -x smd_reverse_min3.netcdf -ref smd_reverse_min2.rst" %(prmtop))

    print("Perform smd_reverse_min4 %d steps..." %smd_reverse_min_steps)
    print_inputf('smd_reverse_min4.in', 'min4', smd_reverse_min_steps)
    os.system("pmemd.cuda -O -i smd_reverse_min4.in -o smd_reverse_min4.out -p %s -c smd_reverse_min3.rst -r smd_reverse_min4.rst -x smd_reverse_min4.netcdf -ref smd_reverse_min3.rst" %(prmtop))

    print("Perform smd_reverse_min5 %d steps..." %smd_reverse_min_steps)
    print_inputf('smd_reverse_min5.in', 'min5', smd_reverse_min_steps)
    os.system("pmemd.cuda -O -i smd_reverse_min5.in -o smd_reverse_min5.out -p %s -c smd_reverse_min4.rst -r smd_reverse_min5.rst -x smd_reverse_min5.netcdf -ref smd_reverse_min4.rst" %(prmtop))

    #NVT
    print("Perform smd_reverse_nvt %d steps..." %smd_reverse_nvt_steps)
    print_inputf('smd_reverse_nvt.in', 'nvt', smd_reverse_nvt_steps)
    os.system("pmemd.cuda -O -i smd_reverse_nvt.in -o smd_reverse_nvt.out -p %s -c smd_reverse_min5.rst -r smd_reverse_nvt.rst -x smd_reverse_nvt.netcdf -ref smd_reverse_min5.rst" %(prmtop))

    #SNPT
    print("Perform smd_reverse_snpt 50000 ...")
    print_inputf('smd_reverse_snpt.in', 'snpt', 50000)
    os.system("mpirun -np 4 pmemd.MPI -O -i smd_reverse_snpt.in -o smd_reverse_snpt.out -p %s -c smd_reverse_nvt.rst -r smd_reverse_snpt.rst -x smd_reverse_snpt.netcdf -ref smd_reverse_nvt.rst" %(prmtop))

    #NPT
    print("Perform smd_reverse_npt %d steps..." %smd_reverse_npt_steps)
    print_inputf('smd_reverse_npt.in', 'npt', smd_reverse_npt_steps)
    os.system("pmemd.cuda -O -i smd_reverse_npt.in -o smd_reverse_npt.out -p %s -c smd_reverse_snpt.rst -r smd_reverse_npt.rst -x smd_reverse_npt.netcdf -ref smd_reverse_snpt.rst" %(prmtop))

    #MD
    print("Perform smd_reverse_md %d steps..." %smd_reverse_md_steps)
    print_inputf('smd_reverse_md.in', 'md', smd_reverse_md_steps)
    os.system("pmemd.cuda -O -i smd_reverse_md.in -o smd_reverse_md.out -p %s -c smd_reverse_npt.rst -r smd_reverse_md.rst -x smd_reverse_md.netcdf -ref smd_reverse_npt.rst" %(prmtop))

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
