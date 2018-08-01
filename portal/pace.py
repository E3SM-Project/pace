# imports
import argparse
import requests
import sys
import os
import zipfile
import getpass

# server connection
url = "https://pace.ornl.gov/dev1/upload"
login_url="https://pace.ornl.gov/dev1/uploadlogin"

def parseArguments(): 
	parser = argparse.ArgumentParser(description="PACE upload tool.")
	parser.add_argument('-ed', action='store', dest='source', help="Experiment directory Name", required=True)
	#parser.add_argument('--perf-archive', '-pa',help="perf archive name", required=True)
	args = parser.parse_args()
	# print args
	return args

# zips all files in the list
def createOutputZip(zfname, filelist):
	zf = zipfile.ZipFile("%s.zip" % (zfname), "w", zipfile.ZIP_DEFLATED)
	for f in filelist:
		arcname = zfname + "/" + f
		print "Adding file: %s to archive: %s.zip" % (arcname, zfname)
		zf.write(f,arcname)
	zf.close()
	return

# zips given directory path
def zipSubdir(zfname, path):
	zf = zipfile.ZipFile("%s.zip" % (zfname), "w", zipfile.ZIP_DEFLATED)
	abs_src = os.path.abspath(path)
	for root,dirs,files in os.walk(path):
		for file in files:
			absname = os.path.abspath(os.path.join(root, file))
			arcname = zfname + "/" + absname[len(abs_src) + 1:]
			print "Adding file: %s to archive: %s.zip" % (arcname, zfname)
			zf.write(absname,arcname)
	zf.close()
	return

# main
result=parseArguments()

zfname='uploadzip'
# file upload case		

FileList=[]
flag=1	
namefile=''

# directory upload case
flag=1
while flag==1:
	path = result.source	
	#path= raw_input('Enter full path: ')
	# error handling directory				
	if(path!=''):
		if (os.path.isdir(path)):
			# zip it
			zipSubdir(zfname,path)
			flag=0
		else:
			print("No such directory: "+ path)
	else:
		flag=0

# error handle empty zip file
if(os.path.exists('uploadzip.zip')):
	if(os.stat('uploadzip.zip').st_size!=0):
		# open zip to be uploaded
		fin = open('uploadzip.zip', 'rb')			
		files = {'file': fin}
		try:
			# request for connection to server
			r = requests.post(url, files=files)
			print(r.text)
		finally:
			fin.close()
	else:
		print('Nothing to upload, Empty zip folder')
else:
	print('Nothing to upload, Exiting ...')

