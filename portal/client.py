# imports
import requests
import sys
import os
import zipfile
import getpass

# server connection
url = "https://pace.ornl.gov/dev1/upload"
login_url="https://pace.ornl.gov/dev1/uploadlogin"

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
if (len(sys.argv)!=1):
	print('Usage: python client.py')
else:
	# authentication process	
	username = str(raw_input('Enter username: '))
	password = getpass.getpass('Enter password: ')
	data = {'pass':password,'name':username}
	r = requests.post(login_url, data=data)
	print(r.text)
	# login success
	if r.text == 'ok':
		# upload interface		
		print('Upload option')
		print('1. files upload')
		print('2. folder upload')
		opt = input('Enter your option(1 or 2): ')
		zfname='uploadzip'
		# file upload case		
		if opt == 1:
			FileList=[]
			flag=1	
			namefile=''
			# enter multiple files
			while flag==1:
				namefile=str(raw_input('Enter file: '))
				# error handling files, 
				# no error, add file to list				
				if(namefile!=''):
					if(os.path.exists(namefile)):
						FileList.append(namefile)
					else:
						print("No such file: "+ namefile)
				else:
					flag=0;
			# zip it
			createOutputZip(zfname,FileList)	
		# directory upload case
		elif opt == 2:
			flag=1
			while flag==1:
				path= raw_input('Enter full path: ')
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
		else:
			# invalid option
			sys.exit("Invalid upload option, option are (1 or 2)")
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
	else:
		# user authentication failed
		print("Invalid username/password")
