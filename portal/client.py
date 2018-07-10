import requests
import sys
url = "https://pace.ornl.gov/dev1/upload"
t=1
if (len(sys.argv)<2):
	print('Usage: python client.py filename.ext')
else:
	for i in range(len(sys.argv)-1):	
		fin = open(sys.argv[i+1], 'rb')	
		files = {'file': fin}
		try:
			r = requests.post(url, files=files)
			print(r.text)
		finally:
			fin.close()
