from __future__ import print_function
import os
import pandas as pd

os.system("cat md_us.log md2_us2.log > md_usc.log")
os.system("awk '{ print NR FS $2 }' md_usc.log > md_usf.log")
path = os.getcwd() +'/'
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
lower_b = mean - CENTER_DEVIATION*std
upper_b = mean + CENTER_DEVIATION*std
RST=open("us_dis.RST","r")
for line in RST:
  if "rk3" in line:
    a,b=line.split(",igr1=")
    #a,b=line.split(",/")
    c,d=a.split("rk3=")
    us_window_restraint=int(float(d))
RST.close()
log=open("info2.log","a")
print('window: WINDOW;  restraint: %s;  center_deviation: CENTER_DEVIATION; lower bound: %s;  upper bound: %s'%(us_window_restraint, lower_b, upper_b),file=log)
if lower_b < round(float(WINDOW),2) and round(float(WINDOW),2) < upper_b:
   if "adapt2.RST" not in os.listdir('.'):
     pass
   else:
     RST2=open("adapt2.RST","r")
     for line in RST2:
       if "rk3" in line:
         aa,bb=line.split(",igr1=")
         #a,b=line.split(",/")
         cc,dd=aa.split("rk3=")
         rst2=int(float(dd))
     RST2.close()
     if us_window_restraint != rst2:
       #print ('Inconsistent restraints between us_dis.RST and adapt.RST, re-running python adaptive.py')
       print('Inconsistent restraints between us_dis.RST and adapt2.RST, re-running python adaptive2.py',file=log)
       os.system("sed -i 's/%s/%s/g' us_dis.RST"%(us_window_restraint,rst2))
       os.system("python adaptive2.py")
     else:
       ###print ('good;', lower_b, WINDOW, upper_b)
       print('good; %s WINDOW %s'%(lower_b,upper_b),file=log)
       slm = open("command",'w')
       slm.write("pmemd.cuda -O -i us_npt.in -o us_npt.out -p PRMTOP -c start.rst -r us_npt.rst -x us_npt.netcdf -ref start.rst\n")
       slm.write("pmemd.cuda -O -i us_md.in -o us_md.out -p PRMTOP -c us_npt.rst -r us_md.rst -x us_md.netcdf -ref us_npt.rst\n")
       slm.write("pmemd.cuda -O -i us_md2.in -o us_md2.out -p PRMTOP -c us_md.rst -r us_md2.rst -x us_md2.netcdf -ref us_md.rst\n")
       slm.write("if grep 'Total wall time' us_md2.out;then\n")
       slm.write("   echo 'all done'\n")
       slm.write("else\n")
       slm.write("   sbatch %s-all.slm\n"%(WINDOW))
       slm.write("fi\n")
       slm.close()
       os.system("cat adapt_header.slm command > %s-all.slm"%(WINDOW))
       os.system("sbatch %s-all.slm"%(WINDOW))
else:
   us_window_restraint_new = int(us_window_restraint) + int(INCREMENT)
   os.system("cp SLM_HEADER adapt_header.slm")
   os.system("cp us_md2.in adapt_md2.in")
   os.system("cp us_dis.RST adapt2.RST")
   os.system("sed -i 's/3:30:00/1:00:00/g' adapt_header.slm")
   os.system("sed -i 's/nstlim=US_MD_STEPS,/nstlim=TEST_US_MD_STEPS,/g' adapt_md2.in")
   os.system("sed -i 's/us_md.RST/adapt2.RST/g' adapt_md2.in")
   os.system("sed -i 's/rk2=%s.0, rk3=%s.0,/rk2=%s.0, rk3=%s.0,/g' adapt2.RST"%(us_window_restraint,us_window_restraint,us_window_restraint_new,us_window_restraint_new))
   os.system("sed -i 's/rk2=%s.0, rk3=%s.0,/rk2=%s.0, rk3=%s.0,/g' us_dis.RST"%(us_window_restraint,us_window_restraint,us_window_restraint_new,us_window_restraint_new))
   slm = open("command",'w')
   slm.write("pmemd.cuda -O -i adapt_md2.in -o adapt_md2.out -p PRMTOP -c us_md.rst -r adapt_md2.rst -x adapt_md2.netcdf -ref us_md.rst\n")
   slm.write("if grep 'Total wall time' adapt_md2.out;then\n")
   slm.write("   echo 'all done'\n")
   slm.write("   source ~/.bashrc\n")
   slm.write("   python adaptive2.py\n")
   slm.write("else\n")
   slm.write("   sbatch adapt2.slm\n")
   slm.write("fi\n")
   slm.close()
   os.system("cat adapt_header.slm command > adapt2.slm")
   os.system("sed -i 's/XXXXXXXXX/%s_%s/g' adapt2.slm"%(WINDOW,us_window_restraint_new))
   print ('window: WINDOW;  restraint: %s;  center_deviation: CENTER_DEVIATION; lower bound: %s;  upper bound: %s'%(us_window_restraint, lower_b, upper_b))
   os.system("sbatch adapt2.slm")
log.close()
