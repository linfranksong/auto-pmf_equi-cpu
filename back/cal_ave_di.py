#------------------------------------------------------------------------------
# This module is for average restraint value calculation
#------------------------------------------------------------------------------
from __future__ import print_function
import numpy
import os
import pandas as pd

def print_md_inputf(file_name, nxt, window_steps, ADDTIONAL_RST):

    md_mdf = open(file_name, 'w')

    if nxt in ['min1','min2','min3','min4','min5','nvt','npt','md','snpt']:
        print("%s for free MD"%(nxt), file=md_mdf)

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
    if ADDTIONAL_RST != "NONE":
       print("  nmropt=1,", file=md_mdf)
    if nxt in ['min1','min2','min3','min4','min5']:
        print("  ntb=1,", file=md_mdf)
    elif nxt == 'nvt':
        print("  ntb=1,", file=md_mdf)
        print("  ntt=3,", file=md_mdf)
        print("  gamma_ln=2.0,", file=md_mdf)
        print("  tempi=2.0,", file=md_mdf)
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
        ntwx = window_steps//100
        print("  ntwx=%d," %ntwx, file=md_mdf)
        print("  ntwv=-1,", file=md_mdf)
    elif nxt in ['min1','min2','min3','min4','min5']:
        print("  ntwx=2000,", file=md_mdf)
    elif nxt in ['nvt','npt','snpt']:
        ntwx = window_steps//10
        print("  ntwx=%d," %ntwx, file=md_mdf)

    print("  ioutfm=1,", file=md_mdf)
    print("  iwrap=0,", file=md_mdf)
    print(" ", file=md_mdf)


    if nxt == 'min1':
        print("  ntr=1, restraintmask='!:WAT', restraint_wt=200,", file=md_mdf)
    elif nxt == 'min2':
        print("  ntr=1, restraintmask='!:WAT & !@H=', restraint_wt=200,", file=md_mdf)
    elif nxt == 'min3':
        print("  ntr=1, restraintmask='!:WAT & @C,O,CA,N', restraint_wt=200,", file=md_mdf)
    elif nxt == 'min4':
        print("  ntr=1, restraintmask='!:WAT & @C,O', restraint_wt=200,", file=md_mdf)
    elif nxt == 'nvt':
        print("  nmropt=1,", file=md_mdf)

    print(" /", file=md_mdf)
    if nxt == 'nvt':
        istep2_1 = int(window_steps)-10000
        istep1_2 = istep2_1 + 1
        print(" &wt TYPE='TEMP0', istep1=0, istep2=%s, value1=2.0, value2=300.0 /"%(istep2_1),file=md_mdf) 
        print(" &wt TYPE='TEMP0', istep1=%s, istep2=%s, value1=300.0, value2=300.0 /"%(istep1_2,window_steps),file=md_mdf)
    if ADDTIONAL_RST != "NONE":
        print("&wt TYPE='DUMPFREQ', istep1=10000, /",file=md_mdf)
        print("&wt TYPE='END', /",file=md_mdf)
        print("DISANG=final_md_dis.RST",file=md_mdf)
        print("DUMPAVE=%s_md.log"%(nxt),file=md_mdf)

    md_mdf.close()

def cal(restr_name):
  new_f=open("%s_sort.txt"%(restr_name),"w")
  old_f=open("%s.txt"%(restr_name),"r")
  for line in old_f:
    i,j=line.split()
    new_f.write("%s,%s\n"%(i,j))
  old_f.close()
  new_f.close()

  data=pd.read_csv('%s_sort.txt'%(restr_name), sep=',',header=0,engine='python')
  data.columns = ["num", "value"]
  avg=data["value"].mean()
  return avg

def freeMD(prmtop, inpcrd, md_min_steps, md_nvt_steps, md_npt_steps, md_md_steps,coord_atm1_num,coord_atm2_num, ADDTIONAL_RST):

    #free MD simulation
    print("****Perform free MD simulation ...")

    freemd=open('freemd.slm',"w")
    freemd.seek(0,2)

    print("Perform md_min1 %d steps..." %md_min_steps)
    print_md_inputf('md_min1.in', 'min1', md_min_steps,ADDTIONAL_RST)
    os.system("pmemd.cuda -O -i md_min1.in -o md_min1.out -p %s -c %s -r md_min1.rst -x md_min1.netcdf -ref %s" %(prmtop, inpcrd,inpcrd))
    freemd.write("pmemd.cuda -O -i md_min1.in -o md_min1.out -p %s -c %s -r md_min1.rst -x md_min1.netcdf -ref %s\n"%(prmtop, inpcrd,inpcrd))

    print("Perform md_min2 %d steps..." %md_min_steps)
    print_md_inputf('md_min2.in', 'min2', md_min_steps,ADDTIONAL_RST)
    os.system("pmemd.cuda -O -i md_min2.in -o md_min2.out -p %s -c md_min1.rst -r md_min2.rst -x md_min2.netcdf -ref md_min1.rst" %(prmtop))
    freemd.write("pmemd.cuda -O -i md_min2.in -o md_min2.out -p %s -c md_min1.rst -r md_min2.rst -x md_min2.netcdf -ref md_min1.rst\n" %(prmtop))

    print("Perform md_min3 %d steps..." %md_min_steps)
    print_md_inputf('md_min3.in', 'min3', md_min_steps,ADDTIONAL_RST)
    os.system("pmemd.cuda -O -i md_min3.in -o md_min3.out -p %s -c md_min2.rst -r md_min3.rst -x md_min3.netcdf -ref md_min2.rst" %(prmtop))
    freemd.write("pmemd.cuda -O -i md_min3.in -o md_min3.out -p %s -c md_min2.rst -r md_min3.rst -x md_min3.netcdf -ref md_min2.rst\n" %(prmtop))

    print("Perform md_min4 %d steps..." %md_min_steps)
    print_md_inputf('md_min4.in', 'min4', md_min_steps,ADDTIONAL_RST)
    os.system("pmemd.cuda -O -i md_min4.in -o md_min4.out -p %s -c md_min3.rst -r md_min4.rst -x md_min4.netcdf -ref md_min3.rst" %(prmtop))
    freemd.write("pmemd.cuda -O -i md_min4.in -o md_min4.out -p %s -c md_min3.rst -r md_min4.rst -x md_min4.netcdf -ref md_min3.rst\n" %(prmtop))

    print("Perform md_min5 %d steps..." %md_min_steps)
    print_md_inputf('md_min5.in', 'min5', md_min_steps,ADDTIONAL_RST)
    os.system("pmemd.cuda -O -i md_min5.in -o md_min5.out -p %s -c md_min4.rst -r md_min5.rst -x md_min5.netcdf -ref md_min4.rst" %(prmtop))
    freemd.write("pmemd.cuda -O -i md_min5.in -o md_min5.out -p %s -c md_min4.rst -r md_min5.rst -x md_min5.netcdf -ref md_min4.rst\n" %(prmtop))

    #NVT
    print("Perform md_nvt %d steps..." %md_nvt_steps)
    print_md_inputf('md_nvt.in', 'nvt', md_nvt_steps,ADDTIONAL_RST)
    os.system("pmemd.cuda -O -i md_nvt.in -o md_nvt.out -p %s -c md_min5.rst -r md_nvt.rst -x md_nvt.netcdf -ref md_min5.rst" %(prmtop))
    freemd.write("pmemd.cuda -O -i md_nvt.in -o md_nvt.out -p %s -c md_min5.rst -r md_nvt.rst -x md_nvt.netcdf -ref md_min5.rst\n" %(prmtop))

    #SNPT
    print("Perform md_snpt 50000 steps...")
    print_md_inputf('md_snpt.in', 'snpt', 50000,ADDTIONAL_RST)
    os.system("srun -n 4 pmemd.MPI -O -i md_snpt.in -o md_snpt.out -p %s -c md_nvt.rst -r md_snpt.rst -x md_snpt.netcdf -ref md_nvt.rst" %(prmtop))
    freemd.write("srun -n 4 pmemd.MPI -O -i md_snpt.in -o md_snpt.out -p %s -c md_nvt.rst -r md_snpt.rst -x md_snpt.netcdf -ref md_nvt.rst\n" %(prmtop))

    #NPT
    print("Perform md_npt %d steps..." %md_npt_steps)
    print_md_inputf('md_npt.in', 'npt', md_npt_steps,ADDTIONAL_RST)
    os.system("pmemd.cuda -O -i md_npt.in -o md_npt.out -p %s -c md_snpt.rst -r md_npt.rst -x md_npt.netcdf -ref md_snpt.rst" %(prmtop))
    freemd.write("pmemd.cuda -O -i md_npt.in -o md_npt.out -p %s -c md_snpt.rst -r md_npt.rst -x md_npt.netcdf -ref md_snpt.rst\n" %(prmtop))

    #MD
    print("Perform md_md %d steps..." %md_md_steps)
    print_md_inputf('md_md.in', 'md', md_md_steps,ADDTIONAL_RST)
    os.system("pmemd.cuda -O -i md_md.in -o md_md.out -p %s -c md_npt.rst -r md_md.rst -x md_md.netcdf -ref md_npt.rst" %(prmtop))
    freemd.write("pmemd.cuda -O -i md_md.in -o md_md.out -p %s -c md_npt.rst -r md_md.rst -x md_md.netcdf -ref md_npt.rst\n" %(prmtop))

    #Cpptraj input file
    centerf = open('center.in', 'w')
    print("trajin md_md.netcdf", file=centerf)
    print("autoimage", file=centerf)
########## NNNNNNNNNNNNNNNNNNNNNNNNNNNeed to update this for different cases!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    print("trajout md_md_center.netcdf netcdf", file=centerf)
    centerf.close()
    os.system("cpptraj -p %s -i center.in > center.out" %prmtop)

    cpptrajf = open('cpptraj.in', 'w')
    print("trajin md_md_center.netcdf", file=cpptrajf)
    print("distance @%s @%s out md_md_center.txt"%(coord_atm1_num,coord_atm2_num), file=cpptrajf)
    cpptrajf.close()
    os.system("cpptraj -p %s -i cpptraj.in > cpptraj.out" %prmtop)

    #Get average
    average=cal('md_md_center')
    average=round(float(average),2)
    os.system("tail -n +2 md_md_center.txt > md_md_center_tailed.txt")

    dat=pd.read_csv('md_md_center_tailed.txt', delim_whitespace=True, header=0,engine='python')
    dat.columns = ["num", "value"]
    index = abs(dat['value'] - round(float(average),2)).idxmin()
    fram_num=dat['num'][index]

    if abs(round(float(dat['value'][index]),2) - round(float(average),2)) > 0.5:
       print ("Please double check equilibrium distance because the closes distance found in md_md_center.txt is more than 1 A away from the equilibrium distance")
    else:
       ptrajf = open('ptraj.in', 'w')
       print("trajin md_md_center.netcdf %s %s"%(fram_num,fram_num), file=ptrajf)
       print("trajout md_md_center_%s.rst"%(fram_num), file=ptrajf)
       ptrajf.close()
       os.system("cpptraj -p %s -i ptraj.in > ptraj.out" %prmtop)

       return average,fram_num
