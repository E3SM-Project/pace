import requests
import sys
import os
import zipfile
url = "https://pace.ornl.gov/dev1/upload"
t=1

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

print(len(sys.argv))
if (len(sys.argv)<3):
	print('Usage: python client.py "OPTION" "Files/Dir"')
	print('OPTION = 1, for file uploads')
	print('OPTION = 2, for directory uploads')
else:
	zfname='uploadzip'
	opt = sys.argv[1]
	if opt == '1':	
		FileList = sys.argv[2: ]
		print (FileList)
		createOutputZip(zfname,FileList)	
	elif opt == '2':
		path=sys.argv[2]
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
