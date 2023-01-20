#
# Copyright 2021-2023 The Card Room
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

from blockfrost import BlockFrostApi, ApiError, ApiUrls
from collections import namedtuple
from tcr.project_data import ProjectData
from tcr.wallet import Wallet
from tcr.policy import Policy
import pycardano

Status = namedtuple('Status', ['is_healthy', 'server_time', 'height', 'slot'])

class BlockFrostNode:
    network_lookup = {
        ProjectData.Network.MAINNET: {
            'network': pycardano.Network.MAINNET,
            'url': ApiUrls.mainnet.value
        },
        ProjectData.Network.PREPROD: {
            'network': pycardano.Network.TESTNET,
            'url': ApiUrls.preprod.value
        },
        ProjectData.Network.PREVIEW: {
            'network': pycardano.Network.TESTNET,
            'url': ApiUrls.preview.value
        },
        ProjectData.Network.TESTNET: {
            'network': pycardano.Network.TESTNET,
            'url': ApiUrls.testnet.value
        }
    }

    def __init__(self, network:ProjectData.Network, api_key:str):
        self.api = BlockFrostApi(project_id=api_key,
                                 base_url=BlockFrostNode.network_lookup[network]['url'])
        self.chain_context = pycardano.BlockFrostChainContext(
            project_id=api_key,
            network=BlockFrostNode.network_lookup[network]['network'],
            base_url=BlockFrostNode.network_lookup[network]['url'],
        )


    def get_status(self) -> Status:
        try:
            health = self.api.health()
            time = self.api.clock()
            block = self.api.block_latest()

            return Status(health.is_healthy,
                          time.server_time,
                          block.height,
                          block.slot)
        except:
            return Status(False, 0, 0, 0)

    def get_address_info_ex(self, address:str):
        return self.api.address_extended(address)

    def get_utxos(self, address:str):
        return self.api.address_utxos(address)

    def resolve_ada_handle(self, ada_handle:str) -> str:
        policy_id = 'f0ff48bbb7bbe9d59a40f1ce90e9e9d0ff5002ec48f232b49ca0fb9a'
        asset_name = ada_handle.encode('ascii').hex()
        asset = policy_id + asset_name
        return self.api.asset_addresses(asset)[0].address

    def get_associated_addresses(self, stake_address:str):
        return self.api.account_addresses(stake_address)

    def get_assets(self, policy_id:str):
        """
        Get the quantity of each asset in a policy
        """
        all_assets = []
        page = 1

        while True:
            try:
                assets = self.api.assets_policy(policy_id, page = page)
                if len(assets) == 0:
                    break
                all_assets.extend(assets)
                page += 1
            except ApiError as ae:
                break

        return all_assets

    def get_asset_history(self, policy_id:str, name:str):
        asset = policy_id + name.encode('ascii').hex()
        return self.api.asset_history(asset)

    def get_asset_transactions(self, policy_id:str, name:str):
        asset = policy_id + name.encode('ascii').hex()
        return self.api.asset_transactions(asset)

    def get_transaction_metadata(self, tx_hash:str):
        return self.api.transaction_metadata(tx_hash)

    def transfer_ada(self, source:Wallet, destination:str, lovelace:int) -> str:
        builder = pycardano.TransactionBuilder(self.chain_context)
        address = source.get_delegated_payment_address(idx=Wallet.AddressIndex.ROOT)

        builder.add_input_address(address)
        builder.add_output(pycardano.TransactionOutput(
            pycardano.Address.from_primitive(destination),
            pycardano.Value.from_primitive([lovelace]))
        )

        signed_tx = builder.build_and_sign(
            [source.get_signing_key(idx=Wallet.AddressIndex.ROOT)],
            change_address=address
        )
        self.chain_context.submit_tx(signed_tx.to_cbor())

        return str(signed_tx.id)

    # todo use specific input utxo
    # automatically select output address
    def mint_nft(
        self,
        policy:Policy,
        metadata:dict,
        output_address:str
    ) -> str:
        policy_id = policy.get_id()
        multi_asset_primitive = {policy_id.payload:{}}

        for item in metadata[721][policy_id.payload.hex()]:
            multi_asset_primitive[policy_id.payload][item.encode('utf-8')] = 1

        nft = pycardano.MultiAsset.from_primitive(multi_asset_primitive)

        builder = pycardano.TransactionBuilder(self.chain_context)
        input_address = policy.get_wallet().get_delegated_payment_address(idx=Wallet.AddressIndex.ROOT)
        builder.add_input_address(input_address)
        builder.ttl = policy.get_ttl()
        builder.mint = nft
        builder.native_scripts = [policy.get_script()]
        builder.auxiliary_data = pycardano.AuxiliaryData(
            pycardano.AlonzoMetadata(
                metadata=pycardano.Metadata(metadata)
            )
        )

        min_val = pycardano.min_lovelace(
            self.chain_context,
            output=pycardano.TransactionOutput(
                address=output_address,
                amount=pycardano.Value(0, nft)
            )
        )
        builder.add_output(pycardano.TransactionOutput(
            address=output_address,
            amount=pycardano.Value(min_val, nft))
        )
        signing_keys = [policy.get_wallet().get_signing_key(idx=Wallet.AddressIndex.ROOT)]
        signing_keys.extend(policy.get_signing_keys())
        signed_tx = builder.build_and_sign(
            signing_keys,
            change_address=input_address
        )

        self.chain_context.submit_tx(signed_tx.to_cbor())

        return str(signed_tx.id)

    def mint_royalty_token(
        self,
        policy:Policy,
        royalty_address:str,
        rate:str
    ) -> str:
        policy_id = policy.get_id()
        metadata = {
            721: {
                policy_id.payload.hex(): {
                    '':{}
                }
            },
            777: {
                'rate':rate,
                'addr': royalty_address if len(royalty_address) <= 64
                        else [royalty_address[i:i+64] for i in range(0, len(royalty_address), 64)]
            }
        }

        return self.mint_nft(
            policy,
            metadata,
            policy.get_wallet().get_payment_address(idx=Wallet.AddressIndex.ROOT)
        )
