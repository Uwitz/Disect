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

	@classmethod
	def load_credentials(cls):
		if not os.isfile("./resources/credentials.json"):
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


class Database:
	def __init__(self):
		self.database = AsyncIOMotorClient(
			os.getenv("MONGO"),
			tls = True,
			tlsCertificateKeyFile = "mongo_cert.pem"
		)
		self.encryption = Encryption()
		try:
			self.encyption.load_credentials()
		except FileNotFoundError:
			self.encyption.generate_credentials()

	def _recursive_encryption(self, json: dict) -> dict:
		enc_json = {}
		for key, value in json.items():
			if isinstance(value, dict):
				enc_json[self.encryption.encrypt(key)] = self._recursive_encryption(value)
			else:
				enc_json[self.encryption.encrypt(key)] = self.encryption.encrypt(value)
		return enc_json

	async def insert_one(self, collection: str, json: dict):
		enc_json = self._recursive_encryption(json)
		return await self.database["Disect"][collection].insert_one(enc_json)

	async def update_one(self, collection: str, query: dict, update: dict):
		enc_query = {
			self.encryption.encrypt(key): self.encryption.encrypt(value)
			for key, value in query
		}

		enc_update = {
			self.
		}

		return await self.database["Disect"][collection].update_one(enc_query)