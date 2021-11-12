import os


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
    #print (dir_list)
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
