import os
import csv


def writesh(name, ii, adder, multi, unroll, mode,constraint = 0):
    u=int(unroll)
    a=int(adder)
    m=int(multi)
    if constraint:
        f = open("./"+name+"/run_unconstrained.sh", mode)
        id = ii
        f.write("./main.sh "+name+" "+unroll+" op0.json "+ii+" 700"+"\n")
        f.write("echo \""+name+"\" > iic"+ii+".txt"+"\n")
        f.write("./get_results.sh "+name+" "+unroll+" "+ii+" 700 >> iic"+ii+".txt"+"\n")
    else:
        f = open("./"+name+"/run.sh", mode)
        id = str(u*(a+m))
        if ii == '1': # for ii=1 we needed to add an extra adder in some benchmarks to make sure vivado got ii=1
            f.write("./main.sh "+name+" "+unroll+" ops.json "+id+" 700 "+ii+"\n")
        else:
            f.write("./main.sh "+name+" "+unroll+" ops"+ii+".json "+id+" 700 "+ii+"\n")
        f.write("echo \""+name+"\" > ii"+ii+".txt"+"\n")
        f.write("./get_results.sh "+name+" "+unroll+" "+id+" 700 >> ii"+ii+".txt"+"\n")
    f.close()

def writejson(name, adder, multi,ii):
    f = open("./"+name+"/ops"+ii+".json", "w")
    s="{"
    if int(adder) > 0:
        s+=("\"+\": "+adder)
    if int(multi) > 0:
        if int(adder) > 0:
            s+=", "
        s+=("\"*\": "+multi)
    s+="}"
    f.write(s)
    f.close()

# cons = int(sys.argv[1])
for cons in range(0,2):
    j=0
    csv_in = open('iiunrolls.csv', 'r')
    for row in csv.reader(csv_in):
        #skip the header
        if j == 0:
            j+=1
            continue 
        bench_name=row[0]
        ii=row[1]
        adder=row[2]
        multi=row[3]
        unroll=row[4]
        if (j % 5) == 1:
            writesh(bench_name,ii,adder,multi,unroll,'w',cons)
            if cons:
                a = "./"+bench_name+"/run_unconstrained.sh"
            else:
                a = "./"+bench_name+"/run.sh"
            os.system('chmod +x ' + a)
        else:
            writesh(bench_name,ii,adder,multi,unroll,'a',cons)
        if cons == 0:
            writejson(bench_name,adder,multi,ii)
        j+=1


