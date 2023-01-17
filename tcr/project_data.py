
from cryptography.fernet import Fernet
import base64
import json
from enum import StrEnum

class ProjectData:
    class Network(StrEnum):
        NONE = ''
        MAINNET = 'mainnet'
        PREPROD = 'preprod'
        PREVIEW = 'preview'
        TESTNET = 'testnet'

    class Constants(StrEnum):
        NAME = 'name'
        WALLETS = 'wallets'
        POLICIES = 'policies'
        NETWORK = 'network'

    def __init__(self, file:str, key:str):
        self.data = {}
        self.file = file

        tempkey = bytearray(base64.b64encode(key.encode('ascii'))[0:43])
        tempkey.append(61)
        self.key = bytes(tempkey)
        self.encryptor = Fernet(self.key)

        try:
            with open(self.file, 'rb') as cipherfile:
                ciphertext = cipherfile.read()
                plaintext = self.encryptor.decrypt(ciphertext)
                self.data = json.loads(plaintext)
        except FileNotFoundError as fnfe:
            self.data = {ProjectData.Constants.NETWORK: ProjectData.Network.NONE,
                         ProjectData.Constants.WALLETS: [],
                         ProjectData.Constants.POLICIES: []}

        print(json.dumps(self.data, indent=4))

    def save(self):
        plaintext = json.dumps(self.data)
        ciphertext = self.encryptor.encrypt(plaintext.encode('ascii'))
        with open(self.file, 'wb') as cipherfile:
            cipherfile.write(ciphertext)

    def get_network(self) -> Network:
        if not ProjectData.Constants.NETWORK in self.data:
            self.data[ProjectData.Constants.NETWORK] = ProjectData.Network.NONE

        return ProjectData.Network(self.data[ProjectData.Constants.NETWORK])

    def set_network(self, network:Network):
        self.data[ProjectData.Constants.NETWORK] = network

    def get_wallet(self, name:str) -> dict:
        if not ProjectData.Constants.WALLETS in self.data:
            self.data[ProjectData.Constants.WALLETS] = []

        for wallet in self.data[ProjectData.Constants.WALLETS]:
            if wallet['name'] == name:
                return wallet

        return None

    def get_wallets(self) -> dict:
        if not ProjectData.Constants.WALLETS in self.data:
            self.data[ProjectData.Constants.WALLETS] = []

        return self.data[ProjectData.Constants.WALLETS]

    def add_wallet(self, obj):
        self.data[ProjectData.Constants.WALLETS].append(obj)

    def delete_wallet(self, name):
        for w in self.data[ProjectData.Constants.WALLETS]:
            if w[ProjectData.Constants.NAME] == name:
                self.data[ProjectData.Constants.WALLETS].remove(w)
                break

    def get_policies(self):
        if not ProjectData.Constants.POLICIES in self.data:
            self.data[ProjectData.Constants.POLICIES] = []

        return self.data[ProjectData.Constants.POLICIES]

    def add_policy(self, obj):
        self.data[ProjectData.Constants.POLICIES].append(obj)

    def delete_policy(self, name):
        for p in self.data[ProjectData.Constants.POLICIES]:
            if p[ProjectData.Constants.NAME] == name:
                self.data[ProjectData.Constants.POLICIES].remove(p)
                break
