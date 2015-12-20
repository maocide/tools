# Author: Mario Negri
# Description:
# Python script to monitor mysql queries and get the time to complete them
# requires installation of python-mysqldb package
# outputs a tab separated file with queries executed, time taken and rowcount
# specify logfile as argument or default position is used

import time
import subprocess
import select
import re
import sys
import MySQLdb

if len(sys.argv) > 1:
	logfile = sys.argv[1]
else:
	logfile = "/var/log/mysql/mysql.log"

if len(sys.argv) > 2:
	user = sys.argv[2]
else:
	user = ""

if len(sys.argv) > 3:
	passwd = sys.argv[3]
else:
	passwd = ""

print "Tail on " + logfile

f = subprocess.Popen(['tail','-n0','-F',logfile],\
        stdout=subprocess.PIPE,stderr=subprocess.PIPE)
p = select.poll()
p.register(f.stdout)

log = ""
print "Press ^C to stop monitoring\n"

skip = 0
startswith = ""
selectnocacheRe = re.compile(re.escape('SELECT '), re.IGNORECASE)

while True:
	try:
	    if p.poll(0.5):
	    	line = f.stdout.readline()
	    	#print line
	    	while line != "":
		    	if re.match('^.*[0-9]+\ Connect', line):
	    			startswith = "Connect"
	    			sys.stdout.write('>')
	    		if re.match('^.*[0-9]+\ Init', line):
	    			startswith = "Init"
	    			sys.stdout.write('^')
	    			startswith = "Init"
	    			log = log + "\n#SEPARATOR\n"
	    			line = "USE " + line[line.find("Init DB")+7:] + ";"
	    		if re.match('^.*[0-9]+\ Quit', line):
	    			startswith = "Quit"
	    			sys.stdout.write('<')
	    		if re.match('^.*[0-9]+\ Query', line):
	    			sys.stdout.write('.')
	    			startswith = "Query"
	    			log = log + "\n#SEPARATOR\n"
	    			line = line[line.find("Query")+5:]
	    		if(startswith == "Query" or startswith == "Init"):
					line = selectnocacheRe.sub('SELECT SQL_NO_CACHE ', line)
					log = log + line
		        line = f.stdout.readline()

	        	
	    time.sleep(0.5)
	except KeyboardInterrupt:
		break

f.kill()

print "\n"
print "Data collected:"
#print log

queries = re.split('\n#SEPARATOR\n', log)

print "\n"

for index in range(len(queries)):
	queries[index] = " ".join(queries[index].split("\n"))
	queries[index] = " ".join(queries[index].split("\t"))
	queries[index] = queries[index].strip()
	print queries[index]

db = MySQLdb.connect(host="localhost",
                     user=user,
                     passwd=passwd)

db.autocommit(False) # We won't make any change to the database

cursor = db.cursor()

filename = "querytime.txt";
out_file = open(filename,"w")

total_time = 0.0

for index in range(len(queries)):
	if queries[index]:
		start_time = time.time()
		cursor.execute(queries[index])
		exec_time = time.time() - start_time
		total_time += exec_time
		out_file.write("{:s}\t{:8.7f}\t{:d}\n".format(queries[index], exec_time, cursor.rowcount))
		print queries[index] + "\n" + str(exec_time) + " seconds\n" + str(cursor.rowcount) + " rows\n"


out_file.close()
db.rollback()

print "Total time taken to execute all the queries: {:8.7f} Seconds.".format(total_time)
print "Wrote " + filename