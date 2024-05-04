import os
import json
import string
import random
import base64

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad,unpad
from motor.motor_asyncio import AsyncIOMotorClient

class Encryption:
	def __init__(self, key, iv):
		self.key = key
		self.iv = iv

	def encrypt(self, data):
		data = pad(data.encode(),16)
		cipher = AES.new(self.key.encode('utf-8'),AES.MODE_CBC, self.iv)
		return base64.b64encode(cipher.encrypt(data))

	def decrypt(self, encrypted_data):
		encrypted_data = base64.b64decode(encrypted_data)
		cipher = AES.new(self.key.encode('utf-8'), AES.MODE_CBC, self.iv)
		return unpad(cipher.decrypt(encrypted_data), 16)

	def generate_credentials(self):
		self.key = ''.join(
			random.SystemRandom().choice(string.ascii_uppercase + string.ascii_lowercase + string.digits)
			for _ in range(16)
		)
		self.iv = ''.join(
			random.SystemRandom().choice(string.ascii_uppercase + string.ascii_lowercase + string.digits)
			for _ in range(16)
		)
		json.dump(
			{
				"key": self.key,
				"iv": self.iv
			},
			open("./resources/credentials.json", "w"),
			ensure_ascii = False,
			indent = 4
		)

class Database:
	def __init__(self):
		self.database = AsyncIOMotorClient(
			os.getenv("MONGO"),
			tls = True,
			tlsCertificateKeyFile = "mongo_cert.pem"
		)
		...