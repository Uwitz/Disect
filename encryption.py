import os
import json
import string
import random
import base64

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad,unpad
from motor.motor_asyncio import AsyncIOMotorClient

class Encryption:
	def __init__(self):
		self._ = None

	@classmethod
	def load_credentials(cls):
		if not os.path.isfile("./resources/credentials.json"):
			raise FileNotFoundError("Encryption Credentials file not found.")

		credentials: dict = json.load(open("./resources/credentials.json", "r"))
		cls.key = credentials.get("key")
		cls.iv = credentials.get("iv")

	@classmethod
	def generate_credentials(cls):
		cls.key = ''.join(
			random.SystemRandom().choice(string.ascii_uppercase + string.ascii_lowercase + string.digits)
			for _ in range(16)
		)
		cls.iv = ''.join(
			random.SystemRandom().choice(string.ascii_uppercase + string.ascii_lowercase + string.digits)
			for _ in range(16)
		)
		json.dump(
			{
				"key": cls.key,
				"iv": cls.iv
			},
			open("./resources/credentials.json", "w"),
			ensure_ascii = False,
			indent = 4
		)

	def encrypt(self, data):
		data = pad(data.encode(),16)
		cipher = AES.new(self.key.encode('utf-8'),AES.MODE_CBC, self.iv)
		return base64.b64encode(cipher.encrypt(data))

	def decrypt(self, encrypted_data):
		encrypted_data = base64.b64decode(encrypted_data)
		cipher = AES.new(self.key.encode('utf-8'), AES.MODE_CBC, self.iv)
		return unpad(cipher.decrypt(encrypted_data), 16)