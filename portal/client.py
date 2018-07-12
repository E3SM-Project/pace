import requests
import sys
import os
import zipfile
url = "https://pace.ornl.gov/dev1/upload"
login_url="https://pace.ornl.gov/dev1/uploadlogin"


def createOutputZip(zfname, filelist):
	zf = zipfile.ZipFile("%s.zip" % (zfname), "w", zipfile.ZIP_DEFLATED)
	for f in filelist:
		arcname = zfname + "/" + f
		print "Adding file: %s to archive: %s.zip" % (arcname, zfname)
		zf.write(f,arcname)
	zf.close()
	return

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

if (len(sys.argv)!=3):
	print('Usage: python client.py username password')
else:
	username = sys.argv[1]
	password = sys.argv[2]	
	data = {'pass':password,'name':username}
	r = requests.post(login_url, data=data)
	print(r.text)
	if r.text == 'ok':
		print('Upload option')
		print('1. files upload')
		print('2. folder upload')
		opt = input('Enter your option(1 or 2): ')
		zfname='uploadzip'
		if opt == 1:
			FileList=[]
			flag=1	
			namefile=''
			while flag==1:
				namefile=str(raw_input('Enter file: '))
				if(namefile!=''):
					FileList.append(namefile)
				else:
					flag=0;
			print (FileList)
			createOutputZip(zfname,FileList)	
		elif opt == 2:
			path= raw_input('Enter full path: ')
			zipSubdir(zfname,path)
		else:
			sys.exit("Invalid upload option, option are (1 or 2)")

		fin = open('uploadzip.zip', 'rb')	
		files = {'file': fin}
		try:
			r = requests.post(url, files=files)
			print(r.text)
		finally:
			fin.close()
