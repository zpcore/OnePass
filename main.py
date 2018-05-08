import base64,json,sys,getpass
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto import Random
from enum import Enum
from data_input import Token,MyEncoder
from collections import namedtuple

secret = 'secret.dat' # set your password file name

def encrypt(key, source, encode=False):
	key = SHA256.new(key).digest()  # use SHA-256 over our key to get a proper-sized AES key
	IV = Random.new().read(AES.block_size)  # generate IV
	encryptor = AES.new(key, AES.MODE_CBC, IV)
	padding = AES.block_size - len(source) % AES.block_size  # calculate needed padding
	source += bytes([padding]) * padding  # Python 2.x: source += chr(padding) * padding
	data = IV + encryptor.encrypt(source)  # store the IV at the beginning and encrypt
	return base64.b64encode(data).decode("latin-1") if encode else data

def decrypt(key, source, decode=False):
	if decode:
		source = base64.b64decode(source.encode("latin-1"))
	key = SHA256.new(key).digest()  # use SHA-256 over our key to get a proper-sized AES key
	IV = source[:AES.block_size]  # extract the IV from the beginning
	decryptor = AES.new(key, AES.MODE_CBC, IV)
	data = decryptor.decrypt(source[AES.block_size:])  # decrypt
	padding = data[-1]  # pick the padding value from the end; Python 2.x: ord(data[-1])
	if data[-padding:] != bytes([padding]) * padding:  # Python 2.x: chr(padding) * padding
		#raise ValueError("Invalid padding...")
		print('Error: OnePass password incorrect!')
		sys.exit()
	return data[:-padding]  # remove the padding

class State(Enum):
	INPUT_PASS = 1
	WRITE_OR_READ = 2
	WRITE = 3
	READ = 4
	ONEPASS_PASSWORD = 5
	REGISTERED_PASSWORD = 6
	REMOVE = 7

def encodeJsonList2file(password_bytes, decodedJson, file):
	data = json.dumps(decodedJson, ensure_ascii=False)# convert json to str
	new_secret = encrypt(password_bytes,data.encode())
	with open(file, 'wb') as f:
		f.write(new_secret);

def decodeFile2Json(password_bytes, file):
	with open(file, 'rb') as f:
		data = f.read()
		tmp = decrypt(password_bytes,data)
		decodedJson = json.loads(tmp.decode('utf-8'))
	return decodedJson

def main():
	state = State.INPUT_PASS
	while(True):
		if(state == State.INPUT_PASS):
			mainPass = getpass.getpass('Input your OnePass password:').encode()
			# print(mainPass)
			try:
				f = open(secret, 'rb')
				decodeFile2Json(mainPass,secret) # test the password
				f.close()
			except IOError:
				print('OnePass file not exist. Building a new secret file...')
				verifyPass = getpass.getpass('Reverify OnePass password:')
				if(mainPass.decode()==verifyPass):
					print('Password established!')
				else:
					print('Password does not match. Restart...\n')
					state = State.INPUT_PASS
					continue
				f = open(secret, 'wb')
				f.write(encrypt(mainPass,b'{"keypair":[]}'))
				f.close()
			state = State.WRITE_OR_READ

		elif(state == State.WRITE_OR_READ):
			choice = input('Choose action number: \n'+
				'Register (1)\n'+
				'Read (2)\n'+
				'Update OnePass Password (3)\n'+
				'Update Assocaition Password (4)\n'+
				'Remove Assocaition (5)\n'
				).strip()
			if(choice == '1'):
				state = State.WRITE
			elif(choice == '2'):
				state = State.READ
			elif(choice == '3'):
				state = State.ONEPASS_PASSWORD
			elif(choice == '4'):
				state = State.REGISTERED_PASSWORD
			elif(choice == '5'):
				state = State.REMOVE
			else:
				print('Incorrect choice, try again.')
		elif(state == State.WRITE):
			print('--------Reg--------')
			tok = Token()
			tok.get_input()
			token = json.dumps(tok, cls=MyEncoder)
			# print(token)
			data = decodeFile2Json(mainPass,secret)
			# print(data)
			data["keypair"].append(json.loads(bytes(token,'utf-8').decode("utf-8")))
			encodeJsonList2file(mainPass,data,secret)

			print('Register succeed!')
			print('-------------------')
			sys.exit()
		elif(state == State.ONEPASS_PASSWORD):
			new_mainPass = getpass.getpass('Input your new OnePass password:')
			verify_new_mainPass = getpass.getpass('Input your new OnePass password again:')
			if(new_mainPass==verify_new_mainPass):
				data = decodeFile2Json(mainPass, secret)
				encodeJsonList2file(new_mainPass.encode(), data, secret)
				print('New OnePass password set!')
				sys.exit()
			else:
				print('Password not match, try again.')

		elif(state == State.REGISTERED_PASSWORD):
			found = False
			data = decodeFile2Json(mainPass,secret)
			# company = [name['company'] for name in data['keypair']]
			choice = input('Which association\'s password you want to change?	').replace(" ", "").lower()

			for item in data['keypair']:
				if(choice==item['company'].replace(" ", "").lower()):
					found = True
					print('----------RESULT-----------\n'+
						'company:'+item['company']+'\n'+'old password:'+item['password']+'\n'+
						'---------------------------')
					choice = input('Type new password:')
					item['password'] = choice
					encodeJsonList2file(mainPass,data,secret)
					print('Finish setting new password for '+item['company']+'.')
			if found:
				sys.exit()
			print('Assocaition not found.')

		elif(state == State.REMOVE):
			found = False
			data = decodeFile2Json(mainPass,secret)
			# company = [name['company'] for name in data['keypair']]
			choice = input('Which association\'s you want to remove?	')

			for item in data['keypair']:
				if(choice==item['company']):
					found = True
					print('----------RESULT-----------\n'+
						'company:'+item['company']+'\n'+'old password:'+item['password']+'\n'+
						'---------------------------')
					data['keypair'].remove(item)
					encodeJsonList2file(mainPass,data,secret)
					print('Removed Association '+item['company']+'.')
			if found:
				sys.exit()
			print('Assocaition not found.')

		elif(state == State.READ):
			found = False
			with open(secret, 'rb') as f:
				data=f.read()
				tmp = decrypt(mainPass,data)
				data = json.loads(tmp.decode('utf-8'))
				company = [name['company'] for name in data['keypair']]
				choice = input('Assocaition Name:	').replace(" ", "").lower()
				if(choice == '_all'):
					print(company)
				else:
					for item in data['keypair']:
						if(choice==item['company'].replace(" ", "").lower()):
							found = True
							print('----------RESULT-----------\n'+
								'company:'+item['company']+'\n'+
								'password:'+item['password']+'\n'+
								'email:'+item['email']+'\n'
								'---------------------------')
					if not found:
						print('Assocaition not found.')


if __name__ == '__main__':
	main()