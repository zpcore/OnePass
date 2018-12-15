#!/usr/bin/python

import string, sys
from random import *

characters = string.ascii_letters + string.punctuation  + string.digits
low_bound, up_bound = 8, 16
if(len(sys.argv)==1):
	pass
elif(len(sys.argv)==2):
	low_bound, up_bound = int(sys.argv[1]), int(sys.argv[1])+8 
elif(len(sys.argv)==3):
	low_bound, up_bound = int(sys.argv[1]), int(sys.argv[2])
	if(up_bound<low_bound):
		print('Upper bound should be greater than lower bound.')
else:
	print('Incorrect format.') 

password =  "".join(choice(characters) for x in range(randint(low_bound, up_bound)))

print(password)