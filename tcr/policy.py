#
# Copyright 2021-2022 The Card Room
#
# MIT License:
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is furnished
# to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
File: policy.py
Author: SuperKK
"""

from collections import namedtuple

from tcr.wallet import Wallet
from tcr.project_data import ProjectData
import logging

from pycardano.crypto.bip32 import HDWallet
import pycardano

logger = logging.getLogger('policy')

PolicySettings = namedtuple('PolicySettings', ['name', 'wallet', 'seed_phrase', 'before_slot'])

class Policy:
    def __init__(self, user:ProjectData, obj:dict):
        parameters = PolicySettings(**obj)

        self.name = parameters.name
        self.wallet = Wallet(user.get_network(), user.get_wallet(parameters.wallet))
        self.seed_phrase = parameters.seed_phrase
        self.before_slot = int(parameters.before_slot)
        self.network = ProjectData.NetworkLookup[user.get_network().lower()]

        self.hdwallet_root = HDWallet.from_mnemonic(self.seed_phrase)
        policy_vkey = pycardano.PaymentExtendedVerificationKey.from_signing_key(self.get_signing_key())

        pub_key_policy = pycardano.ScriptPubkey(policy_vkey.hash())
        pub_key_wallet = pycardano.ScriptPubkey(self.wallet.get_root_verification_key().hash())

        must_before_slot = pycardano.InvalidHereAfter(self.before_slot)
        self.ttl = must_before_slot.after
        self.script = pycardano.ScriptAll([pub_key_policy, pub_key_wallet, must_before_slot])
        self.signature_key_hash = pub_key_policy.key_hash.payload.hex()

    def get_name(self):
        return self.name

    def get_wallet(self):
        return self.wallet

    def get_wallet_name(self):
        return self.wallet.get_name()

    def get_before_slot(self) -> str:
        return self.before_slot

    def get_signature_key_hash(self) -> str:
        return self.signature_key_hash

    def get_ttl(self):
        return self.ttl

    def get_script(self) -> pycardano.ScriptAll:
        return self.script

    def get_id(self) -> pycardano.ScriptHash:
        return self.script.hash()

    def get_id_str(self) -> str:
        return self.script.hash().payload.hex()

    def get_signing_key(self):
        return pycardano.PaymentExtendedSigningKey.from_hdwallet(self.hdwallet_root)

    def get_signing_keys(
        self
    ) -> list[pycardano.PaymentExtendedSigningKey]:
        return [self.get_signing_key(), self.wallet.get_root_signing_key()]

    @staticmethod
    def create_new(
        user:ProjectData,
        name:str,
        wallet:str,
        before_slot: int
    ):
        seed_phrase = HDWallet.generate_mnemonic()
        parameters = dict(PolicySettings(name=name,
                                         wallet=wallet,
                                         seed_phrase=seed_phrase,
                                         before_slot=int(before_slot))._asdict())
        return Policy(user, parameters)

    def serialize(self):
        return dict(PolicySettings(name=self.name,
                                   wallet=self.wallet.get_name(),
                                   seed_phrase=self.seed_phrase,
                                   before_slot=int(self.before_slot))._asdict())
