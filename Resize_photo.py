import cv2
import numpy
from os import listdir
from os.path import isfile, join
mypath='Singer/'
onlyfiles = [ f for f in listdir(mypath) if isfile(join(mypath,f)) ]
for n in range(0, len(onlyfiles)):
	image=cv2.imread(join(mypath,onlyfiles[n]))    
	face = cv2.resize(image,(300,300),interpolation=cv2.INTER_AREA)
	file_name_path = 'music_web/Singer/'+onlyfiles[n][:-4]+onlyfiles[n][-4:]
	cv2.imwrite(file_name_path,face)
	print(n)
print('Colleting Samples Complete!!!')