import json
import string, sys
from random import *

class Token:
	def __init__(self):
		self.company, self.website, self.email, self.username, self.password = None, None, None, None, None

	def get_input(self):
		while(self.company in (None,'')):
			self.company = input('Account Association:')
			if(self.company in (None,'')):
				print('Account Association cannot be null, try again.')

		self.website = input('Website linked to the account:')

		self.email = input('Email linked to the account:')

		# while(self.email in (None,'')):
		# 	self.email = input('Registered Email:')
		# 	if(self.email in (None,'')):
		# 		print('Email cannot be null, try again.')

		while(self.username in (None,'')):
			self.username = input('Username:')
			if(self.username in (None,'')):
				print('Username cannot be null, try again.')

		while(self.password in (None,'')):
			select = input('Random generate a password for you? Type Y or N.	').strip().lower()
			if(select in ('y','yes')):
				characters = string.ascii_letters + string.punctuation  + string.digits
				low_bound, up_bound = 10, 20
				password =   "".join(choice(characters) for x in range(randint(low_bound, up_bound)))
				self.password = password
				print('auto generated password:'+self.password)
			elif(select in ('n','no')):
				self.password = input('Password:')
				if(self.password in (None,'')):
					print('Password cannot be null, try again.')
			else:
				print('Incorrect choice. Try again.')

class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if not isinstance(obj, Token):
            return super().default(obj)

        return obj.__dict__

# tok = Token()
# tok.get_input()
# print(json.dumps(tok, cls=MyEncoder))