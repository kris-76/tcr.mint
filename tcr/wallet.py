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
File: wallet.py
Author: SuperKK
"""

from typing import Tuple
import os
import logging
from enum import Enum
from enum import IntEnum
import pycardano

from pycardano.crypto.bip32 import HDWallet
from pycardano import PaymentVerificationKey

from collections import namedtuple
from tcr.command import Command

logger = logging.getLogger('wallet')

WalletSettings = namedtuple('Wallet', ['name', 'seed_phrase'])


class Wallet:
    """
    The Wallet class is used to create a new wallet and all operations
    associated with creating wallets.

    Commands based on https://github.com/input-output-hk/cardano-addresses
    """

    network_lookup = {
        'mainnet': pycardano.Network.MAINNET,
        'preprod': pycardano.Network.TESTNET,
        'preview': pycardano.Network.TESTNET,
        'testnet': pycardano.Network.TESTNET
    }

    class AddressIndex(IntEnum):
        ROOT = 0
        MINT = 1
        PRESALE = 2
        MUTATE_REQUEST = 3

    def __init__(self, network: str, obj:dict):
        parameters = WalletSettings(**obj)
        self.name = parameters.name
        self.seed_phrase = parameters.seed_phrase
        self.network = Wallet.network_lookup[network.lower()]

        self.hdwallet = HDWallet.from_mnemonic(self.seed_phrase)
        self.hdwallet_stake = self.hdwallet.derive_from_path("m/1852'/1815'/0'/2/0")

        self.hdwallet_payment = []
        for idx in range(0, 4):
            self.hdwallet_payment.append(self.hdwallet.derive_from_path(f"m/1852'/1815'/0'/0/{idx}"))
            print(f'{self.name}[{idx}] = {self.get_delegated_payment_address(idx).encode()}')

    @staticmethod
    def create_new( name:str, network:str):
        seed_phrase = HDWallet.generate_mnemonic()
        return Wallet(network,
                      dict(WalletSettings(name=name,
                                          seed_phrase=seed_phrase)._asdict()))

    def serialize(self):
        return dict(WalletSettings(name=self.name,
                                   seed_phrase=self.seed_phrase)._asdict())

    def get_name(self) -> str:
        """
        Return the name of the wallet.
        """

        return self.name

    def get_signing_key(self,
                        idx:AddressIndex=AddressIndex.MINT) -> pycardano.PaymentExtendedSigningKey:
        return pycardano.PaymentExtendedSigningKey.from_hdwallet(self.hdwallet_payment[idx])

    def get_stake_signing_key(self):
        return pycardano.PaymentExtendedSigningKey.from_hdwallet(self.hdwallet_stake)

    def get_stake_address(self) -> pycardano.Address:
        """
        @return pycardano.Address.  Call .encode() to convert to a string
        """
        stake_signing_key = self.get_stake_signing_key()
        stake_vk = pycardano.PaymentExtendedVerificationKey.from_signing_key(stake_signing_key)

        addr = pycardano.Address(payment_part=None,
                                 staking_part=stake_vk.hash(),
                                 network=self.network)
        return addr

    def get_payment_address(self,
                            idx:AddressIndex=AddressIndex.MINT) -> pycardano.Address:
        """
        Get the payment address for the specified index.

        @param idx Index for the address to get.

        @return pycardano.Address.  Call .encode() to convert to a string
        """

        signing_key = self.get_signing_key(idx)
        spend_vk = pycardano.PaymentExtendedVerificationKey.from_signing_key(signing_key)

        addr = pycardano.Address(payment_part=spend_vk.hash(),
                                 staking_part=None,
                                 network=self.network)
        return addr

    def get_delegated_payment_address(self,
                                      idx:AddressIndex=AddressIndex.MINT) -> pycardano.Address:
        """
        Get the delegated payment address for the specified index.

        @param idx Index for the address to get.

        @return pycardano.Address.  Call .encode() to convert to a string
        """

        signing_key = self.get_signing_key(idx)
        spend_vk = pycardano.PaymentExtendedVerificationKey.from_signing_key(signing_key)

        stake_signing_key = self.get_stake_signing_key()
        stake_vk = pycardano.PaymentExtendedVerificationKey.from_signing_key(stake_signing_key)

        addr = pycardano.Address(payment_part=spend_vk.hash(),
                                 staking_part=stake_vk.hash(),
                                 network=self.network)
        return addr
